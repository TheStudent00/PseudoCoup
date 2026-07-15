from tree_sitter import Parser, Language
import tree_sitter_kotlin as tskotlin
import re
from typing import Optional
from pseudocoup.core.ledger import Ledger
from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, ClassDefNode, MethodDefNode,
    AssignmentNode, ReturnNode, BinaryOpNode, CallNode,
    IdentifierNode, LiteralNode,
    IfNode, WhileNode, ForNode, TryCatchNode,
    ListNode, DictNode, SubscriptNode, AttributeNode
)

class KotlinIngestor:
    def __init__(self, ledger: Ledger, recorder=None):
        self.ledger = ledger
        # Optional CoverageRecorder (Task 13). When None, ingest is unchanged.
        self.recorder = recorder
        self.parser = Parser()
        
        # Determine tree-sitter version compat
        try:
            # For tree-sitter < 0.22
            self.language = Language(tskotlin.language(), "kotlin")
            self.parser.set_language(self.language)
        except Exception:
            # For tree-sitter >= 0.22
            self.language = Language(tskotlin.language())
            try:
                self.parser.set_language(self.language)
            except AttributeError:
                self.parser.language = self.language

    def parse(self, source_bytes: bytes, file_scope: Optional[str] = None) -> ModuleNode:
        # Cluster-5 sweep-3-escalation-2: `file_scope` (the declaring file's
        # eventual output name) is stashed as instance state rather than
        # threaded through every recursive `_map_node` call signature (it is
        # called with positional/keyword `scope` hundreds of times below).
        # `register_param_shape` call sites read `self._file_scope` to also
        # populate the scope-qualified ledger index. Reset per-call so a
        # missing `file_scope` (e.g. ad-hoc/test callers) degenerates cleanly
        # to bare-name-only registration (today's behavior).
        self._file_scope = file_scope
        tree = self.parser.parse(source_bytes)
        root_node = tree.root_node
        result = self._map_node(root_node, source_bytes, "main")
        if self.recorder is not None:
            # Every node `_map_node` was never invoked on is `unvisited`
            # (trivia a parent skipped, or a construct a parent dropped).
            self.recorder.finish_file(root_node)
        return result

    def ingest(self, source_bytes: bytes, file_scope: Optional[str] = None) -> ModuleNode:
        return self.parse(source_bytes, file_scope)

    # Unit: scope-function (`apply`/`also`/`run`/`with`/`buildString`) receiver
    # tagging. Kotlin's scope functions bind the receiver IMPLICITLY inside the
    # trailing lambda body (bare `put(...)`/`append(...)` mean
    # `receiver.put(...)`/`receiver.append(...)`), but the generic lambda-arg
    # mapping just above only adds `it` as a declared param when the literal
    # text `\bit\b` appears in the body (Kotlin's *other* implicit-lambda-arg
    # convention, for single-arg lambdas like `map { it.foo() }`). A
    # `.apply {}`/`buildString {}` body almost never mentions `it` (it mentions
    # the receiver's members bare instead), so it fell through to a
    # zero-arg `() { ... }` Dart closure with every member call left BARE —
    # `appendLine(...)`/`put(...)` resolve to nothing at the Dart call site.
    # This tags the mapped lambda so the egress emitter (dart.py) can push a
    # (receiver_var, receiver_type) frame and prefix bare member calls with the
    # resolved receiver ('it', matching kit.dart's documented convention — see
    # kit.dart's `buildString`/StringBuilder comment block).
    #
    def _scope_fn_receiver_type(self, receiver_ctor_name: Optional[str]) -> Optional[str]:
        """Resolve the receiver type name for an `X().apply{}`/`.also{}`/
        `.run{}` call. `receiver_ctor_name` is the bare constructor name `X`
        (e.g. "JSONObject", "PendingRestart"). Domain types are resolved
        via the ledger's param_shapes (the project's constructor-registration
        mechanism — a data class / class primary ctor registers its shape
        there at ingest, see `register_param_shape` call sites above). Returns
        None (UNBOUND-RECEIVER case) when neither source recognizes the name."""
        if receiver_ctor_name is None:
            return None
        if self.ledger.get_param_shape(receiver_ctor_name) is not None:
            return receiver_ctor_name
        return None

    def _is_coroutine_builder(self, func_name) -> bool:
        """True when `func_name` denotes a coroutine builder whose trailing
        lambda body runs in a suspend/async context, so an `await` inside is
        legal. Recognizes bare `launch`/`withContext`/`runBlocking`
        identifier calls, and `<scope>.launch { }` attribute calls where the
        receiver is one of the known coroutine scopes (viewModelScope, scope) — deliberately NOT Android's ActivityResultLauncher.launch."""
        _scopes = {"viewModelScope", "scope"}
        if isinstance(func_name, IdentifierNode):
            return func_name.name in {"launch", "withContext", "runBlocking"}
        if isinstance(func_name, AttributeNode) and func_name.attr == "launch":
            recv = func_name.value
            if isinstance(recv, IdentifierNode):
                return recv.name in _scopes
            if isinstance(recv, AttributeNode):
                return recv.attr in _scopes
        return False

    def _tag_scope_fn_lambda(self, func_name, lambda_ur_node) -> None:
        """If `func_name` is a recognized scope-function callee
        (`.apply`/`.run` attribute call, or bare `with`/`buildString`
        identifier call) and `lambda_ur_node` is the mapped trailing-lambda
        FunctionDefNode, tag it with `metadata['scope_fn']` = {kind,
        receiver_type} for the egress emitter's receiver-frame tracking, and
        force `it` as the lambda's declared param when the generic mapper
        above left it argless (so the emitted Dart closure always exposes a
        name for the receiver, matching kit.dart's `buildString` 1-arg shape).
        No-op when `func_name` is not a recognized scope function.

        IMPORTANT: `.also` and `.let` are deliberately EXCLUDED here despite
        both being attribute-call scope functions. Per Kotlin semantics only
        `apply`/`run`/`with` bind an IMPLICIT receiver (`this`) against which
        bare member calls resolve; `also` and `let` bind their single lambda
        param as `it`, a VALUE, not a receiver — bare calls inside an
        `.also {}`/`.let {}` body are free calls (or, if nested inside an
        outer `.apply`, members of that OUTER receiver), never members of the
        `also`/`let` value itself. Treating `.also` like `.apply` was the
        cause of a real regression: `curriculumId?.let { put(KEY_CURRICULUM,
        it) }` nested inside an outer `JSONObject().apply { ... }` emitted
        `it.put(KEY_CURRICULUM, it)` — the second `it` (the `let` value,
        curriculumId) got conflated with the injected receiver prefix meant
        for the outer `apply`. Excluding `also`/`let` from tagging means no
        scope-fn frame is pushed for their lambda bodies, so the emitter's
        receiver-frame stack (see dart.py `_scope_fn_stack`) correctly falls
        through to the outer `apply` frame for bare calls, while a literal
        `it` written in source (the `also`/`let` value) passes through
        untouched as a plain identifier — no more name collision."""
        if lambda_ur_node is None or not isinstance(lambda_ur_node, FunctionDefNode):
            return

        kind = None
        receiver_type = None

        if isinstance(func_name, AttributeNode) and func_name.attr in ("apply", "run"):
            # Receiver is `func_name.value`, expected shape `X(...)` (a
            # CallNode whose func_name is a bare IdentifierNode naming the
            # constructed type). Any other receiver shape (a plain variable,
            # a chained call) is legitimately unresolvable here -> UNBOUND.
            recv = func_name.value
            ctor_name = None
            if isinstance(recv, CallNode) and isinstance(recv.func_name, IdentifierNode):
                ctor_name = recv.func_name.name
            kind = func_name.attr
            receiver_type = self._scope_fn_receiver_type(ctor_name)
        elif isinstance(func_name, IdentifierNode) and func_name.name == "buildString":
            kind = "buildString"
            receiver_type = "StringBuilder"
        elif isinstance(func_name, IdentifierNode) and func_name.name == "with":
            # `with(x) { ... }` receiver is the first call argument, folded
            # separately by the curried-call branch below (it is not visible
            # here as `func_name` carries no arg info); tagged there instead.
            return

        if kind is None:
            return

        lambda_ur_node.metadata['scope_fn'] = {
            'kind': kind,
            'receiver_type': receiver_type,
        }
        if not lambda_ur_node.args:
            lambda_ur_node.args = [IdentifierNode("it")]

    def _append_stmt(self, body: list, mapped) -> None:
        """Append a mapped statement to a body, flattening lists.

        A few lowerings (notably control-flow elvis, `val v = expr ?: return`)
        desugar one Kotlin statement into several UR statements and return a
        list; every statement-body loop routes through here so those lists get
        spliced in rather than nested as a single element.

        A bare control-flow elvis used as its own statement (`enrolled ?:
        return X`) is a null-guard; lower it to `if (enrolled == null) X;`
        since `expr ?? return X` is not valid Dart."""
        if mapped is None:
            return
        if isinstance(mapped, list):
            for m in mapped:
                self._append_stmt(body, m)
            return
        if (isinstance(mapped, BinaryOpNode) and mapped.operator == "?:"
                and self._is_control_flow_expr(mapped.right)):
            cond = BinaryOpNode(mapped.left, IdentifierNode("null"), "==")
            body.append(IfNode(cond, [mapped.right], None))
            return
        body.append(mapped)

    @staticmethod
    def _is_control_flow_expr(node) -> bool:
        """True for expressions that are statements in Dart (return/continue/
        break), which therefore cannot sit on the RHS of Dart's `??`."""
        if isinstance(node, ReturnNode):
            return True
        if isinstance(node, IdentifierNode) and node.name in ("continue", "break"):
            return True
        if isinstance(node, CallNode) and node.func_name in ("continue", "break"):
            return True
        return False

    def _lower_elvis_control_flow(self, left, right):
        """Given `left = right` where `right` is a control-flow elvis
        (`expr ?: return/continue/break`), return a two-statement lowering:
            left = expr;
            if (left == null) <control-flow>;
        Returns None when it does not apply (caller then builds a normal
        AssignmentNode). No new node types or helper names are introduced."""
        if not isinstance(right, BinaryOpNode) or right.operator != "?:":
            return None
        if not self._is_control_flow_expr(right.right):
            return None
        cf = right.right
        # `continue`/`break` arrive as bare IdentifierNodes; the emitter renders
        # an identifier as its name, so as a statement they become
        # `continue;`/`break;`. `return` is already a ReturnNode. No wrapping.
        assign = AssignmentNode(left, right.left)
        cond = BinaryOpNode(left, IdentifierNode("null"), "==")
        guard = IfNode(cond, [cf], None)
        return [assign, guard]

    def _hoist_binding_rhs(self, left, right):
        """Handle `x = when (val r = expr) { ... }` (or the `if`/`when` binding
        form) on the RHS of an assignment/property.

        `_map_when` lowers a subject that is itself a binding (`when (val r =
        e)`) into a Python list `[bind_stmt, if_chain]`: the binding must run as
        a statement before the branch chain. In statement position `_append_stmt`
        splices such lists. But on the RHS of an assignment the whole list would
        land in expression position and reach the emitter as a raw `list`
        (rendered `/* UNRENDERED: list */`).

        Split it: hoist every leading statement, then assign the final branch
        expression to `left`. Returns a statement list, or None when `right` is
        not such a hoistable list (caller then builds a normal AssignmentNode)."""
        if not isinstance(right, list) or not right:
            return None
        *prefix, value = right
        return [*prefix, AssignmentNode(left, value)]

    def _get_text(self, node, source_bytes: bytes) -> str:
        if node is None:
            return ""
        return source_bytes[node.start_byte:node.end_byte].decode('utf-8')

    def _map_when(self, node, source_bytes: bytes, scope: str = "main") -> URNode:
        """Lower a Kotlin `when` expression to a nested IfNode chain.

        The emitter renders IfNode chains as ternaries (expression position) or
        if/else statements, so `when` reuses that machinery. Both subject
        (`when (x) { A, B -> ...; is T -> ...; in r -> ...; else -> ... }`) and
        subjectless (`when { cond -> ...; else -> ... }`) forms are supported.
        """
        subject_node = next((c for c in node.named_children if c.type == 'when_subject'), None)
        # A subject can be a plain expression (`when (x)`) or a binding
        # (`when (val result = expr)`). tree-sitter models the binding as a
        # `variable_declaration` child followed by the value expression. In that
        # case the comparison subject is the *bound variable*, and the binding
        # itself must be hoisted as a statement before the if-chain (a bare
        # `variable_declaration` has no UR mapping and would otherwise render the
        # subject as empty, producing `is(X)` with no left operand).
        bind_stmt = None
        bind_name = None
        subject_expr_node = None
        if subject_node is not None:
            var_decl = next((c for c in subject_node.named_children
                             if c.type == 'variable_declaration'), None)
            if var_decl is not None:
                ident = next((c for c in var_decl.named_children
                              if c.type in ('identifier', 'simple_identifier')), None)
                bind_name = self._get_text(ident, source_bytes) if ident is not None else None
                value_node = next((c for c in subject_node.named_children
                                   if c is not var_decl), None)
                if bind_name and value_node is not None:
                    bind_stmt = AssignmentNode(
                        IdentifierNode(bind_name),
                        self._map_node(value_node, source_bytes, scope),
                    )
            else:
                subject_expr_node = next((c for c in subject_node.named_children), None)

        def _clone_subject():
            # Re-map the subject per branch so nodes are not shared across the tree.
            if bind_name is not None:
                return IdentifierNode(bind_name)
            if subject_expr_node is not None:
                return self._map_node(subject_expr_node, source_bytes, scope)
            return None

        entries = [c for c in node.named_children if c.type == 'when_entry']

        def _branch_body(result_node):
            body = []
            if result_node is None:
                return body
            if result_node.type == 'block':
                for child in result_node.named_children:
                    self._append_stmt(body, self._map_node(child, source_bytes, scope))
            else:
                self._append_stmt(body, self._map_node(result_node, source_bytes, scope))
            return body

        def _condition_for(cond_node):
            # Build the boolean condition for a single when-entry condition node.
            if cond_node.type == 'type_test':
                # `is T` -> `subject is T`
                type_node = next((c for c in cond_node.named_children), None)
                type_name = self._get_text(type_node, source_bytes) if type_node else ""
                return BinaryOpNode(_clone_subject() or IdentifierNode(""), IdentifierNode(type_name), "is")
            if cond_node.type == 'range_test':
                # `in range` -> `range.contains(subject)`
                rng = next((c for c in cond_node.named_children), None)
                rng_mapped = self._map_node(rng, source_bytes, scope) if rng else None
                return BinaryOpNode(_clone_subject() or IdentifierNode(""), rng_mapped, "in")
            mapped = self._map_node(cond_node, source_bytes, scope)
            if subject_node is not None:
                # Subject form: `A` -> `subject == A`
                return BinaryOpNode(_clone_subject() or IdentifierNode(""), mapped, "==")
            # Subjectless form: the condition is already boolean.
            return mapped

        def _with_binding(chain):
            # If the subject was a `when (val x = expr)` binding, hoist the
            # assignment before the if-chain. `_append_stmt` flattens the list.
            if bind_stmt is not None:
                return [bind_stmt, chain]
            return chain

        # Build the chain from the bottom up.
        root = None
        prev_if = None
        for entry in entries:
            named = [c for c in entry.named_children
                     if c.type not in ('line_comment', 'block_comment', 'multiline_comment')]
            is_else = any((not c.is_named) and self._get_text(c, source_bytes) == 'else'
                          for c in entry.children)
            # The result is the last named child; conditions are the preceding ones.
            result_node = named[-1] if named else None
            cond_nodes = named[:-1]

            if is_else:
                # else branch: attach as final orelse.
                else_if = IfNode(LiteralNode(True), _branch_body(result_node), None)
                if prev_if is None:
                    # `when { else -> x }` degenerates to the body.
                    return _with_binding(else_if)
                prev_if.orelse = else_if
                continue

            # Combine multiple conditions with OR.
            conditions = [_condition_for(c) for c in cond_nodes] if cond_nodes else []
            if not conditions:
                condition = LiteralNode(True)
            else:
                condition = conditions[0]
                for extra in conditions[1:]:
                    condition = BinaryOpNode(condition, extra, "||")

            this_if = IfNode(condition, _branch_body(result_node), None)
            if root is None:
                root = this_if
            if prev_if is not None:
                prev_if.orelse = this_if
            prev_if = this_if

        return _with_binding(root if root is not None else IfNode(LiteralNode(True), [], None))

    def _make_range(self, kind: str, left, right):
        """Build a normalized range node.

        Represents Kotlin ranges (`a..b`, `a until b`, `a downTo b`,
        `<range> step n`) as a CallNode to the synthetic `__range__` symbol so
        the emitter can lower them to target-language loops/iterables. The
        `kind` metadata records inclusivity/direction/step.
        """
        if kind == "step":
            # `left` is already a range CallNode; attach the step operand.
            if isinstance(left, CallNode):
                left.metadata['range_step'] = right
                return left
            # Fallback: treat as inclusive range with step.
            node = CallNode(IdentifierNode("__range__"), [left, right])
            node.metadata['range_kind'] = '..'
            return node
        node = CallNode(IdentifierNode("__range__"), [left, right])
        node.metadata['range_kind'] = kind
        return node

    def _map_string_literal(self, node, source_bytes: bytes, scope: str = "main") -> URNode:
        """Map a Kotlin string_literal, preserving interpolations.

        Produces a LiteralNode whose `parts` is an ordered list of literal
        string segments (str) and embedded expression UR nodes. The emitter
        assembles these into a target-language interpolated string. A plain
        string (no interpolation) yields a simple LiteralNode(value).
        """
        parts = []           # list of str | URNode
        buf = ""             # accumulating literal text
        children = [c for c in node.children if c.type not in ('"', '"""')]

        i = 0
        while i < len(children):
            c = children[i]
            if c.type == 'interpolation':
                # ${ expr } — the single named child is the expression.
                expr_node = next((g for g in c.named_children), None)
                if buf:
                    parts.append(buf); buf = ""
                if expr_node is not None:
                    parts.append(self._map_node(expr_node, source_bytes, scope))
                i += 1
                continue

            text = self._get_text(c, source_bytes)
            if text == '$':
                # Simple `$name` / `$name.prop` form: the grammar emits a bare
                # `$` string_content, then the following string_content begins
                # with the interpolated identifier. Split it out.
                nxt = children[i + 1] if i + 1 < len(children) else None
                nxt_text = self._get_text(nxt, source_bytes) if nxt is not None else ""
                m = re.match(r'([A-Za-z_][A-Za-z0-9_]*)', nxt_text)
                if m:
                    ident = m.group(1)
                    if buf:
                        parts.append(buf); buf = ""
                    parts.append(IdentifierNode(ident))
                    remainder = nxt_text[len(ident):]
                    buf += remainder
                    i += 2
                    continue
                # Lone '$' with no identifier (e.g. literal dollar): keep it.
                buf += '$'
                i += 1
                continue

            buf += text
            i += 1

        if buf:
            parts.append(buf)

        # No interpolation: single literal segment.
        if len(parts) == 1 and isinstance(parts[0], str):
            return LiteralNode(parts[0])
        if not parts:
            return LiteralNode("")

        lit = LiteralNode(None)
        lit.parts = parts
        return lit

    def _absorb_body_members(self, body_node, source_bytes, scope, methods, fields, nested_classes=None):
        """Map every member of a `class_body` and route it into `methods` /
        `fields`. Shared by class_declaration, object_declaration,
        companion_object and object_literal. A nested `companion_object`
        member arrives as a marker ClassDefNode (`is_companion`); its already-
        static-tagged members are spliced into the enclosing class here.

        A nested `class Foo { ... }`/`object Foo { ... }` member also arrives
        as a (non-companion, non-object-literal) ClassDefNode. Dart has no
        nested-class syntax, so rather than silently discarding it (the
        previous behavior — it matched none of the branches below and was
        dropped, leaving call sites like `P(...)`/`D(...)` and `List<D>`
        dangling with no declaration at all), collect it into
        `nested_classes` when the caller supplies a list. The emitter hoists
        these to Dart top level alongside the enclosing class/object."""
        for child in body_node.named_children:
            mapped = self._map_node(child, source_bytes, scope)
            if mapped is None:
                continue
            if isinstance(mapped, ClassDefNode) and mapped.metadata.get('is_companion'):
                methods.extend(mapped.methods)
                fields.extend(mapped.fields)
            elif isinstance(mapped, ClassDefNode):
                if nested_classes is not None:
                    nested_classes.append(mapped)
            elif isinstance(mapped, FunctionDefNode):
                method = MethodDefNode(mapped.name, mapped.args, mapped.body, mapped.return_type)
                method.metadata = mapped.metadata
                methods.append(method)
            elif isinstance(mapped, MethodDefNode):
                methods.append(mapped)
            elif isinstance(mapped, AssignmentNode):
                fields.append(mapped)
            elif isinstance(mapped, list):
                for m in mapped:
                    if isinstance(m, AssignmentNode):
                        fields.append(m)

    def _body_has_var(self, body_node):
        """True if a `class_body` declares any mutable (`var`) property — the
        structural test that makes an `object` a stateful singleton rather than
        a bag of statics."""
        for child in body_node.named_children:
            if child.type == 'property_declaration':
                if any(gc.type == 'var' for gc in child.children):
                    return True
        return False

    def _delegation_base(self, ds, source_bytes):
        """The bare supertype name a `delegation_specifier` lists (generics /
        packages stripped)."""
        if ds.type != 'delegation_specifier':
            return None
        ci = next((c for c in ds.named_children if c.type == 'constructor_invocation'), None)
        ut = next((c for c in (ci or ds).named_children if c.type == 'user_type'), None)
        if ut is None:
            return None
        return self._get_text(ut, source_bytes).split('<')[0].strip().split('.')[-1]

    def _map_node(self, node, source_bytes: bytes, scope: str = "main") -> URNode:
        if node is None:
            return None

        if self.recorder is not None:
            self.recorder.record_seen(node)

        if node.type == 'source_file':
            body = []
            for child in node.named_children:
                mapped = self._map_node(child, source_bytes, scope)
                self._append_stmt(body, mapped)
            return ModuleNode(body)

        elif node.type == 'function_declaration':
            # name is usually an identifier child
            ident_node = next((c for c in node.named_children if c.type == 'identifier'), None)
            name = self._get_text(ident_node, source_bytes) if ident_node else ""

            new_scope = name if scope == "main" else f"{scope}.{name}"

            # Phase 3 sweep 7 (extension-function receiver lowering). A Kotlin
            # extension `fun T.f(args): R { ... this ... }` places the RECEIVER
            # type `T` as a `user_type`/`nullable_type` named child positioned
            # BEFORE the function-name node (verified against the actual
            # tree-sitter output — see the probe in this task: for
            # `fun MovementPattern.displayName(): String`, named_children are
            # [user_type 'MovementPattern', identifier(field=name) 'displayName',
            #  function_value_parameters, user_type 'String', function_body]).
            # A plain function has NO type node before the name. So the receiver
            # is the last type node whose position precedes the name node's.
            # `field_name_for_child` reliably marks the name node (field='name'),
            # which disambiguates it from the receiver type even when the
            # receiver is itself a `user_type` (`List<MuscleGroup>`) or a dotted
            # `com.sara...MovementPattern`. This receiver is NOT the return type;
            # the return type is grabbed separately below from the type node that
            # follows `function_value_parameters`.
            name_child_index = None
            for c in node.named_children:
                try:
                    fld = node.field_name_for_child(node.children.index(c))
                except Exception:
                    fld = None
                if fld == 'name':
                    name_child_index = node.named_children.index(c)
                    break
            extension_receiver = None
            if name_child_index is not None:
                for c in node.named_children[:name_child_index]:
                    if c.type in ('user_type', 'nullable_type'):
                        extension_receiver = self._get_text(c, source_bytes)

            modifiers_node = next((c for c in node.named_children if c.type == 'modifiers'), None)
            is_composable = False
            is_suspend = False
            if modifiers_node:
                for mod in modifiers_node.named_children:
                    if mod.type == 'annotation':
                        type_node = next((c for c in mod.named_children if c.type == 'user_type'), None)
                        if type_node and self._get_text(type_node, source_bytes) == "Composable":
                            is_composable = True
                        # Annotation args (Room `@Query("""...""")`, etc.) have no
                        # Dart equivalent and are never emitted, but their nested
                        # literals must still be *visited* for the coverage gate.
                        # Walk-and-discard: record_seen fires on every descendant,
                        # the mapped result is thrown away.
                        self._map_node(mod, source_bytes, new_scope)
                    elif mod.type == 'function_modifier' and self._get_text(mod, source_bytes) == 'suspend':
                        # Kotlin `suspend fun` -> Dart `Future<R> ... async`.
                        # This same function_declaration path is shared by
                        # top-level functions AND class methods (methods are
                        # mapped here then rewrapped as MethodDefNode in
                        # `_absorb_body_members`, which copies `.metadata`
                        # wholesale), so tagging it once here covers both.
                        is_suspend = True


            # return type. For an extension `fun T.f(...): R`, the receiver `T`
            # is ALSO a `user_type`/`nullable_type` sitting before the name, so
            # `next(... first type node ...)` would wrongly grab the receiver as
            # the return type. The return type is the type node that FOLLOWS the
            # `function_value_parameters` node. Anchor on the params node's
            # position (present for every real function decl; falls back to the
            # first type node when absent, preserving prior behavior for the
            # non-extension no-params edge case).
            params_pos = None
            for i, c in enumerate(node.named_children):
                if c.type == 'function_value_parameters':
                    params_pos = i
                    break
            if params_pos is not None:
                type_node = next(
                    (c for c in node.named_children[params_pos + 1:]
                     if c.type in ('user_type', 'nullable_type')),
                    None,
                )
            else:
                type_node = next((c for c in node.named_children if c.type in ('user_type', 'nullable_type')), None)
            return_type = self._get_text(type_node, source_bytes) if type_node else None

            # Phase 3 sweep 5 (method-return foundation): when this
            # `function_declaration` is a METHOD (declared inside a class or
            # interface body), `scope` here is the enclosing declaring type's
            # name — NOT `new_scope` (which is already `scope.name`, the
            # method's own scope for its params/locals). This is threaded in
            # by `_absorb_body_members`, which is called with the class/
            # interface's `new_scope` from the `class_declaration` branch and
            # passes it straight through as `scope` into `_map_node` for every
            # member, including this one. Top-level functions arrive with
            # `scope == "main"` and have no declaring type, so they are
            # skipped here — their return type already lives on
            # `func_node.metadata['type']` below, which is sufficient for
            # that case (only method calls on a receiver of known type need
            # this table; a bare top-level function call has no receiver to
            # resolve). Populating this table does not change any emission —
            # nothing currently reads `ledger.method_returns`.
            if name and scope != "main":
                self.ledger.register_method_return(
                    scope, name, return_type or 'void', is_suspend=is_suspend
                )

            args = []
            # Unit 09.9: parameter shape for this function/composable, keyed
            # by bare `name` and registered below. `has_default` reuses the
            # same "trailing non-ident/type child" default detection used for
            # data class fields at ~544 (a Kotlin parameter default is
            # `= expr` after the type). `is_trailing_lambda` is true only for
            # the LAST param when its type is a Kotlin function type
            # (contains `->`), mirroring Kotlin's trailing-lambda call syntax.
            param_shape = []
            params_node = next((c for c in node.named_children if c.type == 'function_value_parameters'), None)
            if params_node:
                # Grammar quirk (spot-checked against the actual tree-sitter
                # output, not assumed): `name: Type = default` does NOT nest
                # the default expression inside the `parameter` node — the
                # default-value expression is a SEPARATE named sibling
                # immediately following the `parameter` node in
                # `function_value_parameters`. So default-detection here
                # looks at the next sibling, not at extra children of `p`.
                all_children = list(params_node.named_children)
                param_positions = [i for i, c in enumerate(all_children) if c.type == 'parameter']
                for idx, pos in enumerate(param_positions):
                    p = all_children[pos]
                    p_ident = next((c for c in p.named_children if c.type == 'identifier'), None)
                    p_type = next((c for c in p.named_children if c.type in ('user_type', 'nullable_type')), None)
                    p_fn_type = next((c for c in p.named_children if c.type == 'function_type'), None)
                    # Phase 3 sweep 7 (vararg-as-List lowering). Kotlin
                    # `fun f(vararg c: T)` emits the `vararg` keyword as a
                    # `parameter_modifiers` sibling positioned IMMEDIATELY
                    # BEFORE the vararg `parameter` node (verified via probe:
                    # the FVP named_children are [..., parameter_modifiers>
                    # parameter_modifier>vararg, parameter 'c', ...]). Detect by
                    # inspecting the preceding sibling. A vararg param is lowered
                    # to a Dart `List<T> c` declaration (below, via the arg-node
                    # metadata) and its call sites splat/spread into a Dart list
                    # literal `[...]` (dart.py visit_CallNode, keyed off the
                    # is_vararg flag threaded onto param_shape's 5th element).
                    is_vararg = (
                        pos > 0
                        and all_children[pos - 1].type == 'parameter_modifiers'
                        and 'vararg' in self._get_text(all_children[pos - 1], source_bytes)
                    )
                    if p_ident and p_type:
                        ident_name = self._get_text(p_ident, source_bytes)
                        type_str = self._get_text(p_type, source_bytes)
                        self.ledger.register_type(new_scope, ident_name, type_str)
                    if p_ident:
                        arg_node = self._map_node(p_ident, source_bytes, new_scope)
                        if is_vararg:
                            # Tag the formal so the declaration emitter renders
                            # `List<ElementType> name`. The element type is the
                            # param's own declared type (`Float`->`double`,
                            # `AuthoredWeekNote` as-is); mapping happens in the
                            # emitter. The vararg is always Kotlin's LAST param.
                            arg_node.metadata['is_vararg'] = True
                            if p_type is not None:
                                arg_node.metadata['vararg_element_type'] = self._get_text(p_type, source_bytes)
                        args.append(arg_node)
                    if p_ident:
                        ident_name = self._get_text(p_ident, source_bytes)
                        type_node_for_shape = p_type or p_fn_type
                        type_str = self._get_text(type_node_for_shape, source_bytes) if type_node_for_shape else None
                        # The next sibling belongs to this parameter's default
                        # only if it is an actual default-value EXPRESSION node.
                        # Two other node types can sit between a parameter and
                        # the next one and must NOT be read as a default, or the
                        # preceding param is wrongly flagged `has_default=True`
                        # (which then lowers it to a Dart named param and drops
                        # its positional call args — the sweep-6 `week`/`blobPair`
                        # /`ex` corruption):
                        #   - `parameter_modifiers` (e.g. the `vararg` keyword,
                        #     which tree-sitter emits as a SEPARATE sibling
                        #     BEFORE the vararg parameter — so `week`'s
                        #     `workoutNote`, the param before `vararg notes`, was
                        #     mis-flagged; likewise `blobPair`'s `segR` before
                        #     `vararg c`).
                        #   - `line_comment` / `multiline_comment` (a comment
                        #     between two params — `ex`'s `movement` was
                        #     mis-flagged because a `//` comment sat between it
                        #     and `equipment`).
                        # So skip those sibling types; a default exists only if
                        # the FIRST following non-parameter, non-modifier,
                        # non-comment sibling appears before the next parameter.
                        next_pos = pos + 1
                        _skip_sib_types = (
                            'parameter_modifiers', 'line_comment', 'multiline_comment',
                        )
                        while (next_pos < len(all_children)
                               and all_children[next_pos].type in _skip_sib_types):
                            next_pos += 1
                        has_default = (
                            next_pos < len(all_children)
                            and all_children[next_pos].type != 'parameter'
                        )
                        # Capture the default EXPRESSION source text (sweep-2
                        # escalation 1) so the composable formal emission can
                        # emit `this.x = <default>` for const-safe defaults on
                        # non-nullable params (else `required this.x`). The
                        # default node is the sibling immediately after the
                        # parameter node when has_default is true.
                        default_text = (
                            self._get_text(all_children[next_pos], source_bytes)
                            if has_default else None
                        )
                        is_trailing_lambda = (idx == len(param_positions) - 1) and bool(type_str) and '->' in type_str
                        # Sweep 7: 5th element `is_vararg`. All existing consumers
                        # of param_shape use indexed access (p[0..3], guarded by
                        # `len(p) > 3`), never a strict 3/4-tuple unpack, so a 5th
                        # element is non-breaking (audited). Only the call-site
                        # collapse in dart.py reads p[4].
                        param_shape.append((ident_name, has_default, is_trailing_lambda, default_text, is_vararg))

            body = []
            body_node = next((c for c in node.named_children if c.type == 'function_body'), None)
            if body_node:
                # it's usually a block
                block_node = next((c for c in body_node.named_children if c.type == 'block'), None)
                if block_node:
                    for child in block_node.named_children:
                        mapped = self._map_node(child, source_bytes, new_scope)
                        self._append_stmt(body, mapped)
                else:
                    # Expression-bodied function: `fun f(): T = expr`. The
                    # expression is a direct named child of `function_body`
                    # (not wrapped in a `block`). Lower it to a return.
                    expr_node = next((c for c in body_node.named_children), None)
                    if expr_node is not None:
                        mapped_expr = self._map_node(expr_node, source_bytes, new_scope)
                        self._append_stmt(body, ReturnNode(mapped_expr))

            func_node = FunctionDefNode(name, args, body, return_type)
            if return_type:
                func_node.metadata['type'] = return_type
            if is_composable:
                func_node.metadata['is_composable'] = True
            if is_suspend:
                func_node.metadata['is_suspend'] = True
            if extension_receiver:
                # Phase 3 sweep 7: emitter lowers this to a Dart `extension on
                # <receiver> { ... }` so the body's `this` binds to the receiver
                # (a top-level Dart function has no `this` -> the prior
                # invalid_reference_to_this cluster). Copied wholesale into a
                # MethodDefNode by `_absorb_body_members` for member extensions,
                # so this single tag covers both top-level and member cases.
                func_node.metadata['extension_receiver'] = extension_receiver
            if name:
                self.ledger.register_param_shape(name, param_shape, file_scope=getattr(self, '_file_scope', None))
            return func_node

        elif node.type == 'class_declaration':
            ident_node = next((c for c in node.named_children if c.type == 'identifier'), None)
            name = self._get_text(ident_node, source_bytes) if ident_node else ""

            new_scope = name if scope == "main" else f"{scope}.{name}"

            bases = [] # TODO if needed

            methods = []
            fields = []

            # Enum detection: `enum class Foo(...)` carries a `class_modifier`
            # with text 'enum' under `modifiers`. Enum bodies use a distinct
            # `enum_class_body` node (not `class_body`), which the class_body
            # loop below never sees, so enum entries and any trailing members
            # were silently dropped, emitting empty `class Foo {}`.
            modifiers_node = next((c for c in node.named_children if c.type == 'modifiers'), None)
            is_enum = False
            is_data = False
            if modifiers_node:
                for mod in modifiers_node.named_children:
                    if mod.type == 'class_modifier' and self._get_text(mod, source_bytes) == 'enum':
                        is_enum = True
                    elif mod.type == 'class_modifier' and self._get_text(mod, source_bytes) == 'data':
                        is_data = True
                    elif mod.type == 'annotation':
                        # Walk-and-discard for coverage (see `annotation` branch).
                        self._map_node(mod, source_bytes, new_scope)

            # Primary constructor: `class Foo(val a: T, val b: U)`. tree-sitter
            # models this as a `primary_constructor` > `class_parameters` >
            # `class_parameter` chain. `val`/`var` parameters declare class
            # properties; without this they were dropped, leaving data classes
            # emitted as empty `class Foo {}` bodies (invalid where a body was
            # expected and breaking every construction site).
            data_fields = []
            # Unit 10.1: primary-constructor property params for NON-data
            # classes (see the is_prop branch below), so the emitter can
            # synthesize a constructor and make them locator-constructible.
            ctor_fields = []
            # Unit 09.9: parameter shape for the primary constructor, built
            # alongside the existing field-extraction loop (consumes the same
            # `default_node` detection at ~544, not duplicated). Registered
            # under the class name for BOTH data classes and regular classes
            # that declare a primary constructor.
            ctor_param_shape = []
            pc_node = next((c for c in node.named_children if c.type == 'primary_constructor'), None)
            if pc_node:
                params_node = next((c for c in pc_node.named_children if c.type == 'class_parameters'), None)
                if params_node:
                    for cp in params_node.named_children:
                        if cp.type != 'class_parameter':
                            continue
                        # A val/var keyword marks it as a declared property.
                        is_prop = any(gc.type in ('val', 'var') for gc in cp.children)
                        p_ident = next((c for c in cp.named_children if c.type == 'identifier'), None)
                        p_type = next((c for c in cp.named_children if c.type in ('user_type', 'nullable_type')), None)
                        default_node = cp.named_children[-1] if cp.named_children and cp.named_children[-1] is not p_ident and cp.named_children[-1] is not p_type else None
                        if p_ident:
                            ident_name = self._get_text(p_ident, source_bytes)
                            type_str = self._get_text(p_type, source_bytes) if p_type else None
                            if p_type:
                                self.ledger.register_type(new_scope, ident_name, type_str)
                            has_default = default_node is not None
                            is_trailing_lambda = bool(type_str) and '->' in type_str
                            ctor_param_shape.append((ident_name, has_default, is_trailing_lambda))
                            if is_prop:
                                default_val = self._map_node(default_node, source_bytes, new_scope) if default_node else None
                                fields.append(AssignmentNode(self._map_node(p_ident, source_bytes, new_scope), default_val))
                                if is_data:
                                    data_fields.append((ident_name, type_str))
                                else:
                                    # Unit 10.1: primary-constructor property
                                    # params of a NON-data class (repository /
                                    # @HiltViewModel with @Inject constructor,
                                    # e.g. UserRepository(userDao: UserDao,
                                    # timeProvider: TimeProvider)) become bare
                                    # fields above but, unlike data classes, no
                                    # constructor was synthesized — leaving
                                    # non-nullable fields uninitialized and the
                                    # class impossible to construct via the DI
                                    # locator. Record (name, type) here so the
                                    # emitter can synthesize a matching
                                    # constructor (see visit_ClassDefNode /
                                    # ctor_fields).
                                    ctor_fields.append((ident_name, type_str))

            nested_classes = []
            body_node = next((c for c in node.named_children if c.type == 'class_body'), None)
            if body_node:
                self._absorb_body_members(body_node, source_bytes, new_scope, methods, fields, nested_classes)

            enum_entries = []
            if is_enum:
                enum_body_node = next((c for c in node.named_children if c.type == 'enum_class_body'), None)
                if enum_body_node:
                    for child in enum_body_node.named_children:
                        if child.type == 'enum_entry':
                            # `_map_node` is not routed for structural extraction here (the
                            # entry has no standalone UR shape); call it purely so
                            # `record_seen` fires and the coverage recorder marks
                            # `enum_entry` as handled rather than unvisited.
                            self._map_node(child, source_bytes, new_scope)

                            entry_ident = next((c for c in child.named_children if c.type == 'identifier'), None)
                            entry_name = self._get_text(entry_ident, source_bytes) if entry_ident else ""

                            arg_nodes = []
                            val_args_node = next((c for c in child.named_children if c.type == 'value_arguments'), None)
                            if val_args_node:
                                for va in val_args_node.named_children:
                                    if va.type == 'value_argument' and va.named_children:
                                        mapped_arg = self._map_node(va.named_children[-1], source_bytes, new_scope)
                                        if mapped_arg is not None:
                                            arg_nodes.append(mapped_arg)

                            enum_entries.append((entry_name, arg_nodes))
                        elif child.type in ('function_declaration', 'property_declaration', 'companion_object', 'anonymous_initializer'):
                            mapped = self._map_node(child, source_bytes, new_scope)
                            if mapped is None:
                                continue
                            if isinstance(mapped, ClassDefNode) and mapped.metadata.get('is_companion'):
                                methods.extend(mapped.methods)
                                fields.extend(mapped.fields)
                            elif isinstance(mapped, FunctionDefNode):
                                method = MethodDefNode(mapped.name, mapped.args, mapped.body, mapped.return_type)
                                method.metadata = mapped.metadata
                                methods.append(method)
                            elif isinstance(mapped, MethodDefNode):
                                methods.append(mapped)
                            elif isinstance(mapped, AssignmentNode):
                                fields.append(mapped)
                            elif isinstance(mapped, list):
                                for m in mapped:
                                    if isinstance(m, AssignmentNode):
                                        fields.append(m)

            class_node = ClassDefNode(name, bases, methods, fields)
            if is_enum:
                class_node.metadata['is_enum'] = True
                class_node.metadata['enum_entries'] = enum_entries
            if is_data:
                class_node.metadata['is_data'] = True
                class_node.metadata['data_fields'] = data_fields
            elif ctor_fields:
                class_node.metadata['ctor_fields'] = ctor_fields
            if ctor_param_shape:
                self.ledger.register_param_shape(name, ctor_param_shape, file_scope=getattr(self, '_file_scope', None))
            if nested_classes:
                class_node.metadata['nested_classes'] = nested_classes
            return class_node

        elif node.type == 'object_declaration':
            # Kotlin singleton `object Foo { ... }`. Two lowerings, decided
            # structurally (never per-name): if the body declares any MUTABLE
            # property (a `var`), the object holds state and becomes a Dart
            # singleton (`class Foo { Foo._(); static final Foo instance = ...;
            # <instance members> }`); otherwise it is stateless and becomes a
            # class of `static` members (`class Foo { static ... }`). Either way
            # `Foo.bar` / `Foo.baz()` resolve — the emitter picks the form from
            # `metadata['object_singleton']`.
            ident_node = next((c for c in node.named_children if c.type == 'identifier'), None)
            name = self._get_text(ident_node, source_bytes) if ident_node else ""
            new_scope = name if scope == "main" else f"{scope}.{name}"

            modifiers_node = next((c for c in node.named_children if c.type == 'modifiers'), None)
            if modifiers_node:
                for mod in modifiers_node.named_children:
                    if mod.type == 'annotation':
                        # Walk-and-discard for coverage (@Module/@InstallIn etc.).
                        self._map_node(mod, source_bytes, new_scope)

            bases = []
            dss = next((c for c in node.named_children if c.type == 'delegation_specifiers'), None)
            if dss:
                for ds in dss.named_children:
                    ut = self._delegation_base(ds, source_bytes)
                    if ut:
                        bases.append(ut)

            methods = []
            fields = []
            nested_classes = []
            has_mutable_state = False
            body_node = next((c for c in node.named_children if c.type == 'class_body'), None)
            if body_node:
                has_mutable_state = self._body_has_var(body_node)
                self._absorb_body_members(body_node, source_bytes, new_scope, methods, fields, nested_classes)

            obj_node = ClassDefNode(name, bases, methods, fields)
            obj_node.metadata['is_object'] = True
            obj_node.metadata['object_singleton'] = has_mutable_state
            if has_mutable_state:
                # Stateful singleton: members emit as INSTANCE members reached
                # via `.instance`, so record the name for the egress call-site
                # rewrite `Name.member` -> `Name.instance.member`. Keyed purely
                # on the structural stateful-singleton test, never per-name.
                self.ledger.register_singleton_object(name)
            if nested_classes:
                obj_node.metadata['nested_classes'] = nested_classes
            return obj_node

        elif node.type == 'companion_object':
            # `companion object { ... }` inside a class. Its members become
            # `static` members of the enclosing class. The handler tags each
            # member `is_static` and returns a marker ClassDefNode; the enclosing
            # class-body loop (`_absorb_body_members`) splices the tagged members
            # into the enclosing class. A bare in-class reference to a companion
            # member resolves because the member is a plain static on the class.
            new_scope = f"{scope}.Companion" if scope != "main" else "Companion"
            methods = []
            fields = []
            cbody = next((c for c in node.named_children if c.type == 'class_body'), None)
            if cbody:
                self._absorb_body_members(cbody, source_bytes, new_scope, methods, fields)
            for m in methods:
                m.metadata['is_static'] = True
            for f in fields:
                f.metadata['is_static'] = True
            marker = ClassDefNode("Companion", [], methods, fields)
            marker.metadata['is_companion'] = True
            return marker

        elif node.type == 'anonymous_initializer':
            # `init { ... }` — the statements run in the constructor. Lowered to
            # a MethodDefNode carrying the block; the enclosing class-body loop
            # collects it and the emitter appends the statements to the (created
            # if absent) constructor body.
            body = []
            block_node = next((c for c in node.named_children if c.type == 'block'), None)
            if block_node:
                for child in block_node.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    self._append_stmt(body, mapped)
            init_node = MethodDefNode("__init_block__", [], body, None)
            init_node.metadata['is_init_block'] = True
            return init_node

        elif node.type == 'object_literal':
            # `object : Iface { ... }` — an anonymous object in expression
            # position. Dart has no anonymous classes. For a single-method
            # interface the whole object collapses to a Dart closure (the one
            # method's parameters + body). The ingestor records the shape;
            # the emitter renders single-method literals as closures. Multi-
            # member literals (needing a named private class) are flagged
            # `object_literal_multimember` for the emitter to handle/escalate.
            bases = []
            dss = next((c for c in node.named_children if c.type == 'delegation_specifiers'), None)
            super_args = []
            if dss:
                for ds in dss.named_children:
                    ut = self._delegation_base(ds, source_bytes)
                    if ut:
                        bases.append(ut)
                    ci = next((c for c in ds.named_children if c.type == 'constructor_invocation'), None)
                    if ci:
                        va = next((c for c in ci.named_children if c.type == 'value_arguments'), None)
                        if va:
                            for a in va.named_children:
                                if a.type == 'value_argument' and a.named_children:
                                    super_args.append(self._map_node(a.named_children[-1], source_bytes, scope))

            methods = []
            fields = []
            body_node = next((c for c in node.named_children if c.type == 'class_body'), None)
            if body_node:
                self._absorb_body_members(body_node, source_bytes, scope, methods, fields)

            lit = ClassDefNode("", bases, methods, fields)
            lit.metadata['is_object_literal'] = True
            lit.metadata['super_args'] = super_args
            # Strip `override` no-op; a single method + no fields => closure form.
            lit.metadata['single_method'] = (len(methods) == 1 and not fields)
            return lit

        elif node.type == 'secondary_constructor':
            args = []
            params_node = next((c for c in node.named_children if c.type == 'function_value_parameters'), None)
            if params_node:
                for p in params_node.named_children:
                    if p.type == 'parameter':
                        p_ident = next((c for c in p.named_children if c.type == 'identifier'), None)
                        p_type = next((c for c in p.named_children if c.type in ('user_type', 'nullable_type')), None)
                        if p_ident and p_type:
                            ident_name = self._get_text(p_ident, source_bytes)
                            type_str = self._get_text(p_type, source_bytes)
                            self.ledger.register_type(scope, ident_name, type_str)
                        if p_ident:
                            args.append(self._map_node(p_ident, source_bytes, scope))

            body = []
            block_node = next((c for c in node.named_children if c.type == 'block'), None)
            if block_node:
                for child in block_node.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    self._append_stmt(body, mapped)
            return MethodDefNode("__init__", args, body, None)

        elif node.type == 'property_declaration':
            # Walk-and-discard any annotations for coverage (see `annotation`
            # branch) — e.g. `@JvmField`/Room column annotations on properties.
            prop_modifiers_node = next((c for c in node.named_children if c.type == 'modifiers'), None)
            if prop_modifiers_node:
                for mod in prop_modifiers_node.named_children:
                    if mod.type == 'annotation':
                        self._map_node(mod, source_bytes, scope)

            # Destructuring declaration: `val (a, b) = expr`. tree-sitter
            # substitutes a `multi_variable_declaration` for the plain
            # `variable_declaration` child. Contract with the emitter: an
            # AssignmentNode with `.left = None`, `.right = <mapped RHS>`, and
            # `.metadata['destructure'] = [names...]`.
            multi_decl = next((c for c in node.named_children if c.type == 'multi_variable_declaration'), None)
            if multi_decl is not None:
                self._map_node(multi_decl, source_bytes, scope)  # register as seen
                names = []
                for vd in multi_decl.named_children:
                    if vd.type != 'variable_declaration':
                        continue
                    vd_ident = next((c for c in vd.named_children if c.type == 'identifier'), None)
                    if vd_ident:
                        names.append(self._get_text(vd_ident, source_bytes))

                right_node = None
                for c in node.named_children:
                    if c is not multi_decl:
                        right_node = c
                right = self._map_node(right_node, source_bytes, scope) if right_node is not None else None

                assign = AssignmentNode(None, right)
                assign.metadata['destructure'] = names
                return assign

            var_decl = next((c for c in node.named_children if c.type == 'variable_declaration'), None)
            ident_node = next((c for c in var_decl.named_children if c.type == 'identifier'), None) if var_decl else None
            type_node = next((c for c in var_decl.named_children if c.type in ('user_type', 'nullable_type')), None) if var_decl else None
            
            left = None
            if ident_node:
                ident_name = self._get_text(ident_node, source_bytes)
                if type_node:
                    type_str = self._get_text(type_node, source_bytes)
                    self.ledger.register_type(scope, ident_name, type_str)
                left = self._map_node(ident_node, source_bytes, scope)

            # right side is the last named child of property_declaration if it is an expression
            right = None
            if len(node.named_children) > 1:
                # Usually it's the last child like number_literal, string_literal, property_delegate, etc.
                right_node = node.named_children[-1]
                if right_node.type == 'property_delegate':
                    delegate_expr = next((c for c in right_node.named_children), None)
                    if delegate_expr:
                        right = self._map_node(delegate_expr, source_bytes, scope)
                        if left:
                            left.metadata['is_delegate'] = True
                elif right_node.type != 'variable_declaration':
                    right = self._map_node(right_node, source_bytes, scope)
            
            if left and right:
                hoisted = self._hoist_binding_rhs(left, right)
                if hoisted is not None:
                    return hoisted
                lowered = self._lower_elvis_control_flow(left, right)
                if lowered is not None:
                    return lowered
                return AssignmentNode(left, right)
            return None

        elif node.type == 'assignment':
            if len(node.named_children) >= 2:
                left = self._map_node(node.named_children[0], source_bytes, scope)
                right = self._map_node(node.named_children[1], source_bytes, scope)
                hoisted = self._hoist_binding_rhs(left, right)
                if hoisted is not None:
                    return hoisted
                lowered = self._lower_elvis_control_flow(left, right)
                if lowered is not None:
                    return lowered
                return AssignmentNode(left, right)
            return None

        elif node.type == 'return_expression':
            # Unlabeled: children are (`return`, [value]).
            # Labeled (`return@label [value]`): children are
            # (`return@`, label-identifier, [value]) — the label identifier
            # is itself a *named* child, so it must not be mistaken for the
            # returned value. A `return@label` names the lambda/function
            # being returned from; Dart's bare `return` inside a closure
            # already returns from the innermost closure, so the label is
            # dropped and only the trailing value (if any) is kept.
            is_labeled = any(
                (not c.is_named) and self._get_text(c, source_bytes) == 'return@'
                for c in node.children
            )
            value_nodes = node.named_children[1:] if is_labeled else node.named_children
            if value_nodes:
                value = self._map_node(value_nodes[0], source_bytes, scope)
                return ReturnNode(value)
            return ReturnNode(None)

        elif node.type == 'labeled_expression':
            # `label@{ ... }` (most commonly a labeled lambda literal used so
            # that `return@label` inside it has a target). Dart has no
            # equivalent to a label on an expression/lambda, so unwrap to the
            # inner expression and discard the label entirely.
            inner = next(
                (c for c in node.named_children if c.type != 'label'),
                None,
            )
            if inner is None and node.named_children:
                inner = node.named_children[-1]
            return self._map_node(inner, source_bytes, scope)

        elif node.type == 'binary_expression':
            if len(node.named_children) == 2:
                left_node = node.named_children[0]
                right_node = node.named_children[1]
                # Find the operator text from source bytes since unnamed child is the operator
                op_node = None
                for child in node.children:
                    if not child.is_named:
                        op_node = child
                        break
                operator = self._get_text(op_node, source_bytes).strip() if op_node else ""
                
                left = self._map_node(left_node, source_bytes, scope)
                right = self._map_node(right_node, source_bytes, scope)
                return BinaryOpNode(left, right, operator)
            return None
            
        elif node.type == 'prefix_expression' or node.type == 'unary_expression':
            op_node = next((c for c in node.children if not c.is_named), None)
            operator = self._get_text(op_node, source_bytes).strip() if op_node else ""
            if operator == '!':
                arg_node = node.named_children[0] if node.named_children else None
                arg = self._map_node(arg_node, source_bytes, scope) if arg_node else None
                return BinaryOpNode(IdentifierNode(""), arg, "!")
            elif operator == '-':
                arg_node = node.named_children[0] if node.named_children else None
                arg = self._map_node(arg_node, source_bytes, scope) if arg_node else None
                return BinaryOpNode(IdentifierNode(""), arg, "-")
            elif operator == '!!':
                # Kotlin non-null assertion `x!!` -> Dart `x!`.
                arg_node = node.named_children[0] if node.named_children else None
                arg = self._map_node(arg_node, source_bytes, scope) if arg_node else None
                return BinaryOpNode(arg, IdentifierNode(""), "!!")
            elif operator in ('++', '--'):
                # Pre/postfix increment. Determine position from child order.
                arg_node = node.named_children[0] if node.named_children else None
                arg = self._map_node(arg_node, source_bytes, scope) if arg_node else None
                # If the operator token precedes the operand it is prefix.
                is_prefix = op_node is not None and (arg_node is None or op_node.start_byte < arg_node.start_byte)
                if is_prefix:
                    return BinaryOpNode(IdentifierNode(""), arg, operator)
                return BinaryOpNode(arg, IdentifierNode(""), operator)
            return None

        elif node.type == 'call_expression':
            ident_node = next((c for c in node.named_children if c.type in ('identifier', 'navigation_expression', 'call_expression')), None)
            lambda_node = next((c for c in node.named_children if c.type in ('annotated_lambda', 'lambda_literal')), None)
            
            if ident_node and ident_node.type == 'call_expression':
                base_call = ident_node
                real_ident = next((c for c in base_call.named_children if c.type in ('identifier', 'navigation_expression')), None)
                func_name = self._map_node(real_ident, source_bytes, scope) if real_ident else IdentifierNode("")
                
                # Non-declarative curried call: Kotlin's trailing-lambda sugar
                # on a call whose callee is itself a call, e.g.
                # `combine(a, b) { ... }` or `withContext(ctx) { ... }`, parses
                # as call_expression(call_expression(f, inner_args), lambda).
                # Fold this into a single CallNode(f, inner_args + [lambda])
                # instead of returning CallNode(CallNode(f, inner_args), [lambda]),
                # which would emit as the invalid curried `f(args)(lambda)`.
                inner_args = []
                val_args_node = next((c for c in base_call.named_children if c.type == 'value_arguments'), None)
                if val_args_node:
                    for child in val_args_node.named_children:
                        if child.type == 'value_argument':
                            value_node = child.named_children[-1] if child.named_children else child
                            mapped = self._map_node(value_node, source_bytes, scope)
                            if mapped:
                                inner_args.append(mapped)
                if lambda_node:
                    mapped_lambda = self._map_node(lambda_node, source_bytes, scope)
                    if mapped_lambda:
                        # `with(receiver) { ... }` curries here: `func_name` is
                        # the bare identifier "with", and the receiver is the
                        # single already-mapped inner_args[0] (a variable, not
                        # a constructor call — `with` operates on an EXISTING
                        # value, unlike `.apply`/`.also`/`.run` which chain off
                        # a fresh `X()`). Resolve its type the same way: a bare
                        # IdentifierNode with a ledger-known type, or a
                        # CallNode(IdentifierNode(X), ...) constructor result.
                        if (
                            isinstance(func_name, IdentifierNode)
                            and func_name.name == "with"
                            and inner_args
                        ):
                            recv = inner_args[0]
                            ctor_name = None
                            if isinstance(recv, CallNode) and isinstance(recv.func_name, IdentifierNode):
                                ctor_name = recv.func_name.name
                            elif isinstance(recv, IdentifierNode):
                                ctor_name = recv.metadata.get('type') or None
                            receiver_type = self._scope_fn_receiver_type(ctor_name)
                            mapped_lambda.metadata['scope_fn'] = {
                                'kind': 'with',
                                'receiver_type': receiver_type,
                            }
                            if not mapped_lambda.args:
                                mapped_lambda.args = [IdentifierNode("it")]
                        else:
                            self._tag_scope_fn_lambda(func_name, mapped_lambda)
                        if self._is_coroutine_builder(func_name):
                            mapped_lambda.metadata['async_builder_callback'] = True
                        inner_args.append(mapped_lambda)
                return CallNode(func_name, inner_args)

            func_name = self._map_node(ident_node, source_bytes, scope) if ident_node else IdentifierNode("")
            
            # Named-argument preservation: capture a source `name = value`
            # call-argument prefix for EVERY call (not just `.copy(...)`),
            # tagging it on the mapped arg node as `metadata['arg_name']`.
            # This used to be scoped to `.copy(...)` calls only (the
            # synthesized data-class `copy` method is the only callee
            # guaranteed to have matching named params in emitted Dart), out
            # of concern that broadly preserving names would emit `name:
            # value` against callees whose Dart signatures are still
            # positional. That concern is now handled on the EMIT side
            # instead: `dart.py`'s plain-function definition emitter lowers
            # Kotlin default-valued params to Dart named-optional params
            # (mirroring the existing composable-constructor `param_shape`
            # machinery), so a callee's Dart signature now has named params
            # wherever its Kotlin source had default-valued params — exactly
            # the params whose call sites use `name =` syntax (Kotlin
            # requires named syntax to skip defaulted middle params). So it
            # is now safe, and necessary, to capture `arg_name` unconditionally
            # here; whether it actually gets emitted as `name: value` vs
            # positional is decided at the call site in dart.py by whether
            # the callee's known param_shape marks that param `has_default`.
            args = []
            val_args_node = next((c for c in node.named_children if c.type == 'value_arguments'), None)
            if val_args_node:
                for child in val_args_node.named_children:
                    if child.type == 'value_argument':
                        arg_ident = next((c for c in child.named_children if c.type == 'identifier'), None)
                        # A bare identifier that is itself the sole child is the
                        # value, not a `name =` prefix; only treat it as a name
                        # prefix when a further value node follows it.
                        if arg_ident is not None and len(child.named_children) < 2:
                            arg_ident = None
                        value_node = child.named_children[-1] if child.named_children else child
                        mapped = self._map_node(value_node, source_bytes, scope)
                        if mapped:
                            if arg_ident is not None:
                                mapped.metadata['arg_name'] = self._get_text(arg_ident, source_bytes)
                            args.append(mapped)
                            
            if lambda_node:
                mapped_lambda = self._map_node(lambda_node, source_bytes, scope)
                if mapped_lambda:
                    self._tag_scope_fn_lambda(func_name, mapped_lambda)
                    if self._is_coroutine_builder(func_name):
                        mapped_lambda.metadata['async_builder_callback'] = True
                    args.append(mapped_lambda)

            return CallNode(func_name, args)

        elif node.type == 'identifier':
            name = self._get_text(node, source_bytes)
            ident_node = IdentifierNode(name)
            ledger_type = self.ledger.get_type(scope, name)
            if ledger_type:
                ident_node.metadata['type'] = ledger_type
            return ident_node

        elif node.type == 'null_literal' or self._get_text(node, source_bytes) == 'null':
            return IdentifierNode("null")
            
        elif node.type == 'this_expression':
            return IdentifierNode("self")

        elif node.type == 'super_expression':
            return IdentifierNode("super")

        elif node.type == 'character_literal':
            # Kotlin Char literal. Dart has no char type; the equivalent value
            # is a single-character String. Preserve the inner text (already
            # single-quoted) so escapes like '\n' / '\'' survive.
            text = self._get_text(node, source_bytes)
            inner = text[1:-1] if len(text) >= 2 else text
            # Emit as a Dart double-quoted string literal.
            lit = LiteralNode(None)
            if inner == '"':
                lit.raw = True
                lit.value = "'\"'"
            else:
                lit.raw = True
                lit.value = '"' + inner + '"'
            return lit

        elif node.type in ('integer_literal', 'number_literal'):
            value_str = self._get_text(node, source_bytes)
            try:
                value = int(value_str)
            except ValueError:
                value = float(value_str) if '.' in value_str else value_str
            return LiteralNode(value)

        elif node.type in ('float_literal', 'double_literal'):
            value_str = self._get_text(node, source_bytes).rstrip('fF')
            return LiteralNode(float(value_str))

        elif node.type == 'string_literal':
            return self._map_string_literal(node, source_bytes, scope)

        elif node.type == 'multiline_string_literal':
            # `"""..."""` — same interpolation model as `string_literal`;
            # `_map_string_literal` strips both `"` and `"""` delimiter tokens.
            # A Kotlin raw string can contain literal newlines; a Dart single-
            # quoted string cannot. Tag the literal so the emitter wraps it in a
            # Dart triple-quoted string (`"""..."""`), which permits newlines.
            lit = self._map_string_literal(node, source_bytes, scope)
            if isinstance(lit, LiteralNode):
                lit.metadata['multiline'] = True
            return lit

        elif node.type == 'collection_literal':
            # `[ elem, elem, ... ]` (Kotlin annotation-array / arrayOf-like
            # literal). Children are expressions separated by anonymous commas.
            elements = [self._map_node(c, source_bytes, scope) for c in node.named_children]
            return ListNode([e for e in elements if e is not None])

        elif node.type == 'spread_expression':
            # `*expr` (spread into vararg) -> Dart `...expr`. The emitter
            # special-cases a call to the synthetic `__spread__` symbol to
            # render the `...` prefix.
            inner_node = next((c for c in node.named_children), None)
            inner = self._map_node(inner_node, source_bytes, scope) if inner_node is not None else None
            return CallNode(IdentifierNode("__spread__"), [inner] if inner is not None else [])

        elif node.type == 'enum_entry':
            # Consumed structurally by the `class_declaration` handler (name +
            # value_arguments extracted directly from the raw node). This
            # branch exists purely so `record_seen` fires when reached and the
            # coverage recorder does not report it as unvisited/dropped.
            return None

        elif node.type == 'annotation':
            # `@Database(entities = [...])`, `@Query("""SQL""")`, etc. — Kotlin
            # annotation arguments are compile-time-only metadata (Room schema,
            # SQL) with no Dart equivalent, so nothing is emitted. But their
            # nested literals (`collection_literal`, `multiline_string_literal`)
            # must still be *visited* for the coverage gate. Walk the
            # constructor invocation's value_arguments purely to record_seen on
            # descendants, then discard every mapped result.
            invocation = next((c for c in node.named_children if c.type == 'constructor_invocation'), None)
            if invocation is not None:
                val_args_node = next((c for c in invocation.named_children if c.type == 'value_arguments'), None)
                if val_args_node:
                    for va in val_args_node.named_children:
                        if va.type == 'value_argument':
                            for child in va.named_children:
                                self._map_node(child, source_bytes, scope)
            return None

        elif node.type == 'multi_variable_declaration':
            # `(a, b)` destructuring target. Consumed structurally by the
            # `property_declaration` and `for_statement` handlers (names read
            # directly off the raw node). This branch exists purely so
            # `record_seen` fires when reached.
            return None

        elif node.type == 'boolean_literal':
            value_str = self._get_text(node, source_bytes)
            return LiteralNode(value_str == 'true')

        elif node.type == 'if_expression':
            condition_node = next((c for c in node.children if c.type == 'parenthesized_expression'), None)
            if not condition_node and node.named_children:
                condition_node = node.named_children[0]

            condition = self._map_node(condition_node, source_bytes, scope) if condition_node else None

            remaining_children = [c for c in node.named_children if c is not condition_node]
            then_node = remaining_children[0] if len(remaining_children) > 0 else None
            else_node = remaining_children[1] if len(remaining_children) > 1 else None

            def _map_branch(branch_node):
                mapped_children = []
                if branch_node is None:
                    return mapped_children
                if branch_node.type == 'block':
                    for child in branch_node.named_children:
                        mapped = self._map_node(child, source_bytes, scope)
                        self._append_stmt(mapped_children, mapped)
                else:
                    mapped = self._map_node(branch_node, source_bytes, scope)
                    self._append_stmt(mapped_children, mapped)
                return mapped_children

            body = _map_branch(then_node)

            orelse = None
            if else_node is not None:
                if else_node.type == 'if_expression':
                    orelse = self._map_node(else_node, source_bytes, scope)
                else:
                    orelse_body = _map_branch(else_node)
                    orelse = IfNode(LiteralNode(True), orelse_body, None)

            return IfNode(condition, body, orelse)

        elif node.type == 'when_expression':
            return self._map_when(node, source_bytes, scope)

        elif node.type == 'while_statement':
            # tree-sitter-kotlin does not wrap the while condition in a
            # parenthesized_expression: the condition is the first named child
            # that is not the loop body block.
            condition_node = next(
                (c for c in node.named_children
                 if c.type not in ('block', 'parenthesized_expression')),
                None,
            )
            if condition_node is None:
                paren = next((c for c in node.named_children if c.type == 'parenthesized_expression'), None)
                condition_node = paren
            condition = self._map_node(condition_node, source_bytes, scope) if condition_node else None
            
            body = []
            block_node = next((c for c in node.named_children if c.type == 'block'), None)
            if block_node:
                for child in block_node.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    self._append_stmt(body, mapped)
            return WhileNode(condition, body)

        elif node.type == 'for_statement':
            target_node = next(
                (c for c in node.named_children
                 if c.type in ('variable_declaration', 'identifier', 'multi_variable_declaration')),
                None,
            )
            target = None
            destructure_names = None
            if target_node:
                if target_node.type == 'multi_variable_declaration':
                    # `for ((k, v) in map)` destructuring target. Contract with
                    # the emitter: `ForNode.target = None`, and
                    # `.metadata['destructure'] = [names...]`.
                    self._map_node(target_node, source_bytes, scope)  # register as seen
                    destructure_names = []
                    for vd in target_node.named_children:
                        if vd.type != 'variable_declaration':
                            continue
                        vd_ident = next((c for c in vd.named_children if c.type == 'identifier'), None)
                        if vd_ident:
                            destructure_names.append(self._get_text(vd_ident, source_bytes))
                elif target_node.type == 'variable_declaration':
                    ident = next((c for c in target_node.named_children if c.type == 'identifier'), None)
                    target = self._map_node(ident, source_bytes, scope) if ident else None
                else:
                    target = self._map_node(target_node, source_bytes, scope)

            # Kotlin "for (x in iter)" has 'in_expression' or something?
            # Actually, the children of for_statement are usually parameter/variable_declaration and the iterable expression
            # Wait, `for (k in (1 until 6))`
            # The second named child is usually the iterable.
            iter_mapped = None
            if len(node.named_children) > 1:
                # The 2nd child is the iterable
                iter_mapped = self._map_node(node.named_children[1], source_bytes, scope)

            body = []
            block_node = next((c for c in node.named_children if c.type == 'block'), None)
            if block_node:
                for child in block_node.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    self._append_stmt(body, mapped)
            for_node = ForNode(target, iter_mapped, body)
            if destructure_names is not None:
                for_node.metadata['destructure'] = destructure_names
            return for_node

        elif node.type == 'try_expression':
            body = []
            blocks = [c for c in node.named_children if c.type == 'block']
            if len(blocks) > 0:
                for child in blocks[0].named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    self._append_stmt(body, mapped)
            
            handlers = []
            catch_node = next((c for c in node.named_children if c.type == 'catch_block'), None)
            if catch_node:
                catch_block = next((c for c in catch_node.named_children if c.type == 'block'), None)
                if catch_block:
                    for child in catch_block.named_children:
                        mapped = self._map_node(child, source_bytes, scope)
                        if mapped:
                            handlers.append(mapped)

            return TryCatchNode(body, handlers)

        elif node.type == 'throw_expression':
            exc = None
            if node.named_children:
                exc = self._map_node(node.named_children[0], source_bytes, scope)
            return CallNode("throw", [exc]) if exc else CallNode("throw", [])

        elif node.type == 'navigation_expression': # e.g. a.b
            # A line/multiline comment between the receiver and the `.member`
            # (e.g. a comment above a `.filterNot { }` in a call chain) is a
            # named child of the navigation. Skip comments so the property is
            # the real member identifier, not the comment text (which otherwise
            # emitted as `.// comment(...)` and broke the call chain).
            nav_children = [
                c for c in node.named_children
                if c.type not in ('line_comment', 'multiline_comment')
            ]
            obj_node = nav_children[0] if len(nav_children) > 0 else None
            prop_node = nav_children[1] if len(nav_children) > 1 else None

            obj = self._map_node(obj_node, source_bytes, scope) if obj_node else None
            attr = self._get_text(prop_node, source_bytes) if prop_node else ""

            # `X::class` is a Kotlin class reference; tree-sitter models it as a
            # navigation whose member is the `class` keyword. Dart has no `::`
            # reflection operator and `class` is a reserved word, so `X.class`
            # will not parse. The minimal structural equivalent is the type
            # itself as a first-class value: reduce `X::class` to the type
            # reference `X`. Any following `.java`/`.kotlin`/`.simpleName`
            # projection then chains onto `X` naturally.
            if attr == 'class':
                return obj

            return AttributeNode(obj, attr)

        elif node.type == 'index_expression': # e.g. a[b]
            value_node = node.named_children[0] if len(node.named_children) > 0 else None
            slice_node = node.named_children[1] if len(node.named_children) > 1 else None
            
            value = self._map_node(value_node, source_bytes, scope) if value_node else None
            slice_mapped = self._map_node(slice_node, source_bytes, scope) if slice_node else None
            return SubscriptNode(value, slice_mapped)

        elif node.type == 'infix_expression':
            # tree-sitter-kotlin models `a OP b` as three named children:
            # [left, operator_identifier, right]. The operator is a named
            # `identifier`/`simple_identifier` node in the middle, NOT an
            # anonymous child, so it must be read from named_children[1] and
            # the real RHS from named_children[2].
            named = node.named_children
            left = self._map_node(named[0], source_bytes, scope) if len(named) > 0 else None
            operator = self._get_text(named[1], source_bytes).strip() if len(named) > 1 else ""
            right = self._map_node(named[2], source_bytes, scope) if len(named) > 2 else None

            if operator in ("until", "downTo", "step"):
                return self._make_range(operator, left, right)
            return BinaryOpNode(left, right, operator)

        elif node.type == 'range_expression':
            # Kotlin `a..b` (inclusive IntRange).
            named = node.named_children
            left = self._map_node(named[0], source_bytes, scope) if len(named) > 0 else None
            right = self._map_node(named[1], source_bytes, scope) if len(named) > 1 else None
            return self._make_range("..", left, right)

        elif node.type == 'parenthesized_expression':
            if node.named_children:
                return self._map_node(node.named_children[0], source_bytes, scope)
            return None
            
        elif node.type == 'annotated_expression':
            # `@OptIn(...) expr` — annotations are compile-time only; unwrap to
            # the underlying expression (the last non-annotation named child).
            annotation_node = next(
                (c for c in node.named_children if c.type == 'annotation'),
                None,
            )
            expr_node = next(
                (c for c in reversed(node.named_children) if c.type != 'annotation'),
                None,
            )
            # A declaration-level annotation with parenthesized arguments — e.g.
            # `@InstallIn(SingletonComponent::class)` on a top-level interface —
            # is parsed as `annotated_expression[annotation, parenthesized_expr]`
            # where the parenthesized node is the ANNOTATION'S OWN argument list
            # (the `annotation` node carries no `value_arguments` of its own),
            # not a guarded expression. Emitting it leaked a bare
            # `SingletonComponent;` statement. Annotation arguments are
            # compile-time metadata only, so drop the whole node in that case.
            if (
                annotation_node is not None
                and expr_node is not None
                and expr_node.type == 'parenthesized_expression'
                and not any(
                    c.type == 'value_arguments'
                    for c in annotation_node.named_children
                )
            ):
                return None
            return self._map_node(expr_node, source_bytes, scope) if expr_node else None

        elif node.type == 'callable_reference':
            # Kotlin `::name` (unbound) -> Dart tear-off `name`.
            # Kotlin `recv::name` -> Dart `recv.name`.
            named = node.named_children
            if len(named) >= 2:
                recv = self._get_text(named[0], source_bytes)
                name = self._get_text(named[1], source_bytes)
                return IdentifierNode(f"{recv}.{name}")
            elif named:
                return IdentifierNode(self._get_text(named[0], source_bytes))
            return IdentifierNode(self._get_text(node, source_bytes).lstrip(':'))

        elif node.type == 'is_expression': # e.g. outcome is Foo.Bar
            named = node.named_children
            left = self._map_node(named[0], source_bytes, scope) if len(named) > 0 else None
            # RHS is a type node; keep its source text as the type identifier.
            type_text = self._get_text(named[1], source_bytes) if len(named) > 1 else ""
            # Detect negation `!is` via anonymous children.
            op_text = "".join(
                self._get_text(c, source_bytes) for c in node.children if not c.is_named
            )
            operator = "!is" if "!is" in op_text else "is"
            return BinaryOpNode(left, IdentifierNode(type_text), operator)

        elif node.type == 'as_expression': # e.g. pair[0] as String
            if node.named_children:
                return self._map_node(node.named_children[0], source_bytes, scope)
            return None
            
        elif node.type == 'in_expression': # e.g. "quickfox" in words
            # Treat as BinaryOpNode with operator 'in'
            if len(node.named_children) == 2:
                left = self._map_node(node.named_children[0], source_bytes, scope)
                right = self._map_node(node.named_children[1], source_bytes, scope)
                return BinaryOpNode(left, right, "in")
            return None

        elif node.type in ('lambda_literal', 'annotated_lambda'):
            # Lambda params: explicit `{ i -> ... }` declares them via a
            # `lambda_parameters` child on the `lambda_literal` (for
            # `annotated_lambda`, the real `lambda_literal` is a child — find
            # it so params come from there, not from the wrapper). With no
            # explicit params, Kotlin implicitly binds a bare `it`; scan the
            # lambda body's source text for a `\bit\b` reference and, if
            # present, declare `it` as the sole parameter so the Dart closure
            # isn't emitted with an undefined identifier.
            lambda_lit = node if node.type == 'lambda_literal' else next(
                (c for c in node.named_children if c.type == 'lambda_literal'), None
            )
            block = next((c for c in node.named_children if c.type in ('lambda_literal', 'block')), node)

            args = []
            params_node = next((c for c in lambda_lit.named_children if c.type == 'lambda_parameters'), None) if lambda_lit else None
            if params_node:
                for vd in params_node.named_children:
                    if vd.type == 'multi_variable_declaration':
                        # Destructuring lambda param: `{ (a, b) -> ... }`
                        # (also seen with a `_` discard slot, e.g.
                        # `{ (_, coverage) -> ... }`). Same contract as the
                        # `val (a, b) = expr` and `for ((k, v) in map)` cases
                        # above/below: a synthetic single IdentifierNode arg
                        # standing in for the whole tuple, tagged with
                        # `.metadata['destructure'] = [names...]` so the
                        # emitter (dart.py) can bind the real names from it
                        # at the top of the lambda body.
                        names = []
                        for inner_vd in vd.named_children:
                            if inner_vd.type != 'variable_declaration':
                                continue
                            inner_ident = next((c for c in inner_vd.named_children if c.type == 'identifier'), None)
                            if inner_ident:
                                names.append(self._get_text(inner_ident, source_bytes))
                        synth = IdentifierNode("_destructured")
                        synth.metadata['destructure'] = names
                        args.append(synth)
                        continue
                    if vd.type != 'variable_declaration':
                        continue
                    p_ident = next((c for c in vd.named_children if c.type == 'identifier'), None)
                    if p_ident:
                        args.append(IdentifierNode(self._get_text(p_ident, source_bytes)))
            elif lambda_lit is not None:
                lambda_text = self._get_text(lambda_lit, source_bytes)
                if re.search(r'\bit\b', lambda_text):
                    args = [IdentifierNode("it")]

            body = []
            if block:
                for child in block.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    self._append_stmt(body, mapped)
            return FunctionDefNode("lambda", args, body, None)

        # Ignore imports for UR-AST as per typical transpiler mapping
        elif node.type == 'import_list' or node.type == 'import':
            return None

        else:
            # No branch matched: this node type has no handler. Record it as a
            # drop so the coverage gate surfaces it as work for Tasks 07-10.
            if self.recorder is not None:
                self.recorder.record_dropped(node)
            return None
