from enum import Enum

class NodeTypes(Enum):
    OPERATOR = 0
    FACT = 1
    PHRASE = 2 # this is a type of temporary node (like "(A + B)") that will still need to be decomposed into operator and facts

class Node:
    type: None
    value: None
    left: None
    right: None

    def __init__(self, type, value):
        if (not isinstance(type, NodeTypes)):
            raise TypeError("Could not instantiate Node: the provided type should be a NodeTypes enum value.")
        self.type = type
        self.value = value
        self.left = None
        self.right = None

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
        self.left = None
        self.right = None

    def remove_left(self):
        self.left = None

    def remove_right(self):
        self.right = None

    def __str__(self):
        result = [f"Type: {self.type}, Content: {self.value}"]
        if (self.left is not None):
            result.append(f"Left child: {self.left.get_type()}, Content: {self.left.get_value()}")
        if (self.right is not None):
            result.append(f"Right child: {self.right.get_type()}, Content: {self.right.get_value()}")
        return "\n".join(result)

    def is_leaf(self):
        if self.left is None and self.right is None:
            return True
        return False
    
    def get_leaves(self):
        leaves = []
        if (self.right is None and self.left is None):
            leaves.append(self)
            return leaves
        if (self.right and self.right.is_leaf()):
            leaves.append(self.right)
        if (self.left and self.left.is_leaf()):
            leaves.append(self.left)
        if (self.right and not self.right.is_leaf()):
            leaves.extend(self.right.get_leaves())
        if (self.left and not self.left.is_leaf()):
            leaves.extend(self.left.get_leaves())
        return leaves

