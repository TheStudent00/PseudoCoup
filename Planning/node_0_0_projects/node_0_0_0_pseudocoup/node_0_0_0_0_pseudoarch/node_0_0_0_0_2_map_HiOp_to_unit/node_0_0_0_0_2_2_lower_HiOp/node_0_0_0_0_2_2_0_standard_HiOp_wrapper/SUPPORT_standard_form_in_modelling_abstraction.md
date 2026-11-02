---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.standard_HiOp_wrapper.support.standard_form_in_modelling_abstraction
status: draft
---

# SUPPORT — standard_form_in_modelling_abstraction

The standard-form in the context of modelling abstraction, as its
configurations. Third draft, 2026-10-10. Not literal. For the owner to build on.

- `placeholder_k()`: inert. It stands for whatever code a program puts there.
- `HiOp[k](...)`: part k of one HiOp (the owner's notation, 2026-10-10). `(...)` is
  what the part takes, such as a test; the line indented under it is the
  part's body.
- depended-HiOp: the HiOp that is depended on. dependent-HiOp: a HiOp that
  depends on a depended-HiOp (the owner's words). A loop is a depended-HiOp; the
  `break;` inside it is a dependent-HiOp.

## 1. a HiOp with N bodies

```
placeholder_0()
HiOp[0](...):
    placeholder_1()
HiOp[1](...):
    placeholder_2()
...
HiOp[N-1](...):
    placeholder_N()
placeholder_N+1()
return 0
```

- Each of the N parts holds one body. A part may take nothing, as an `if`'s
  second part takes nothing.
- With N = 0 the HiOp is `HiOp(...)` alone, as `a + b` is.
- When each part runs, and how often, is the HiOp's own meaning. The
  configuration is the same for every HiOp.
- How a language writes the parts (`if`, `else`, `while`, the `:` of
  `a ? b : c`) is a label, not part of the configuration.

Table 1. Instances. The HiOp is named by its lowerer; the last column is how
the language writes it, a label.

| HiOp | N | its parts | how the language writes it |
|---|---|---|---|
| clang's `BinaryOperator.Add` | 0 | none; it takes `(a, b)` | `a + b` |
| clang's `WhileStmt` | 1 | `HiOp[0](test)` | `while (test) body` |
| clang's `DoStmt` | 1 | `HiOp[0](test)`, its body run before its test | `do body while (test);` |
| clang's `IfStmt` | 1 or 2 | `HiOp[0](test)`, and `HiOp[1]` when there is a second body | `if (test) body else body` |
| clang's `ConditionalOperator` | 2 | `HiOp[0](test)`, `HiOp[1]`; each body a value | `test ? value : value` |
| clang's `ForStmt` | 3 | `HiOp[0]` the start, `HiOp[1](test)` the body, `HiOp[2]` the step | `for (start; test; step) body` |
| clang's `CompoundStmt` | N | `HiOp[0]` to `HiOp[N-1]`, one statement each | `{ a; b; }` |
| CPython's `For` | 1 or 2 | `HiOp[0](item in items)`, and `HiOp[1]` when there is a second body | `for item in items: body` and `else: body` |

The second draft drew N = 0, 1 and 2 as three configurations of their own,
and wrote the second body with `else`; that tied it to `if` (the owner,
2026-10-10: "but `else` is not the abstraction is it?").

## 2. a depended-HiOp and its dependent-HiOp

```
placeholder_0()
depended_HiOp(...):
    placeholder_1()
    dependent_HiOp(...)
    placeholder_2()
placeholder_3()
return 0
```

For instance a loop and its `break;`, which leads to `placeholder_3()`.

## 3. a depended-HiOp and N dependent-HiOps

```
placeholder_0()
depended_HiOp(...):
    placeholder_1()
    dependent_HiOp_1(...)
    placeholder_2()
    ...
    dependent_HiOp_N(...)
    placeholder_N+1()
placeholder_N+2()
return 0
```

For instance a `switch` and its N `case`s.

## 4. a dependent-HiOp inside another HiOp's body

```
placeholder_0()
depended_HiOp(...):
    placeholder_1()
    HiOp(...):
        dependent_HiOp(...)
    placeholder_2()
placeholder_3()
return 0
```

For instance `while (test) { if (test) break; }`. The `break;` still depends
on the loop, not on the `if`.

Left out on purpose:
- holders;
- how a standard-form is made to compile, which is in
  [SUPPORT_standard_form_for_any_language.md](SUPPORT_standard_form_for_any_language.md);
- the lowered form.

The earlier drafts are in this file's git history: the first, longer and in
code; the second, whose configurations 1 to 3 are now configuration 1, and
whose 4 to 6 are now 2 to 4.
