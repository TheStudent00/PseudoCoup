"""Ingest coverage recorder (Task 13).

Records, for every tree-sitter node encountered while ingesting a Kotlin file,
whether that node was consumed by a handler in `KotlinIngestor._map_node` or
dropped. "Dropped" has two distinct causes, both silent before this instrument:

  handled    - `_map_node` took a real branch for the node type.
  dropped    - `_map_node` was called on the node but fell through to the final
               `else` (no branch for that type) -> returned None.
  unvisited  - the node was never passed to `_map_node` at all, because a parent
               handler walked only the children it cared about and skipped this
               one (trivia like `;`/comments, but also real constructs a parent
               drops on the floor).

`handled` + `dropped` + `unvisited` partitions every node in the tree. The
worklist for Tasks 07-10 is `dropped` ∪ `unvisited`, minus the accepted baseline.

The recorder does not touch emit: it only observes. When no recorder is attached
to the ingestor, `_map_node` runs exactly as before.
"""
from collections import defaultdict


class CoverageRecorder:
    def __init__(self):
        # node_type -> count, and one example "file:line".
        self.handled = defaultdict(int)
        self.dropped = defaultdict(int)
        self.unvisited = defaultdict(int)
        self._example = {}          # (bucket, node_type) -> "file:line"
        # ids of tree-sitter nodes `_map_node` was invoked on, per current file,
        # and ids of those that fell through to the no-handler `else`.
        self._seen_ids = set()
        self._dropped_ids = set()
        self._current_file = "<unknown>"

    def start_file(self, path):
        self._current_file = path
        self._seen_ids = set()
        self._dropped_ids = set()

    def _note_example(self, bucket, node_type, node):
        key = (bucket, node_type)
        if key not in self._example:
            # tree-sitter rows are 0-based; report 1-based lines.
            line = node.start_point[0] + 1
            self._example[key] = f"{self._current_file}:{line}"

    def record_seen(self, node):
        """Called at the top of `_map_node` for every node it is invoked on."""
        self._seen_ids.add(id(node))

    def record_dropped(self, node):
        """Called when `_map_node` fell through to the no-handler `else`."""
        self._dropped_ids.add(id(node))
        self.dropped[node.type] += 1
        self._note_example("dropped", node.type, node)

    def finish_file(self, root_node):
        """After ingesting a file, walk its full tree and bucket every node:
        seen-and-not-dropped -> handled, seen-and-dropped -> dropped (already
        counted), never-seen -> unvisited."""
        stack = [root_node]
        while stack:
            node = stack.pop()
            nid = id(node)
            if nid not in self._seen_ids:
                # Anonymous (unnamed) nodes are operator/keyword/punctuation
                # tokens the grammar exposes but no transpiler handler targets
                # by type (`.`, `,`, `++`, `!in`, `abstract`, ...). They are
                # never a real gap, so they are not signal for the worklist.
                if node.is_named:
                    self.unvisited[node.type] += 1
                    self._note_example("unvisited", node.type, node)
            elif nid not in self._dropped_ids:
                self.handled[node.type] += 1
                self._note_example("handled", node.type, node)
            stack.extend(node.children)

    def example_for(self, bucket, node_type):
        return self._example.get((bucket, node_type), "")
