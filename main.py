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


def make_tree(condition, parent_node=None):
    condition = condition.strip()
    print("conditions:", condition)
    operators = "+|^"

    open_parenthesis_counter = 0
    condition = condition.strip()

    length = len(condition)
    if condition[0] == '(' and condition[length - 1] == ')':
        condition = condition[1:(length - 1)].strip()
        length -= 2
    for i in range(length):
        index = (length - 1 - i)
        char = condition[index]
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
        if (char == "!") and (length == 2):
            parent_node.set_type(NodeTypes.OPERATOR)
            parent_node.set_value("!")
            parent_node.set_left(Node(NodeTypes.FACT, condition[length - 1]))
        if (char.isalpha()) and (length == 1):
            parent_node = Node(NodeTypes.FACT, char)
    return parent_node

def addition(a, b):
    if (a is True) and (b is True):
        return True
    if (a is None) or (b is None):
        return None
    return False

def or_operation(a, b):
    if (a is True) or (b is True):
        return True
    if (a is None) and (b is None):
        return None
    return False

def solve_simple_fact(left, right, operator):
    if isinstance(left, str):
        left = left.strip()
        left = Facts[left]
    if isinstance(right, str):
        right = right.strip()
        right = Facts[right]
    print(f"Facts left: {left}, right: {right}, operator: {operator}")
    if (operator is OperatorsEnum.AND.value):
        return addition(left, right)
    elif (operator is OperatorsEnum.OR.value):
        return or_operation(left, right)
    elif (operator is OperatorsEnum.XOR.value):
        return (left ^ right)
    elif (operator is OperatorsEnum.NOT.value):
        return (not left)
    else:
        raise ValueError("Operator isn't in the expected range.")

def solve_tree(parent_node):
    result = None
    left_child = parent_node.get_left()
    right_child = parent_node.get_right()
    if (parent_node.is_leaf()):
        return parent_node
    # problem: on essaie direct de solve avant de créer toutes les branches
    while (left_child and not left_child.is_leaf()):
        left_child = solve_tree(left_child)
        parent_node.set_left(left_child)
    while (right_child and not right_child.is_leaf()):
        right_child = solve_tree(right_child)
        parent_node.set_right(right_child)
    if (left_child.is_leaf() and right_child.is_leaf()):
        result = solve_simple_fact(left_child.get_value(), right_child.get_value(), parent_node.get_value().strip())
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
        # chercher si on connait déjà la valeur des conditions
        # sinon, appeler en récursif pour chaque condition
        tree = make_tree(conditions)
        leaves = tree.get_leaves()
        for leaf in leaves:
            if (Facts[leaf.get_value()] == False):
                solve_query(leaf.get_value())
    if tree:
        # print("tree:", tree.get_value())
        solve_tree(tree)
    else:
        print(f"No rules associated with {query}. Cannot determine its value.")


def solve_queries():
    # try:
    for query in Queries:
        solve_query(query)
    # except Exception as e:
    #     print(f"Error occurred while solving queries: {e}")


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
    
    # print('\n'.join(str(rule) for rule in Rules))
    # print("Facts:", Facts)
    # print("Queries:", Queries)
    # tree = make_tree("A + B")
    # solve_tree(tree)
    # print(tree)
    # left_child = tree.get_left()
    # right_child = tree.get_right()

    # if (left_child.get_left() is not None) or (left_child.get_right() is not None):
    #     print("Left child decomposed:")
    #     print(left_child)
    # if (right_child.get_left() is not None) or (right_child.get_right() is not None):
    #     print("Right child decomposed:")
    #     print(right_child)