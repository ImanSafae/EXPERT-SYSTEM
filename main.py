import string
from Node import Node, NodeTypes
from Rule import Rule
from utils import Utils
from enums import TokensEnum, OperatorsEnum
from collections import OrderedDict
import os
import sys

Rules = []
Facts = {}
Queries = []

def extract_rule(line):
    relation = ""
    split_rule = line.split("<=>")
    if (len(split_rule) == 1):
        split_rule = line.split("=>")
        relation = "implies"
    else:
        relation = "if and only if"

    if (not len(split_rule) == 2):
        raise SyntaxError("Wrong rule format.")
    
    condition = split_rule[0]
    conclusion = split_rule[1]
    newRule = Rule(condition, conclusion, relation)
    Rules.append(newRule)
    

def extract_facts(line):
    facts = line[1:]
    if (len(facts) == 0):
        return
    for index, fact in enumerate(facts):
        if (not fact.isalpha()):
            message = f"Wrong fact format found at index {index}: \"{fact}\". Skipped."
            print(message)
            continue
        Facts[fact.upper()] = True

def extract_queries(line):
    queries = line[1:]
    if (len(queries) == 0):
        return
    for index, query in enumerate(queries):
        if (not query.isalpha()):
            message = f"Wrong query format found at index {index}: \"{query}\". Skipped."
            print(message)
            continue
        Queries.append(query)



def parse_inputfile(input):
    try:
        for index, line in enumerate(input):
            line = Utils.remove_comments(line)
            line = line.strip()
            if (len(line) == 0):
                continue
            if (not Utils.is_string_valid(line)):
                message = f"Invalid character found in line {index}. Line skipped."
                print(message)
                continue
            if line.startswith('='):
                extract_facts(line)
            elif line.startswith('?'):
                extract_queries(line)
            elif line.startswith('#'):
                continue
            else:
                if (not Utils.is_rule_valid(line)):
                    message = f"Invalid rule format at line {index}. Line skipped."
                    print(message)
                    continue
                extract_rule(line)
    except Exception as e:
        print(f"Error while parsing input file: {e}")

def init_facts():
    ord_a = ord("A")

    for i in range(26):
        letter = chr(ord_a + i)
        Facts[letter] = False

# def decompose_node(node):
#     if (not isinstance(node, Node)):
#         raise TypeError("decompose_node: arg should be of type Node.")
#     if (node.get_type() != NodeTypes.PHRASE):
#         raise ValueError("decompose_node: node is already decomposed.")
#     return make_tree(node.value, node)

def handle_not_operator(condition, index):
    if index == -1 or index == len(condition) - 1:
        raise ValueError("Invalid NOT operator usage.")
    if condition[index + 1] == '(':
        # Find the matching closing parenthesis
        open_parens = 1
        for j in range(index + 2, len(condition)):
            if condition[j] == '(':
                open_parens += 1
            elif condition[j] == ')':
                open_parens -= 1
            if open_parens == 0:
                # Replace !(...) with ( ... ) and add NOT operator
                inner = condition[index + 2:j]
                print("inner:", inner)
                parent_node = Node(NodeTypes.OPERATOR, '!')
                parent_node.set_left(make_tree(inner))
                return parent_node
        raise ValueError("Mismatched parentheses in NOT operator usage.")
    else:
        # Handle single character NOT
        if not condition[index + 1].isalpha():
            raise ValueError("Invalid character after NOT operator.")
        parent_node = Node(NodeTypes.OPERATOR, '!')
        parent_node.set_left(Node(NodeTypes.FACT, condition[index + 1]))
        return parent_node

def make_tree(condition, parent_node=None):
    operators = "+|^"
    open_parenthesis_counter = 0
    condition = condition.strip()
    length = len(condition)
    if condition[0] == '(' and condition[length - 1] == ')' and len(Utils.find_all_indexes(condition, '(')) == 1:
        condition = condition[1:(length - 1)].strip()  
        length -= 2
    for i in range(length):
        index = (length - 1 - i)
        char = condition[index]
        if char.isspace():
            continue
        if char == ')':
            open_parenthesis_counter += 1
            continue
        elif char == '(':
            open_parenthesis_counter -=1
        if open_parenthesis_counter > 0:
            continue
        if char in operators:
            parent_node = Node(NodeTypes.OPERATOR, char)
            left_node_content = (condition[:index]).strip()
            right_node_content = (condition[(index + 1):]).strip()
            right_node_type = NodeTypes.FACT if len(right_node_content) == 1 else NodeTypes.PHRASE
            left_node_type = NodeTypes.FACT if len(left_node_content) == 1 else NodeTypes.PHRASE
            parent_node.set_left(Node(left_node_type, left_node_content))
            parent_node.set_right(Node(right_node_type, right_node_content))
            if (parent_node.get_left().get_type() == NodeTypes.PHRASE):
                # print("decomposing left child")
                # parent_node.set_left(decompose_node(parent_node.get_left()))
                parent_node.set_left(make_tree(parent_node.get_left().get_value(), parent_node.get_left()))
            if (parent_node.get_right().get_type() == NodeTypes.PHRASE):
                # print("decomposing right child")
                # parent_node.set_right(decompose_node(parent_node.get_right()))
                parent_node.set_right(make_tree(parent_node.get_right().get_value(), parent_node.get_right()))
            break
        elif (char == "!"):
            parent_node = handle_not_operator(condition, index)
        elif (char.isalpha()) and (length == 1):
            parent_node = Node(NodeTypes.FACT, char)
    return parent_node

def addition(a, b):
    if (a is True) and (b is True):
        return True
    if (a is None) or (b is None):
        return None
    return False

def or_operation(a, b) :
    if (a is True) or (b is True):
        return True
    if (a is None) and (b is None):
        return None
    return False


def solve_simple_fact(left, right, operator):
    """
    Takes two facts ("A", "B", etc.), or their boolean values, as well as an operator (AND, OR, XOR, NOT).
    Fetches the facts' boolean values from the Facts dictionary when needed, and applies the operator.
    """
    if isinstance(left, str):
        left = left.strip()
        if left not in Facts:
            raise ValueError(f"Arg 1 should be a valid fact (alpha character) or its boolean value. Got '{left}' instead.")
        left = Facts[left]
    if isinstance(right, str):
        right = right.strip()
        if right not in Facts:
            raise ValueError(f"Arg 2 should be a valid fact (alpha character) or its boolean value. Got '{right}' instead.")
        right = Facts[right]
    print(f"Facts left: {left}, right: {right}, operator: {operator}")
    if (operator == OperatorsEnum.AND.value):
        return addition(left, right)
    elif (operator == OperatorsEnum.OR.value):
        return or_operation(left, right)
    elif (operator == OperatorsEnum.XOR.value):
        return (left ^ right)
    elif (operator == OperatorsEnum.NOT.value):
        return (not left)
    else:
        raise ValueError("Operator isn't in the expected range.")

def solve_tree(parent_node):
    result = None

    def node_to_value(node):
        """Convert a leaf node's value to a boolean/None. If the leaf stores a fact name (str),
        return Facts.get(name, None). If it already stores a boolean/None, return it as-is.
        """
        if node is None:
            return None
        val = node.get_value()
        if isinstance(val, str):
            return Facts.get(val.strip(), None)
        return val

    # short-circuit: already a leaf
    if parent_node.is_leaf():
        return parent_node

    # resolve children recursively if needed
    left = parent_node.get_left()
    right = parent_node.get_right()
    if left is not None and not left.is_leaf():
        left = solve_tree(left)
        parent_node.set_left(left)
    if right is not None and not right.is_leaf():
        right = solve_tree(right)
        parent_node.set_right(right)

    operator = parent_node.get_value().strip()

    if operator == OperatorsEnum.NOT.value:
        # accept child in left or right (prefer left if present)
        child = left
        if child is None:
            raise ValueError("NOT operator node has no child.")
        cval = node_to_value(child)
        result = None if cval is None else (not cval)
        parent_node.set_type(NodeTypes.FACT)
        parent_node.set_value(result)
        parent_node.remove_children()
        print("result:", result)
        return parent_node

    # binary operators: ensure both children exist
    if left is None or right is None:
        raise ValueError("Binary operator node missing left or right child.")

    lval = node_to_value(left)
    rval = node_to_value(right)

    if operator == OperatorsEnum.AND.value:
        result = addition(lval, rval)
    elif operator == OperatorsEnum.OR.value:
        result = or_operation(lval, rval)
    elif operator == OperatorsEnum.XOR.value:
        result = None if (lval is None or rval is None) else (lval ^ rval)
    else:
        raise ValueError(f"Unknown operator: {operator}")

    parent_node.set_type(NodeTypes.FACT)
    parent_node.set_value(result)
    parent_node.remove_children()
    print("result:", result)
    return parent_node



def solve_query(query):
    if (Facts[query] == True) or (Facts[query] == None):
        print(f"{query} is {Facts[query]}")
        return # si le fact est déjà True ou indéterminé, c'est qu'on l'a déjà traité
    associated_rules = Utils.find_associated_rules(query, Rules)
    tree = None
    print(f"Rules associated with {query}:")
    for rule in associated_rules:
        conditions = rule.conditions
        print(f"conditions to solve: {conditions}")
        tree = make_tree(conditions)
        # leaves = tree.get_leaves()
        # ici on peut chercher à étendre les leaves en cherchant toutes les rules associées
        # print(f"Leaves to solve: {[leaf.get_value() for leaf in leaves]}")
        # for leaf in leaves:
            # if (Facts[leaf.get_value()] == False):
                # print(f"Solving leaf: {leaf.get_value()}")
                # solve_query(leaf.get_value())
        last_nodes = tree.get_last_nodes()
        for node in last_nodes:
            solve_node(node)
    # if tree:
        # print("tree:", tree.get_value())
        # solve_tree(tree)
    # else:
        # print(f"No rules associated with {query}. Cannot determine its value.")


def solve_queries():
    try:
        for query in Queries:
            solve_query(query)
    except Exception as e:
        print(f"Error occurred while solving queries: {e}")


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print("Usage: python main.py <input_file>")
        sys.exit(1)

    input_filename = sys.argv[1]
    if not os.path.isfile(input_filename):
        print(f"File {input_filename} does not exist.")
        sys.exit(1)
    init_facts()

    with open(input_filename, "r") as input:
        parse_inputfile(input)
        solve_queries()
