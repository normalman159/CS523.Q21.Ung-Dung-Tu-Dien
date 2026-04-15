from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Node:
    label: str
    definition: Optional[str] = None
    children: dict[str, "Node"] = field(default_factory=dict)

    @property
    def is_terminal(self) -> bool:
        return self.definition is not None


class RadixTrie:
    def __init__(self) -> None:
        self.root = Node(label="")

    @staticmethod
    def _common_prefix_length(left: str, right: str) -> int:
        limit = min(len(left), len(right))
        index = 0
        while index < limit and left[index] == right[index]:
            index += 1
        return index

    def _replace_child(self, parent: Node, old_child: Node, new_child: Node) -> None:
        old_key = old_child.label[0]
        parent.children.pop(old_key, None)
        parent.children[new_child.label[0]] = new_child

    def insert(self, word: str, definition: str) -> None:
        if not word:
            raise ValueError("word must not be empty")

        current = self.root
        remaining = word

        while True:
            child = current.children.get(remaining[0])
            if child is None:
                current.children[remaining[0]] = Node(label=remaining, definition=definition)
                return

            prefix_length = self._common_prefix_length(child.label, remaining)

            if prefix_length == len(child.label):
                remaining = remaining[prefix_length:]
                if not remaining:
                    child.definition = definition
                    return
                current = child
                continue

            shared_prefix = child.label[:prefix_length]
            existing_suffix = child.label[prefix_length:]
            new_suffix = remaining[prefix_length:]

            existing_branch = Node(
                label=existing_suffix,
                definition=child.definition,
                children=child.children,
            )

            split_node = Node(label=shared_prefix)
            split_node.children[existing_branch.label[0]] = existing_branch

            if new_suffix:
                split_node.children[new_suffix[0]] = Node(
                    label=new_suffix,
                    definition=definition,
                )
            else:
                split_node.definition = definition

            self._replace_child(current, child, split_node)
            return

    def search(self, word: str) -> Optional[str]:
        if not word:
            return None

        current = self.root
        remaining = word

        while remaining:
            child = current.children.get(remaining[0])
            if child is None:
                return None

            if not remaining.startswith(child.label):
                return None

            remaining = remaining[len(child.label) :]
            current = child

        return current.definition

    def delete(self, word: str) -> bool:
        if not word:
            return False

        path: list[tuple[Node, Node]] = []
        current = self.root
        remaining = word

        while remaining:
            child = current.children.get(remaining[0])
            if child is None or not remaining.startswith(child.label):
                return False

            path.append((current, child))
            remaining = remaining[len(child.label) :]
            current = child

        if current.definition is None:
            return False

        current.definition = None

        for parent, node in reversed(path):
            if node.definition is None and not node.children:
                parent.children.pop(node.label[0], None)
                continue

            if node.definition is None and len(node.children) == 1:
                only_child = next(iter(node.children.values()))
                node.label += only_child.label
                node.definition = only_child.definition
                node.children = only_child.children

                if node.definition is None and not node.children:
                    parent.children.pop(node.label[0], None)

        return True
