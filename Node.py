from enum import Enum

class NodeTypes(Enum):
    OPERATOR = 0
    FACT = 1 # a letter, a query to be solved
    PHRASE = 2 # this is a type of temporary node (like "(A + B)") that will still need to be decomposed into operator and facts
    BOOLEAN = 3 # this is a type of node that will hold a boolean value (True or False) after evaluation

class Node:
    type: None
    value: None
    left: None
    right: None
    children: None # this only exists if the type of the Node is FACT. The children are subtrees, all of them conditions that can prove the fact to be True.

    def __init__(self, type, value):
        if (not isinstance(type, NodeTypes)):
            raise TypeError("Could not instantiate Node: the provided type should be a NodeTypes enum value.")
        self.type = type
        self.value = value
        self.left = None
        self.right = None
        if (type == NodeTypes.FACT):
            self.children = []
        else:
            self.children = None

    def set_right(self, node):
        self.right = node

    def set_left(self, node):
        self.left = node

    def set_value(self, value):
        self.value = value

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

    def get_value(self):
        return self.value
    
    def get_left(self):
        if self.left is None:
            return None
        return self.left
    
    def get_right(self):
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
    
    def add_child(self, child):
        if self.type != NodeTypes.FACT:
            raise TypeError("Only nodes of type FACT can have children.")
        self.children.append(child)

    def get_children(self):
        return self.children

    def remove_left(self):
        if self.type != NodeTypes.OPERATOR:
            raise TypeError("Only nodes of type OPERATOR can have left or right children.")
        self.left = None

    def remove_right(self):
        if self.type != NodeTypes.OPERATOR:
            raise TypeError("Only nodes of type OPERATOR can have left or right children.")
        self.right = None

    def __str__(self):
        result = [f"Type: {self.type}, Content: {self.value}"]
        if (self.left is not None):
            result.append(f"Left child: {self.left.get_type()}, Content: {self.left.get_value()}")
        else:
            result.append("Left child: None")
        if (self.right is not None):
            result.append(f"Right child: {self.right.get_type()}, Content: {self.right.get_value()}")
        else:
            result.append("Right child: None")
        if (self.children is not None and len(self.children) > 0):
            result.append(f"Children ({len(self.children)}):")
            for i, child in enumerate(self.children):
                result.append(f" Child {i+1}: {child.get_type()}, Content: {child.get_value()}")
        else:
            result.append("Children: None")
        return "\n".join(result)

    def is_leaf(self):
        if self.type == NodeTypes.FACT:
            return len(self.children) == 0
        if self.left is None and self.right is None:
            return True
        return False
    
    def get_leaves(self):
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
        if (self.left and self.left.is_leaf()):
            leaves.append(self.left)
        if (self.right and self.right.is_leaf()):
            leaves.append(self.right)
        if (self.left and not self.left.is_leaf()):
            leaves.extend(self.left.get_leaves())
        if (self.right and not self.right.is_leaf()):
            leaves.extend(self.right.get_leaves())
        return leaves
    
    def get_last_nodes(self):
        nodes = []
        if (self.is_leaf()):
            nodes.append(self)
            return nodes
        if self.type == NodeTypes.FACT:
            for child in self.children:
                nodes.extend(child.get_last_nodes())
            return nodes
        left = self.left
        right = self.right
        if (left.is_leaf() and right.is_leaf()):
            nodes.append(self)
        else:
            if (not left.is_leaf()):
                nodes.extend(left.get_last_nodes())
            if (not right.is_leaf()):
                nodes.extend(right.get_last_nodes())
        return nodes
    
    