from __future__ import annotations
from enums import ChildLinkTypes, NodeTypes

class Node:
    name: str
    type: NodeTypes
    link_type: ChildLinkTypes
    value: bool | None
    left: Node | None
    right: Node | None
    invert: bool = False
    children: list[Node]

    def __init__(self, name: str, type: NodeTypes, value: bool | None = False, link_type: ChildLinkTypes = ChildLinkTypes.DEFAULT, left: Node | None = None, right: Node | None = None, invert: bool = False):
        self.name = name
        self.type = type
        self.value = value
        self.left = left
        self.right = right
        self.invert = invert
        self.link_type = link_type
        if (type == NodeTypes.FACT):
            self.children = []
        else:
            self.children = None

    def pretty(self, prefix="", is_left=True, first=True) -> str:
        result = prefix + ("" if first else ("└── " if is_left else "├── ")) + ("!" if self.invert or self.link_type == ChildLinkTypes.INVERTED else "") + str(self.name if self.name != '|' else 'OR') + (f' {'✅' if self.value else "❌"}' if self.value is not None else " ??") +"\n"
        childs = self.get_children()
        for i, child in enumerate(childs):
            # Le dernier enfant utilise └──, les autres ├──
            is_last = (i == len(childs) - 1)
            result += child.pretty("" if first else (prefix + ("    " if is_left else "│   ")), is_last, False)
        return result

    def get_children(self) -> list[Node]:
        if self.type == NodeTypes.FACT:
            return self.children if self.children is not None else []
        else:
            children = []
            if self.left is not None:
                children.append(self.left)
            if self.right is not None:
                children.append(self.right)
            return children