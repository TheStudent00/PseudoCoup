from typing import Optional

from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)

class DartEmitter:
    def __init__(self, ledger):
        self.ledger = ledger
        self.indent_level = 0
        self.scopes = [{}]  # List of sets for tracking variable declarations
        self.injected_wrappers = set()
        # Async-frame stack (ported from the WFL vendored emitter, generic
        # Kotlin->Dart concern): one boolean per function body currently being
        # emitted — True iff that body is emitted as Dart `async`, so
        # visit_CallNode can decide whether `await` is legal at a call site.
        self._async_stack = []
        # Emit-scope strings (`ClassName.method` / bare `name`) in the CURRENT
        # module that must be lowered to `async`/`Future<R>` because their body
        # consumes a suspend/async-required call result. Populated per module
        # by `_compute_async_required` at the top of visit_ModuleNode.
        self._module_async_scopes = set()

    def _indent(self) -> str:
        return "    " * self.indent_level

    def push_scope(self):
        self.scopes.append(set())

    def pop_scope(self):
        self.scopes.pop()

    def declare_var(self, name: str):
        self.scopes[-1].add(name)

    def is_declared(self, name: str) -> bool:
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False

    def map_type(self, py_type: str) -> str:
        if not py_type or py_type == 'var' or py_type == 'dynamic':
            return 'var'
        mapping = {
            'int': 'int',
            'str': 'String',
            'float': 'double',
            'bool': 'bool',
            'List[str]': 'List<String>',
            'List[int]': 'List<int>',
            'Dict[str, int]': 'Map<String, int>',
            'Optional[int]': 'int?',
            'Optional[Any]': 'dynamic',
            'Any': 'dynamic',
            'None': 'void',
            'Tuple[str, int]': 'List<dynamic>'
        }
        return mapping.get(py_type, py_type)

    def generate(self, node: URNode) -> str:
        if node is None:
            return "/* Unmapped */"
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: URNode) -> str:
        raise NotImplementedError(f"No visit_{node.__class__.__name__} method")

    def _compute_import_hides(self, own_file):
        """Returns {wrapper_name: set(names_to_hide)} for the current file's
        import set (`self.injected_wrappers`), resolving ambiguous imports so
        every top-level name exported by two imported libraries stays visible
        from exactly one (the canonical owner) and is `hide`-n from the others.

        Ported from the WFL vendored emitter's `_compute_import_hides`; only
        the GENERIC collision source is upstreamed here — transpiled-vs-
        transpiled: a name declared in more than one source file
        (`ledger.symbol_owners` has >1 entry). Keep it visible from the
        canonical owner (`ledger.file_map`, last-writer) and hide it from every
        OTHER imported owner. If the canonical owner is NOT among this file's
        imports, fall back to keeping it visible from ONE deterministically-
        chosen imported owner (min by name) and hiding the rest, so exactly one
        survives. (The vendored copy's other two collision sources — kit.dart
        canonical shims and flutter/material-vs-kit — are WFL/Flutter
        app-specific and were NOT ported.)"""
        wrappers = set(self.injected_wrappers)
        if own_file is not None:
            wrappers.discard(own_file)
        hides = {}

        def add_hide(wrapper, name):
            hides.setdefault(wrapper, set()).add(name)

        # Transpiled-vs-transpiled duplicate top-level names. Only names that
        # (a) have >1 owning file and (b) have >=2 of those owners among THIS
        # file's imports can be ambiguous here.
        for name, owners in self.ledger.symbol_owners.items():
            if len(owners) < 2:
                continue
            imported_owners = owners & wrappers
            if len(imported_owners) < 2:
                continue
            canonical = self.ledger.file_map.get(name)
            if canonical not in imported_owners:
                canonical = min(imported_owners)
            for owner in imported_owners:
                if owner != canonical:
                    add_hide(owner, name)

        return hides

    def visit_ModuleNode(self, node: ModuleNode) -> str:
        self.push_scope()
        self.injected_wrappers.add("builtins_py")

        # Sync->async lowering pre-pass (ported from the WFL vendored emitter,
        # generic Kotlin->Dart concern): before emitting ANY body in this
        # module, compute the set of this module's methods/functions that must
        # be lowered to Dart `async`/`Future<R>` because their body contains a
        # resolved-async call (to an intra-module fixpoint). This must run
        # first so the signature/async-ness of a caller emitted before its
        # callee (source order) is already known. Also seeds the ledger's
        # cross-module `async_required` overlay for later-emitting callers.
        self._compute_async_required(node)

        lines = []
        # A symbol defined in this same file resolves (via the ledger) to this
        # file's own name; importing yourself is an unused import in Dart —
        # drop it. `current_module_file` is set by a multi-file driver before
        # generate(); the default None keeps every import when unset.
        own_file = getattr(self, 'current_module_file', None)
        # Ambiguous-import resolution: compute, per imported library, the set
        # of top-level names to `hide` so a name exported by two imported
        # libraries resolves to a single canonical owner.
        hides = self._compute_import_hides(own_file)
        for wrapper in sorted(list(self.injected_wrappers)):
            if own_file is not None and wrapper == own_file:
                continue
            hide_clause = ""
            names = hides.get(wrapper)
            if names:
                hide_clause = " hide " + ", ".join(sorted(names))
            lines.append(f"import '{wrapper}.dart'{hide_clause};")
        if self.injected_wrappers:
            lines.append("")

        for stmt in node.body:
            # Filter out top-level strings (docstrings)
            if isinstance(stmt, LiteralNode) and isinstance(stmt.value, str):
                continue
            # Filter out Python execution hook if __name__ == "__main__"
            if isinstance(stmt, IfNode) and isinstance(stmt.condition, BinaryOpNode):
                if getattr(stmt.condition.left, 'name', '') == '__name__':
                    continue
                    
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.pop_scope()
        return "\n\n".join(lines)

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> str:
        if getattr(self, 'current_class_name', None):
            scope = f"{self.current_class_name}.{node.name}"
        else:
            scope = node.name

        # Expose `scope` as `self._current_scope` for the duration of this
        # body, so the ledger-driven receiver-type resolvers (used by the
        # async/suspend propagation, ported from the WFL vendored emitter) can
        # look up a bare-identifier receiver's declared type. try/finally
        # restores the prior scope on every exit path uniformly.
        prev_scope = getattr(self, '_current_scope', None)
        self._current_scope = scope
        try:
            return self._visit_FunctionDefNode_impl(node, scope)
        finally:
            self._current_scope = prev_scope

    def _visit_FunctionDefNode_impl(self, node: FunctionDefNode, scope: str) -> str:
        ret_type = node.metadata.get('type', 'dynamic')
        ret_type = self.map_type(ret_type)
        
        body_statements = node.body[:]
        sugared_args = set()
        
        # Unroll constructor assignments (self.x = x) into this.x params
        if node.name == "__init__" and getattr(self, 'current_class_name', None):
            idx = 0
            while idx < len(body_statements):
                stmt = body_statements[idx]
                if isinstance(stmt, AssignmentNode):
                    left = stmt.left
                    right = stmt.right
                    if isinstance(left, AttributeNode) and isinstance(left.value, IdentifierNode) and left.value.name in ("self", "this"):
                        if isinstance(right, IdentifierNode) and right.name == left.attr:
                            sugared_args.add(right.name)
                            idx += 1
                            continue
                break
            body_statements = body_statements[idx:]
        
        args_list = []
        for arg in node.args:
            if isinstance(node, MethodDefNode) and arg.name in ("self", "this"):
                continue
                
            if arg.name in sugared_args:
                args_list.append(f"this.{arg.name}")
            else:
                arg_type = self.ledger.get_type(scope, arg.name)
                if not arg_type:
                    arg_type = arg.metadata.get('type', 'dynamic')
                arg_type = self.map_type(arg_type)
                args_list.append(f"{arg_type} {arg.name}")
        
        args_str = ", ".join(args_list)
        
        lines = []
        is_ctor = node.name == "__init__" and getattr(self, 'current_class_name', None)
        is_suspend = False
        if is_ctor:
            if not body_statements:
                lines.append(f"{self._indent()}{self.current_class_name}({args_str});")
                return "\n".join(lines)
            else:
                lines.append(f"{self._indent()}{self.current_class_name}({args_str}) {{")
        else:
            # A function emits `async`/`Future<R>` if it is Kotlin `suspend`
            # OR the async pre-pass promoted its emit-scope (its body consumes
            # a suspend/async-required result). Both paths produce the
            # identical `Future<R> ... async { }` shape and set the same
            # `_async_stack` frame, so awaits inside a promoted function are
            # legal exactly as in a real suspend function. Constructors can't
            # be `async` in Dart and are never promoted.
            is_suspend = node.metadata.get('is_suspend', False) \
                or (scope in getattr(self, '_module_async_scopes', set()))
            if is_suspend:
                # `dynamic`/`void`/`var` (no declared return type == Unit)
                # becomes `Future<void>`; any real return type wraps as-is.
                future_ret = 'Future<void>' if ret_type in ('void', 'dynamic', 'var') else f'Future<{ret_type}>'
                lines.append(f"{self._indent()}{future_ret} {node.name}({args_str}) async {{")
            else:
                lines.append(f"{self._indent()}{ret_type} {node.name}({args_str}) {{")

        self._async_stack.append(bool(is_suspend) and not is_ctor)
        self.push_scope()
        for arg in node.args:
            if isinstance(node, MethodDefNode) and arg.name in ("self", "this"):
                continue
            self.declare_var(arg.name)
            
        self.indent_level += 1
        for stmt in body_statements:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
            
        self.indent_level -= 1
        self._async_stack.pop()
        self.pop_scope()

        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_MethodDefNode(self, node: MethodDefNode) -> str:
        return self.visit_FunctionDefNode(node)

    def visit_ClassDefNode(self, node: ClassDefNode) -> str:
        lines = []
        bases_str = f" extends {node.bases[0]}" if getattr(node, 'bases', None) else ""
        lines.append(f"{self._indent()}class {node.name}{bases_str} {{")
        
        self.push_scope()
        self.indent_level += 1
        
        prev_class_name = getattr(self, 'current_class_name', None)
        self.current_class_name = node.name
        
        # Ensure all fields are emitted before methods.
        for field in node.fields:
            lines.append(self.generate(field))
            
        for method in node.methods:
            lines.append(self.generate(method))

        # Kotlin data class: synthesize `.copy()` (ported from the WFL
        # vendored emitter, generic Kotlin->Dart concern). Skips classes that
        # already declare their own `copy` member.
        if node.metadata.get('is_data'):
            already_has_copy = any(
                getattr(m, 'name', None) == 'copy' for m in node.methods
            )
            if not already_has_copy:
                lines.append(self._synth_data_class_copy(node))

        self.current_class_name = prev_class_name
        self.indent_level -= 1
        self.pop_scope()
        
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def _synth_data_class_copy(self, node: ClassDefNode) -> str:
        """Synthesize `Foo copy({A? a, B? b}) => Foo(a: a ?? this.a, ...);` for
        a Kotlin data class (ported from the WFL vendored emitter). Field
        names/types come from `metadata['data_fields']`, recorded by the Kotlin
        ingestor's primary-constructor handling; every param is nullable so an
        omitted arg falls back to the current field value."""
        data_fields = node.metadata.get('data_fields') or []
        params = []
        ctor_args = []
        for fname, ftype in data_fields:
            dart_type = self.map_type(ftype) if ftype else 'dynamic'
            if not dart_type.endswith('?') and dart_type not in ('var', 'dynamic'):
                dart_type = f"{dart_type}?"
            params.append(f"{dart_type} {fname}")
            ctor_args.append(f"{fname}: {fname} ?? this.{fname}")
        params_str = ", ".join(params)
        ctor_args_str = ", ".join(ctor_args)
        return (
            f"{self._indent()}{node.name} copy({{{params_str}}}) => "
            f"{node.name}({ctor_args_str});"
        )

    # ------------------------------------------------------------------
    # Transitive async/suspend propagation (ported from the WFL vendored
    # emitter — the generic Kotlin->Dart concern only). All resolution is
    # ledger-driven; anything unresolvable returns None/False, never guessed.
    # ------------------------------------------------------------------

    def _strip_generic_wrapper(self, type_str: str) -> str:
        """Strips a Kotlin nullable marker and ONE layer of generic wrapper
        from a raw type string to get the bare declaring-type name that owns
        the methods (`ProgramDao?` -> `ProgramDao`; `Flow<T?>` -> `Flow`).
        Returns '' for empty/None input."""
        if not type_str:
            return ''
        s = type_str.strip()
        if s.endswith('?'):
            s = s[:-1]
        generic_start = s.find('<')
        if generic_start != -1:
            s = s[:generic_start]
        return s.strip()

    def _get_bare_identifier_type(self, name: str) -> Optional[str]:
        """Declared-type lookup for a bare identifier: tries the current
        method/function scope first (locals and params), then the current
        class scope (primary-constructor property fields are registered under
        the class name at ingest). Both are the same
        `ledger.get_type(scope, identifier)` FQDN mechanism; returns None if
        neither scope is set or neither lookup hits."""
        current_scope = getattr(self, '_current_scope', None)
        if current_scope:
            t = self.ledger.get_type(current_scope, name)
            if t:
                return t
        class_scope = getattr(self, 'current_class_name', None)
        if class_scope:
            t = self.ledger.get_type(class_scope, name)
            if t:
                return t
        return None

    def _resolve_receiver_method_return(self, receiver_node: URNode, method_name: str) -> Optional[str]:
        """Resolves the raw Kotlin return-type string for a call
        `receiver.method_name(...)` when `receiver` is a bare IdentifierNode
        whose declared type the ledger knows. Returns None (never a guessed
        type) when any resolution step fails."""
        if not isinstance(receiver_node, IdentifierNode):
            return None
        receiver_type = self._get_bare_identifier_type(receiver_node.name)
        if not receiver_type:
            return None
        declaring_type = self._strip_generic_wrapper(receiver_type)
        if not declaring_type:
            return None
        return self.ledger.get_method_return(declaring_type, method_name)

    def _is_receiver_method_suspend(self, receiver_node: URNode, method_name: str) -> bool:
        """True if the resolved declaring-type method was declared Kotlin
        `suspend fun` OR was promoted to async by the pre-pass
        (`ledger.async_required`). False (not None) when unresolvable, since
        callers use this as a boolean gate."""
        if not isinstance(receiver_node, IdentifierNode):
            return False
        receiver_type = self._get_bare_identifier_type(receiver_node.name)
        if not receiver_type:
            return False
        declaring_type = self._strip_generic_wrapper(receiver_type)
        if not declaring_type:
            return False
        return (
            self.ledger.is_method_suspend(declaring_type, method_name)
            or self.ledger.is_async_required(declaring_type, method_name)
        )

    def _call_is_async_result(self, node: CallNode) -> bool:
        """Single source of truth for 'does this CallNode produce an
        async/Flow-suspend value that needs `await`'. Used BOTH by the
        emit-time await-injection in `visit_CallNode` AND by the async
        pre-pass (`_compute_async_required`), so the set of calls that
        triggers async promotion is EXACTLY the set that triggers
        `await`/AWAIT-IN-SYNC. Recognizes (all ledger-driven):
          (a) `receiver.method(...)` where `method` resolves to a Kotlin
              `suspend fun` or an egress-promoted async-required method;
          (b) `receiver.method(...).first()` — the zero-arg Flow terminal on
              a `Flow<...>`-returning method;
          (c) bare `foo()` (implicit `this`) resolving to a suspend/
              async-required method on the class being emitted."""
        func_val = node.func_name
        if isinstance(func_val, AttributeNode):
            if self._is_receiver_method_suspend(func_val.value, func_val.attr):
                return True
            if (
                func_val.attr == "first"
                and not node.args
                and isinstance(func_val.value, CallNode)
                and isinstance(func_val.value.func_name, AttributeNode)
            ):
                inner_fn = func_val.value.func_name
                inner_ret = self._resolve_receiver_method_return(inner_fn.value, inner_fn.attr)
                if inner_ret and self._strip_generic_wrapper(inner_ret) == "Flow":
                    return True
            return False
        if isinstance(func_val, IdentifierNode):
            _cls = getattr(self, 'current_class_name', None)
            if _cls and (
                self.ledger.is_method_suspend(_cls, func_val.name)
                or self.ledger.is_async_required(_cls, func_val.name)
            ):
                return True
        return False

    def _iter_calls(self, node, _root=True):
        """Yield every CallNode reachable in the subtree rooted at `node`,
        WITHOUT descending into a nested FunctionDefNode/MethodDefNode body (a
        nested function/lambda is its own async scope; `_root=True` lets the
        top-level callable whose body we ARE analyzing be descended into).
        Structural walk over every child-bearing attribute in the UR AST."""
        if node is None:
            return
        if isinstance(node, (FunctionDefNode, MethodDefNode)) and not _root:
            return
        if isinstance(node, CallNode):
            yield node
        # Scalar child slots across the UR AST.
        for attr in ("value", "func_name", "left", "right", "condition",
                     "slice", "orelse", "target", "iter"):
            child = getattr(node, attr, None)
            if isinstance(child, URNode):
                yield from self._iter_calls(child, _root=False)
        # List child slots.
        for attr in ("args", "keys", "values", "elements", "children",
                     "modifiers", "handlers", "methods", "fields", "bases"):
            seq = getattr(node, attr, None)
            if isinstance(seq, list):
                for c in seq:
                    if isinstance(c, URNode):
                        yield from self._iter_calls(c, _root=False)
        # `properties` is a dict[str, URNode] on DeclarativeNode.
        props = getattr(node, 'properties', None)
        if isinstance(props, dict):
            for c in props.values():
                if isinstance(c, URNode):
                    yield from self._iter_calls(c, _root=False)
        # `body` carries statements for control-flow nodes AND callable bodies.
        body = getattr(node, 'body', None)
        if isinstance(body, list):
            for c in body:
                if isinstance(c, URNode):
                    yield from self._iter_calls(c, _root=False)

    def _collect_module_methods(self, module_node):
        """Return a list of (emit_scope, class_name, func_node) for every
        top-level function and every method inside a class in this module.
        `emit_scope` is the SAME string the emitter uses as the async-set key:
        `ClassName.method` for a method, bare `name` for a top-level function.
        `class_name` is the enclosing class name or None."""
        out = []

        def walk_class(cls_node, cls_name):
            for member in getattr(cls_node, 'methods', []) or []:
                if isinstance(member, (FunctionDefNode, MethodDefNode)) \
                        and not member.metadata.get('is_init_block'):
                    out.append((f"{cls_name}.{member.name}", cls_name, member))
            for nested in (cls_node.metadata.get('nested_classes') or []):
                if isinstance(nested, ClassDefNode):
                    walk_class(nested, nested.name)

        for node in getattr(module_node, 'body', []) or []:
            if isinstance(node, (FunctionDefNode, MethodDefNode)):
                out.append((node.name, None, node))
            elif isinstance(node, ClassDefNode):
                walk_class(node, node.name)
        return out

    def _compute_async_required(self, module_node):
        """Per-module async PRE-PASS (ported from the WFL vendored emitter).

        Populates `self._module_async_scopes` (this module's emit-scope
        strings that must become Dart `async`/`Future<R>`) AND the ledger's
        cross-module `async_required` set, to an INTRA-MODULE FIXPOINT: a
        method is async-required iff its body contains a call for which
        `_call_is_async_result` is true; that predicate already fires for a
        call to a `suspend fun` OR an already-async-required method, so the
        loop repeats until a full pass adds nothing. Bounded by the method
        count, so it always terminates.

        Bound of correctness (documented, not guessed): transitivity is
        captured only for calls the ledger can resolve to a declaring type.
        A cross-module caller whose module already emitted, or an
        unresolvable call, stays flagged `/* AWAIT-IN-SYNC */` — never
        guessed. Constructors are never promoted (Dart forbids `async`
        constructors)."""
        methods = self._collect_module_methods(module_node)
        if not methods:
            self._module_async_scopes = set()
            return
        marked = set()
        prev_class = getattr(self, 'current_class_name', None)
        try:
            changed = True
            while changed:
                changed = False
                for emit_scope, cls_name, func_node in methods:
                    if emit_scope in marked:
                        continue
                    if func_node.name == "__init__":
                        continue
                    if func_node.metadata.get('is_suspend'):
                        # Already async at declaration — not a promotion; its
                        # callers already await via is_method_suspend.
                        continue
                    # `_call_is_async_result` on a bare-`this` call needs the
                    # enclosing class name in scope, exactly as at emit time.
                    self.current_class_name = cls_name
                    body_has_async = any(
                        self._call_is_async_result(call)
                        for call in self._iter_calls(func_node)
                    )
                    if body_has_async:
                        marked.add(emit_scope)
                        # Cross-module overlay so later-emitting callers await.
                        if cls_name:
                            self.ledger.register_async_required(cls_name, func_node.name)
                        changed = True
        finally:
            self.current_class_name = prev_class
        self._module_async_scopes = marked

    def visit_AssignmentNode(self, node: AssignmentNode) -> str:
        if node.right is None:
            if isinstance(node.left, IdentifierNode) and not self.is_declared(node.left.name):
                var_type = node.left.metadata.get('type', 'var')
                var_type = self.map_type(var_type)
                self.declare_var(node.left.name)
                default = ""
                if var_type == "int": default = " = 0"
                elif var_type == "double": default = " = 0.0"
                elif var_type == "bool": default = " = false"
                elif var_type == "String": default = " = \"\""
                return f"{self._indent()}{var_type} {node.left.name}{default};"
            else:
                left_str = self.generate(node.left)
                return f"{self._indent()}{left_str};"

        right_str = self.generate(node.right)
        
        if isinstance(node.left, IdentifierNode) and not self.is_declared(node.left.name):
            var_type = node.left.metadata.get('type', 'var')
            var_type = self.map_type(var_type)
            left_str = f"{var_type} {node.left.name}"
            self.declare_var(node.left.name)
        else:
            left_str = self.generate(node.left)
            
        return f"{self._indent()}{left_str} = {right_str};"

    def visit_ReturnNode(self, node: ReturnNode) -> str:
        if node.value is None:
            return f"{self._indent()}return;"
        val_str = self.generate(node.value)
        return f"{self._indent()}return {val_str};"

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        left_str = self.generate(node.left)
        right_str = self.generate(node.right)
        op = node.operator
        if op == "in":
            return f"{right_str}.contains({left_str})"
        if op == "//":
            op = "~/"
        if op == "is" and right_str == "null":
            op = "=="
        
        if getattr(node.left, 'name', None) == "":
            return f"{op}({right_str})"
            
        return f"{left_str} {op} {right_str}"

    def visit_CallNode(self, node: CallNode, _skip_await_check: bool = False) -> str:
        # `await`-injection (ported from the WFL vendored emitter, generic
        # Kotlin->Dart concern): a call whose result is an async/Flow-suspend
        # value (per `_call_is_async_result`, ledger-driven, never guessed)
        # gets `await` when the enclosing body is async; otherwise a greppable
        # `/* AWAIT-IN-SYNC */` flag is emitted instead, leaving the call text
        # untouched. `_skip_await_check` prevents re-checking on the recursive
        # render of the same node.
        if not _skip_await_check and self._call_is_async_result(node):
            enclosing_async = bool(self._async_stack) and self._async_stack[-1]
            rendered_call = self.visit_CallNode(node, _skip_await_check=True)
            if enclosing_async:
                return f"await {rendered_call}"
            return f"/* AWAIT-IN-SYNC */ {rendered_call}"

        func_val = node.func_name
        if isinstance(func_val, IdentifierNode):
            func_str = func_val.name
        elif isinstance(func_val, str):
            func_str = func_val
        else:
            func_str = self.generate(func_val)

        if func_str == "len" and node.args:
            arg_str = self.generate(node.args[0])
            return f"{arg_str}.length"
        if func_str == "str" and node.args:
            arg_str = self.generate(node.args[0])
            return f"({arg_str}).toString()"
            
        if isinstance(func_str, str):
            if func_str.startswith("math."):
                self.injected_wrappers.add("math_py")
                func_str = func_str.replace("math.", "math_py.", 1)
            elif func_str.startswith("os."):
                self.injected_wrappers.add("io_py")
                func_str = func_str.replace("os.", "io_py.", 1)
            elif func_str.startswith("requests."):
                self.injected_wrappers.add("network_py")
                func_str = func_str.replace("requests.", "network_py.", 1)
        else:
            func_str = str(func_str)
            
        args_str = ", ".join(self.generate(arg) for arg in node.args)
        return f"{func_str}({args_str})"

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        if node.name == "self":
            return "this"
        return node.name

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        if isinstance(node.value, bool):
            return "true" if node.value else "false"
        elif isinstance(node.value, str):
            return f'"{node.value}"'
        else:
            return str(node.value)

    def visit_IfNode(self, node: IfNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}if ({condition_str}) {{"]
        
        self.push_scope()
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.indent_level -= 1
        self.pop_scope()
        
        if node.orelse:
            if isinstance(node.orelse, IfNode):
                if isinstance(node.orelse.condition, LiteralNode) and node.orelse.condition.value is True:
                    lines.append(f"{self._indent()}}} else {{")
                    self.push_scope()
                    self.indent_level += 1
                    for stmt in node.orelse.body:
                        stmt_str = self.generate(stmt)
                        if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                            lines.append(stmt_str)
                        else:
                            lines.append(f"{self._indent()}{stmt_str};")
                    self.indent_level -= 1
                    self.pop_scope()
                    lines.append(f"{self._indent()}}}")
                else:
                    orelse_str = self.generate(node.orelse).lstrip()
                    lines.append(f"{self._indent()}}} else {orelse_str}")
        else:
            lines.append(f"{self._indent()}}}")
            
        return "\n".join(lines)

    def visit_WhileNode(self, node: WhileNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}while ({condition_str}) {{"]
        
        self.push_scope()
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_ForNode(self, node: ForNode) -> str:
        target_str = self.generate(node.target)
        iter_str = self.generate(node.iter)
        
        self.push_scope()
        if isinstance(node.target, IdentifierNode):
            self.declare_var(node.target.name)
            
        lines = [f"{self._indent()}for (var {target_str} in {iter_str}) {{"]
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_TryCatchNode(self, node: TryCatchNode) -> str:
        lines = [f"{self._indent()}try {{"]
        self.push_scope()
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.indent_level -= 1
        self.pop_scope()
        
        lines.append(f"{self._indent()}}} catch (e) {{")
        self.push_scope()
        self.declare_var("e")
        self.indent_level += 1
        
        for stmt in node.handlers:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
                    
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_ListNode(self, node: ListNode) -> str:
        elements_str = ", ".join(self.generate(e) for e in node.elements)
        return f"[{elements_str}]"

    def visit_DictNode(self, node: DictNode) -> str:
        pairs = []
        for k, v in zip(node.keys, node.values):
            pairs.append(f"{self.generate(k)}: {self.generate(v)}")
        pairs_str = ", ".join(pairs)
        return f"{{{pairs_str}}}"

    def visit_SubscriptNode(self, node: SubscriptNode) -> str:
        value_str = self.generate(node.value)
        slice_str = self.generate(node.slice)
        return f"{value_str}[{slice_str}]"

    def visit_AttributeNode(self, node: AttributeNode) -> str:
        value_str = self.generate(node.value)
        return f"{value_str}.{node.attr}"


