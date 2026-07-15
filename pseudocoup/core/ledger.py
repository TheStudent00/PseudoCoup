import json
import os
from typing import Dict, List, Optional

class Ledger:
    """
    High-Resolution Ledger schema structure.
    Capable of parsing and dumping JSON.
    Tracks types and wrappers.
    """
    def __init__(self):
        self.types: Dict[str, str] = {}
        self.wrappers: List[str] = []
        self.memory_erasure: Dict[str, str] = {}
        self.file_map: Dict[str, str] = {}
        # ambiguous_import cluster fix: `file_map` is last-writer-wins, so it
        # only records ONE owning output file per global symbol name. But some
        # symbol names are legitimately DECLARED in two different Kotlin source
        # files (e.g. the `displayName()` extension emitted as a top-level Dart
        # function in MovementPattern.kt AND BodyRegion.kt/MuscleGroup; the
        # `ProgramStructure` type in data/model AND engine; `ConfidenceTier` in
        # two files; `Success` in two). When a downstream file imports BOTH
        # owning libraries, Dart raises `ambiguous_import`. To emit a `hide` on
        # the non-canonical import we need EVERY owning file per name, not just
        # the last. `symbol_owners` records the full set; `file_map` still holds
        # the single canonical owner (last-writer, matching prior behavior), so
        # the hide targets are `symbol_owners[name] - {file_map[name]}`.
        self.symbol_owners: Dict[str, set] = {}
        # Unit 09.9: parallel structure for constructor/function parameter
        # shapes, keyed in the SAME key space as `file_map` (bare symbol
        # name — a data class name, a regular class name, or a top-level
        # function/composable name). NOTE: because this is bare-name keyed,
        # Kotlin function overloads (same name, different params, in
        # different files/scopes) will collide — last registration wins.
        # See the overload-collision grep in the Stage 2 report for the
        # concrete list found in this codebase.
        #
        # Value: ordered list of tuples, one per declared parameter, in
        # declaration order:
        #   (param_name: str, has_default: bool, is_trailing_lambda: bool)
        self.param_shapes: Dict[str, List[tuple]] = {}
        # Cluster-5 sweep-3-escalation-2 durable fix: a SECOND, scope-qualified
        # index alongside `param_shapes`, keyed `f"{file_scope}.{name}"` where
        # `file_scope` is the declaring Kotlin file's output name (the same
        # identity threaded into ingest as `file_scope` — see
        # `KotlinIngestor.ingest`/`parse`). This disambiguates same-named
        # composables/classes declared in DIFFERENT files (SelectionCard x2,
        # SectionHeader x2, DetailSection x3 — see sweep-3 report escalation 2)
        # WITHOUT removing the bare-name map: `param_shapes` is still populated
        # (last-writer-wins, current behavior) as a fallback for lookups that
        # cannot know the callee's defining scope (a call site referencing a
        # composable declared in another file). The declaration-site emission
        # (visit_FunctionDefNode, which is always emitting the very declaration
        # it wants the shape for) CAN always form the qualified key and prefers
        # it. See `register_param_shape`/`get_param_shape` below.
        self.param_shapes_scoped: Dict[str, List[tuple]] = {}
        # Names of Kotlin `object` declarations that are lowered to a STATEFUL
        # Dart singleton (`class Foo { Foo._(); static final Foo instance; <inst
        # members> }`). Their members are emitted as INSTANCE members, so a
        # source call site `Foo.member()` must be rewritten to
        # `Foo.instance.member()` (otherwise static_access_to_instance_member).
        # Registered structurally at ingest (keyed on the object being a
        # stateful singleton, never per-name). Stateless objects are NOT listed
        # here — their members are `static`, so `Foo.member` already resolves.
        self.singleton_objects: List[str] = []
        # Names of Kotlin `enum class` declarations. Populated in a Phase-1
        # pre-pass (tools/transpile_wfl.py) so ALL enum names are known before
        # ANY module emits — needed because enums emit AFTER their call sites,
        # so a self-registering-on-emit set would be order-dependent. Consumed
        # by the egress `EnumType.valueOf(s)` -> `EnumType.values.byName(s)`
        # rewrite (Dart enums have no `valueOf`).
        self.enum_names: set = set()
        # Phase 3 sweep 5 (method-return foundation): a map from a method's
        # DECLARING TYPE + method name to its raw Kotlin return-type string
        # (e.g. `Flow<ProgramEntity?>`, `ProgramEntity?`, `List<X>`, or
        # `'void'` for a Kotlin function with no declared return type/Unit).
        # Keyed `f"{declaring_type}.{method_name}"` — NOT bare method name —
        # because method names collide across unrelated classes/interfaces
        # (e.g. every DAO declares `insert`/`getAll`); a bare-name map would
        # let one DAO's shape silently answer for another's, corrupting the
        # resolved return type at a call site whose receiver is a different
        # declaring type. `declaring_type` is the SAME name the ingestor
        # already threads as `scope`/`new_scope` at a class/interface body
        # (see KotlinIngestor._map_node's `class_declaration` branch and
        # `_absorb_body_members`, which passes that class/interface name down
        # as the `scope` argument into every method's `function_declaration`
        # branch) — so registration reuses that identity rather than
        # inventing a new one. Top-level (non-method) functions have no
        # declaring type and are never registered here; their return type
        # already lives on `func_node.metadata['type']` at the declaration
        # site, which is the existing, sufficient path for that case.
        self.method_returns: Dict[str, str] = {}
        # Parallel to `method_returns`, same key scheme: whether the method
        # is Kotlin `suspend` (needed because a suspend method's Dart return
        # type is wrapped in `Future<...>` and its call sites need `await`,
        # neither of which is visible from the raw return-type string alone).
        self.method_suspend: Dict[str, bool] = {}
        # Phase 3 sweep 7 (sync->async lowering): the set of methods
        # (`f"{declaring_type}.{method_name}"`, SAME key scheme as
        # `method_returns`/`method_suspend`) that the egress has determined must
        # be emitted as Dart `async`/`Future<R>` even though they are NOT Kotlin
        # `suspend`. A method lands here when its OWN body contains a
        # resolved-async call (a call to a `suspend`/already-async_required
        # method), computed by the egress's per-module async pre-pass
        # (`DartEmitter._compute_async_required`) to an intra-module fixpoint.
        # Consumed by the egress await-decision (`_is_receiver_method_suspend`
        # and the bare-`this` call branch) so a caller of such a method awaits
        # it exactly as it would a real `suspend fun`. NOT populated at ingest
        # (the ledger records no call edges — see the sweep-7 report); it is a
        # pure egress-derived overlay, so it is deliberately NOT serialized in
        # dump()/load() (it would be stale on reload and is always recomputed).
        self.async_required: set = set()

    def register_method_return(self, declaring_type: str, method_name: str, ret_str: str, is_suspend: bool = False) -> None:
        """Records the raw Kotlin return-type string for `declaring_type.method_name`
        (e.g. `register_method_return('ProgramDao', 'getEnrolled', 'Flow<ProgramEntity?>')`).
        `ret_str` should be `'void'` (or `'Unit'`) when the Kotlin method has no
        declared return type. `is_suspend` records whether the Kotlin method was
        declared `suspend fun`. Last registration wins for a given key (methods
        are declared once per declaring type in valid Kotlin, so collision here
        would indicate a real duplicate declaration, not an expected overload
        pattern like `param_shapes`)."""
        if not declaring_type or not method_name:
            return
        key = f"{declaring_type}.{method_name}"
        self.method_returns[key] = ret_str
        self.method_suspend[key] = is_suspend

    def get_method_return(self, declaring_type: str, method_name: str) -> Optional[str]:
        """Retrieves the raw Kotlin return-type string registered for
        `declaring_type.method_name`, or None if never registered (e.g. the
        declaring type was never ingested, or the name is a builtin/library
        method with no Kotlin declaration in this codebase). Callers must
        treat None as 'unresolvable' and never guess a type."""
        if not declaring_type or not method_name:
            return None
        return self.method_returns.get(f"{declaring_type}.{method_name}")

    def is_method_suspend(self, declaring_type: str, method_name: str) -> bool:
        """True if `declaring_type.method_name` was registered as Kotlin
        `suspend fun`. False (not None) when unregistered, since callers use
        this as a boolean gate (e.g. 'wrap in Future<>?') and an unresolved
        method should default to the non-suspend rendering rather than force
        a null-check at every call site."""
        if not declaring_type or not method_name:
            return False
        return self.method_suspend.get(f"{declaring_type}.{method_name}", False)

    def register_async_required(self, declaring_type: str, method_name: str) -> None:
        """Mark `declaring_type.method_name` as requiring Dart `async`/`Future<R>`
        emission (Phase 3 sweep 7). Idempotent; ignores empty keys. Set by the
        egress's per-module async pre-pass, never at ingest."""
        if declaring_type and method_name:
            self.async_required.add(f"{declaring_type}.{method_name}")

    def is_async_required(self, declaring_type: str, method_name: str) -> bool:
        """True if `declaring_type.method_name` was marked async_required by the
        egress pre-pass. False (not None) when unmarked, since callers use it as
        a boolean await/async gate exactly like `is_method_suspend`."""
        if not declaring_type or not method_name:
            return False
        return f"{declaring_type}.{method_name}" in self.async_required

    def register_enum(self, name: str) -> None:
        """Record `name` as a Kotlin enum type (Phase-1 pre-pass)."""
        if name:
            self.enum_names.add(name)

    def is_enum(self, name: str) -> bool:
        """True if `name` is a known Kotlin enum type."""
        return name in self.enum_names

    def dump(self, filepath: str) -> None:
        """Exports to a JSON file (e.g. .ledger.json)."""
        data = {
            "types": self.types,
            "wrappers": self.wrappers,
            "memory_erasure": self.memory_erasure,
            "file_map": self.file_map,
            # Sets are serialized as JSON arrays; restored as sets in load().
            "symbol_owners": {k: sorted(v) for k, v in self.symbol_owners.items()},
            # Tuples are serialized as JSON arrays; restored as tuples in load().
            "param_shapes": {k: [list(t) for t in v] for k, v in self.param_shapes.items()},
            "param_shapes_scoped": {k: [list(t) for t in v] for k, v in self.param_shapes_scoped.items()},
            "singleton_objects": self.singleton_objects,
            "method_returns": self.method_returns,
            "method_suspend": self.method_suspend,
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
    def load(self, filepath: str) -> None:
        """Populates the class from a JSON file (e.g. .ledger.json)."""
        if not os.path.exists(filepath):
            return
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.types = data.get("types", {})
            self.wrappers = data.get("wrappers", [])
            self.memory_erasure = data.get("memory_erasure", {})
            self.file_map = data.get("file_map", {})
            self.symbol_owners = {k: set(v) for k, v in data.get("symbol_owners", {}).items()}
            raw_shapes = data.get("param_shapes", {})
            self.param_shapes = {k: [tuple(t) for t in v] for k, v in raw_shapes.items()}
            raw_scoped = data.get("param_shapes_scoped", {})
            self.param_shapes_scoped = {k: [tuple(t) for t in v] for k, v in raw_scoped.items()}
            self.singleton_objects = data.get("singleton_objects", [])
            self.method_returns = data.get("method_returns", {})
            self.method_suspend = data.get("method_suspend", {})

    def register_type(self, scope: str, identifier: str, type_str: str) -> None:
        """Stores a type with its Fully Qualified Domain Name (FQDN) to prevent scope collisions."""
        fqdn = f"{scope}.{identifier}"
        self.types[fqdn] = type_str
        
    def get_type(self, scope: str, identifier: str) -> Optional[str]:
        """Retrieves a type using its Fully Qualified Domain Name (FQDN)."""
        fqdn = f"{scope}.{identifier}"
        return self.types.get(fqdn)
        
    def register_symbol_file(self, symbol: str, file_name: str) -> None:
        """Registers a global symbol (class, function, enum) to its output file name.
        `file_map` is last-writer-wins (single canonical owner); `symbol_owners`
        accumulates ALL owning files so the egress import injector can `hide` a
        name from every non-canonical import that also exports it."""
        self.file_map[symbol] = file_name
        self.symbol_owners.setdefault(symbol, set()).add(file_name)

    def register_symbol_owner_only(self, symbol: str, file_name: str) -> None:
        """Records that `file_name` ALSO declares a top-level `symbol` for the
        purposes of ambiguous_import `hide` detection, WITHOUT touching
        `file_map`. Used for Kotlin nested `class`/`object`/`enum class`
        declarations, which the egress HOISTS to Dart module level (Dart has no
        nested-class syntax) — so they become top-level names that can collide
        across files, but must NOT override the last-writer `file_map` canonical
        owner used elsewhere for reference-driven import injection."""
        if symbol and file_name:
            self.symbol_owners.setdefault(symbol, set()).add(file_name)

    def get_symbol_owners(self, symbol: str) -> set:
        """All output file names (without `.dart`) that declare a top-level
        `symbol`. Empty set if the symbol was never registered. Used by the
        egress import injector to detect ambiguous_import and emit `hide`."""
        return self.symbol_owners.get(symbol, set())
        
    def get_symbol_file(self, symbol: str) -> Optional[str]:
        """Retrieves the file name where a symbol is defined."""
        return self.file_map.get(symbol)

    def register_singleton_object(self, name: str) -> None:
        """Records that Kotlin `object <name>` lowers to a stateful Dart
        singleton, so call sites `<name>.member` can be rewritten to
        `<name>.instance.member` at egress."""
        if name and name not in self.singleton_objects:
            self.singleton_objects.append(name)

    def is_singleton_object(self, name: str) -> bool:
        """True if `name` is a stateful-singleton Kotlin object (its members are
        instance members reached via `.instance`)."""
        return name in self.singleton_objects

    def register_param_shape(self, name: str, shape: List[tuple], file_scope: Optional[str] = None) -> None:
        """Stores the ordered parameter shape for a callable (data class,
        regular class primary constructor, or top-level function/composable).
        Always registers under the bare symbol name (same key space as
        `file_map`; last writer wins on collision — see `param_shapes`
        docstring for the Kotlin overload caveat). When `file_scope` is given
        (the declaring Kotlin file's output name), ALSO registers under the
        scope-qualified key `f"{file_scope}.{name}"` in `param_shapes_scoped`,
        so same-named composables/classes declared in different files no
        longer corrupt each other's shape (cluster-5 sweep-3-escalation-2)."""
        self.param_shapes[name] = shape
        if file_scope:
            self.param_shapes_scoped[f"{file_scope}.{name}"] = shape

    def get_param_shape(self, name: str, file_scope: Optional[str] = None) -> Optional[List[tuple]]:
        """Retrieves the ordered parameter shape for a callable name. When
        `file_scope` is given, tries the scope-qualified key first (exact
        match for the declaration the caller is emitting/resolving); falls
        back to the bare-name (last-writer-wins) map if no qualified entry
        exists, so behavior is never worse than before this fix for callers
        that cannot supply a scope (e.g. a call site resolving a callee
        declared in an unknown file)."""
        if file_scope:
            scoped = self.param_shapes_scoped.get(f"{file_scope}.{name}")
            if scoped is not None:
                return scoped
        return self.param_shapes.get(name)
