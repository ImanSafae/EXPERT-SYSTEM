from enum import Enum


class NodeTypes(Enum):
    OPERATOR = 0
    FACT = 1  # a letter, a query to be solved
    PHRASE = 2  # temporary node (like "(A + B)") that will be decomposed
    BOOLEAN = 3  # type of node that will hold a boolean value after evaluation


class ChildLinkTypes(Enum):
    DEFAULT = 0
    INVERTED = 1


class Child:
    node: None
    link_type: None

    def __init__(self, node, link_type=ChildLinkTypes.DEFAULT):
        if (not isinstance(node, Node)):
            raise TypeError("""Could not instantiate Child:
                    the provided node should be a Node object.""")
        if (not isinstance(link_type, ChildLinkTypes)):
            raise TypeError("""Could not instantiate Child:
                the provided link_type should be a ChildLinkTypes value.""")
        self.node = node
        self.link_type = link_type

    def get_node(self):
        return self.node

    def get_link_type(self):
        return self.link_type


class Node:
    type: NodeTypes
    value: str | bool | None
    left: Child
    right: Child
    children: list[Child]  # this only exists if the type of the Node is FACT.

    def __init__(self, type: NodeTypes, value: str | bool | None):
        self.type = type
        self.value = value
        self.left = None
        self.right = None
        if (type == NodeTypes.FACT):
            self.children = []
        else:
            self.children = None

    def set_right(self, node: Child):
        self.right = node

    def set_left(self, node: Child):
        self.left = node

    def set_value(self, value: str | bool | None):
        self.value = value

    def set_type(self, type: NodeTypes):
        self.type = type

    def get_type(self) -> NodeTypes:
        return self.type

    def get_value(self) -> str | bool | None:
        return self.value

    def get_left(self) -> Child | None:
        if self.left is None:
            return None
        return self.left

    def get_right(self) -> Child | None:
        if self.right is None:
            return None
        return self.right

    def remove_children(self):
        if self.left is not None:
            del self.left
        if self.right is not None:
            del self.right
        if self.children:
            self.children.clear()
        self.left = None
        self.right = None

    def add_child(self, child: Child):
        if self.type != NodeTypes.FACT:
            raise TypeError("Only nodes of type FACT can have children.")
        self.children.append(child)

    def get_children(self) -> list[Child]:
        return self.children

    def remove_left(self):
        if self.type != NodeTypes.OPERATOR:
            raise TypeError("""Only nodes of type OPERATOR
            can have left or right children.""")
        self.left = None

    def remove_right(self):
        if self.type != NodeTypes.OPERATOR:
            raise TypeError("""Only nodes of type OPERATOR
            can have left or right children.""")
        self.right = None

    def __str__(self):
        result = [f"Type: {self.type}, {self.value}"]
        if (self.left is not None):
            result.append(f"Left child:{self.left.type}, {self.left.value}")
        else:
            result.append("Left child: None")
        if (self.right is not None):
            result.append(f"Right child:{self.right.type}, {self.right.value}")
        else:
            result.append("Right child: None")
        if (self.children is not None and len(self.children) > 0):
            result.append(f"Children ({len(self.children)}):")
            for i, child in enumerate(self.children):
                result.append(f"Child {i+1}:{child.type}, {child.value}")
        else:
            result.append("Children: None")
        return "\n".join(result)

    def is_leaf(self) -> bool:
        if self.type == NodeTypes.FACT:
            return len(self.children) == 0
        if self.left is None and self.right is None:
            return True
        return False

    def get_leaves(self) -> list:
        leaves = []
        if self.type == NodeTypes.FACT:
            if self.is_leaf():
                leaves.append(self)
                return leaves
            else:
                for child in self.children:
                    leaves.extend(child.get_leaves())
        if (self.right is None and self.left is None):
            leaves.append(self)
            return leaves
        if (self.left and self.left.get_node().is_leaf()):
            leaves.append(self.left.get_node())
        if (self.right and self.right.get_node().is_leaf()):
            leaves.append(self.right.get_node())
        if (self.left and not self.left.get_node().is_leaf()):
            leaves.extend(self.left.get_node().get_leaves())
        if (self.right and not self.right.get_node().is_leaf()):
            leaves.extend(self.right.get_node().get_leaves())
        return leaves

    def get_last_nodes(self) -> list:
        nodes = []
        if (self.is_leaf()):
            nodes.append(self)
            return nodes
        if self.type == NodeTypes.FACT:
            for child in self.children:
                nodes.extend(child.get_node().get_last_nodes())
            return nodes
        left = self.left.get_node()
        right = self.right.get_node()
        if (left.is_leaf() and right.is_leaf()):
            nodes.append(self)
        else:
            if (not left.is_leaf()):
                nodes.extend(left.get_node().get_last_nodes())
            if (not right.is_leaf()):
                nodes.extend(right.get_node().get_last_nodes())
        return nodes
