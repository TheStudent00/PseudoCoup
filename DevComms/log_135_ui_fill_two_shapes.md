# log_135 — UI fill: the two shapes (structural form)

The one shaping choice at the start of the UI-fill work. No prose model — the pieces, then the call flow.

---

## the pieces that exist today

```
class Node
	attributes:
		kind          # "Column" / "Text" / "Button"
		text          # "New program", or None for a container
		children      # list of Node
	"""the neutral tree: a plain description of the screen. no pixels.
	   runtime/compose.py builds this today."""


module compose              # runtime/compose.py -- the names the transpiled Python calls
	functions:
		Column            # today: returns Node(kind="Column")
		Text              # today: returns Node(kind="Text", text=...)
		Button
		...


module kit                  # the hand-built PseudoUI (Flutter / Kivy).
	widgets:                # already works: 65/65 goldens.
		Column            # real -- draws pixels
		Text              # real -- draws pixels
		Button
		...
```

---

## how it runs today (no pixels yet)

```
compose.Column()               --> Node(kind="Column")
compose.Text("New program")    --> Node(kind="Text", text="New program")
```

result: a `Node` tree. the render gate counts it (28/29). the `kit` is not touched yet.

---

## the fork: how to connect the `Node` tree to the `kit`

### option A -- keep `Node`, add a walker

```
class KitRenderer              # the ONLY new piece in A
	methods:
		walk               # reads a Node tree, calls the matching kit widget per node
```

call flow (two stages):
```
stage 1:   compose.Column()      --> Node(kind="Column")
stage 2:   KitRenderer.walk()    --> kit.Column()
```

### option B -- no `Node`, `compose` calls `kit` directly

```
(no new class; the compose functions are rewritten)
```

call flow (one stage):
```
compose.Column()                 --> kit.Column()
```

---

## side by side

input (transpiled Python, IDENTICAL in both):  `Column(content = Text("New program"))`

```
A:   compose.Column()  -->  Node(Column)[ Node(Text) ]  -->  KitRenderer.walk()  -->  kit.Column([ kit.Text ])
B:   compose.Column()  -->  kit.Column([ kit.Text ])
```

---

## what each costs / gives

```
A:  Node stays.
	+ Node is kit-agnostic: the SAME tree feeds a Flutter kit AND a Kivy kit
	  (second kit = a second walker, not a second compose.py)
	+ the tree is inspectable -- goldens / map tools read it
	- two stages + the Node artifact to carry

B:  Node deleted.
	+ one hop, simpler
	- compose.* is welded to ONE kit
	- a second kit needs a whole second compose.py
```

---

## the invariant (holds in BOTH options)

```
the transpiled line   Column(content = ...)   NEVER changes.
we only ever fill in   compose.*   (and, in A, add KitRenderer).
```

---

## the question, one line

keep the middle `Node` layer (**A**), or drop it and bind straight to the `kit` (**B**)?
