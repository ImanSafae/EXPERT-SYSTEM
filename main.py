from Node import Node, NodeTypes, Child, ChildLinkTypes
from Rule import Rule
from utils import Utils
from enums import OperatorsEnum, RelationEnum
import os
import sys

Rules = []
Facts = {}
Queries = []
Queue = []


def extract_rule(line):
    relation = ""
    split_rule = line.split("<=>")
    if (len(split_rule) == 1):
        split_rule = line.split("=>")
        relation = RelationEnum.IMPLICATION.value
    else:
        relation = RelationEnum.BICONDITIONAL.value

    if not len(split_rule) == 2:
        raise SyntaxError("Wrong rule format.")

    condition = split_rule[0]
    conclusion = split_rule[1]
    if ("|" in conclusion):
        return
    newRule = Rule(condition, conclusion, relation)
    Rules.append(newRule)
    if relation == RelationEnum.BICONDITIONAL.value:
        reverseRule = Rule(conclusion, condition, relation)
        Rules.append(reverseRule)


def extract_facts(line):
    facts = line[1:]
    if len(facts) == 0:
        return
    for index, fact in enumerate(facts):
        if not fact.isalpha():
            message = (f"Wrong fact format found at index {index}: "
                       f"\"{fact}\". Skipped.")
            print(message)
            continue
        Facts[fact.upper()] = True


def extract_queries(line):
    queries = line[1:]
    if len(queries) == 0:
        return
    for index, query in enumerate(queries):
        if not query.isalpha():
            message = (f"Wrong query format found at index {index}: "
                       f"\"{query}\". Skipped.")
            print(message)
            continue
        Queries.append(query)


def parse_inputfile(input):
    try:
        for index, line in enumerate(input):
            line = Utils.remove_comments(line)
            line = line.strip()
            if len(line) == 0:
                continue
            if not Utils.is_string_valid(line):
                message = (f"Invalid character found in line {index}. "
                           f"Line skipped.")
                print(message)
                continue
            if line.startswith('='):
                extract_facts(line)
            elif line.startswith('?'):
                extract_queries(line)
            elif line.startswith('#'):
                continue
            else:
                if not Utils.is_rule_valid(line):
                    message = (f"Invalid rule format at line {index}. "
                               f"Line skipped.")
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
                # print("inner:", inner)
                parent_node = Node(NodeTypes.OPERATOR, '!')
                parent_node.set_left(
                    Child(parse_condition_into_tree(inner)))
                return parent_node
        raise ValueError(
            "Mismatched parentheses in NOT operator usage.")
    else:
        # Handle single character NOT
        if not condition[index + 1].isalpha():
            raise ValueError("Invalid character after NOT operator.")
        parent_node = Node(NodeTypes.OPERATOR, '!')
        parent_node.set_left(
            Child(Node(NodeTypes.FACT, condition[index + 1])))
        return parent_node


def parse_condition_into_tree(condition):
    """
    Parse a condition string (like "A+B|C") into a Node tree.
    Uses right-to-left scan to respect precedence encoded by parentheses.
    """
    if condition is None:
        raise ValueError("Empty condition")
    condition = condition.strip()
    if len(condition) == 0:
        raise ValueError("Empty condition")

    length = len(condition)
    if condition[0] == '(' and condition[-1] == ')':
        open_parens = 0
        encloses = True
        for i, ch in enumerate(condition):
            if ch == '(':
                open_parens += 1
            elif ch == ')':
                open_parens -= 1
                if open_parens == 0 and i < length - 1:
                    encloses = False
                    break
        if encloses:
            condition = condition[1:-1].strip()
            length = len(condition)

    operators = "+|^"
    open_parenthesis_counter = 0

    for i in range(length):
        index = (length - 1 - i)
        char = condition[index]
        if char.isspace():
            continue
        if char == ')':
            open_parenthesis_counter += 1
            continue
        elif char == '(':
            open_parenthesis_counter -= 1
        if open_parenthesis_counter > 0:
            continue
        if char in operators:
            parent_node = Node(NodeTypes.OPERATOR, char)
            left_node_content = (condition[:index]).strip()
            right_node_content = (condition[(index + 1):]).strip()
            right_node_type = (NodeTypes.FACT if len(right_node_content) == 1
                               else NodeTypes.PHRASE)
            left_node_type = (NodeTypes.FACT if len(left_node_content) == 1
                              else NodeTypes.PHRASE)
            parent_node.set_left(
                Child(Node(left_node_type, left_node_content)))
            parent_node.set_right(
                Child(Node(right_node_type, right_node_content)))
            if (parent_node.get_left().get_node().get_type() ==
                    NodeTypes.PHRASE):
                parent_node.set_left(Child(parse_condition_into_tree(
                    parent_node.get_left().get_node().get_value())))
            if (parent_node.get_right().get_node().get_type() ==
                    NodeTypes.PHRASE):
                parent_node.set_right(Child(parse_condition_into_tree(
                    parent_node.get_right().get_node().get_value())))
            return parent_node
        elif (char == '!'):
            return handle_not_operator(condition, index)
        elif (char.isalpha()) and (length == 1):
            return Node(NodeTypes.FACT, char)

    return Node(NodeTypes.PHRASE, condition)


def solve_not(node):
    if not isinstance(node, Node):
        raise TypeError("solve_not: arg should be of type Node.")
    if (node.get_type() != NodeTypes.OPERATOR or
            node.get_value() != OperatorsEnum.NOT.value):
        raise ValueError("solve_not: node should contain a NOT operator.")
    child = node.get_left().get_node()
    if child is None:
        raise ValueError("solve_not: NOT operator node has no child.")
    if child.get_type() != NodeTypes.FACT:
        raise ValueError(
            "solve_not: child of NOT operator should be a FACT node.")
    fact = child.get_value()
    if not fact.isalpha() or len(fact) != 1:
        raise ValueError(
            "solve_not: child node value should be a single alphabetic "
            "character representing a fact.")
    value = Facts[fact.upper()]
    if value is None:
        node.set_type(NodeTypes.BOOLEAN)
        node.set_value(None)
    else:
        node.set_type(NodeTypes.BOOLEAN)
        node.set_value(not value)
    node.remove_children()
    return node


def solve_addition(node):
    if (node.get_type() != NodeTypes.OPERATOR or
            node.get_value() != OperatorsEnum.AND.value):
        raise ValueError(
            "solve_addition: node should contain an AND operator.")
    left = node.get_left().get_node()
    right = node.get_right().get_node()
    if left is None or right is None:
        raise ValueError(
            "solve_addition: AND operator node missing left or right child. "
            "Cannot solve addition without two facts.")
    lfact = left.get_value()
    rfact = right.get_value()
    # print("lfact:", lfact, "rfact:", rfact)
    if (not (isinstance(lfact, bool)) and
            not (lfact.isalpha() and len(lfact) == 1)):
        raise ValueError(
            "solve_addition: left child node value should be a single "
            "alphabetic character representing a fact.")
    if (not (isinstance(rfact, bool)) and
            not (rfact.isalpha() and len(rfact) == 1)):
        raise ValueError(
            "solve_addition: right child node value should be a single "
            "alphabetic character representing a fact.")
    if not isinstance(lfact, bool):
        lvalue = Facts[lfact.upper()]
    else:
        lvalue = lfact
    if not isinstance(rfact, bool):
        rvalue = Facts[rfact.upper()]
    else:
        rvalue = rfact
    if lvalue is None or rvalue is None:
        node.set_type(NodeTypes.BOOLEAN)
        node.set_value(None)
    else:
        node.set_type(NodeTypes.BOOLEAN)
        node.set_value(lvalue and rvalue)
    node.remove_children()
    return node


def solve_or(node):
    if (node.get_type() != NodeTypes.OPERATOR or
            node.get_value() != OperatorsEnum.OR.value):
        raise ValueError("solve_or: node should contain an OR operator.")
    left = node.get_left().get_node()
    right = node.get_right().get_node()
    if left is None or right is None:
        raise ValueError(
            "solve_or: OR operator node missing left or right child. "
            "Cannot solve OR without two facts.")
    lfact = left.get_value()
    rfact = right.get_value()
    if (not (lfact.isalpha() and len(lfact) == 1) and
            not (isinstance(lfact, bool))):
        raise ValueError(
            "solve_or: left child node value should be a single "
            "alphabetic character representing a fact.")
    if (not (rfact.isalpha() and len(rfact) == 1) and
            not (isinstance(rfact, bool))):
        raise ValueError(
            "solve_or: right child node value should be a single "
            "alphabetic character representing a fact.")
    if not isinstance(lfact, bool):
        lvalue = Facts[lfact.upper()]
    else:
        lvalue = lfact
    if not isinstance(rfact, bool):
        rvalue = Facts[rfact.upper()]
    else:
        rvalue = rfact
    if lvalue is None or rvalue is None:
        node.set_type(NodeTypes.BOOLEAN)
        node.set_value(None)
    else:
        node.set_type(NodeTypes.BOOLEAN)
        node.set_value(lvalue or rvalue)
    node.remove_children()
    return node


def solve_xor(node):
    if (node.get_type() != NodeTypes.OPERATOR or
            node.get_value() != OperatorsEnum.XOR.value):
        raise ValueError("solve_xor: node should contain an XOR operator.")
    left = node.get_left().get_node()
    right = node.get_right().get_node()
    if left is None or right is None:
        raise ValueError(
            "solve_xor: XOR operator node missing left or right child. "
            "Cannot solve XOR without two facts.")
    lfact = left.get_value()
    rfact = right.get_value()
    if (not (lfact.isalpha() and len(lfact) == 1) and
            not (isinstance(lfact, bool))):
        raise ValueError(
            "solve_xor: left child node value should be a single "
            "alphabetic character representing a fact.")
    if (not (rfact.isalpha() and len(rfact) == 1) and
            not (isinstance(rfact, bool))):
        raise ValueError(
            "solve_xor: right child node value should be a single "
            "alphabetic character representing a fact.")
    if not isinstance(lfact, bool):
        lvalue = Facts[lfact.upper()]
    else:
        lvalue = lfact
    if not isinstance(rfact, bool):
        rvalue = Facts[rfact.upper()]
    else:
        rvalue = rfact
    if lvalue is None or rvalue is None:
        node.set_type(NodeTypes.BOOLEAN)
        node.set_value(None)
    else:
        node.set_type(NodeTypes.BOOLEAN)
        node.set_value(lvalue ^ rvalue)
    node.remove_children()
    return node


def determine_link(query, rule):
    """
    This function determines whether the link between a fact and its
    condition is direct or inverted.
    For example, in the rule "A + B => C", the condition "A + B" directly
    supports "C".
    In the rule "A + B => !C", the condition "A + B" inversely supports "C".
    """
    conclusions = rule.conclusions
    # print("conclusions to study: [", conclusions, "]")
    if query in conclusions and "!" in conclusions:
        return ChildLinkTypes.INVERTED
    return ChildLinkTypes.DEFAULT


def make_tree(parent_node):
    """
    Recursively extend a FACT node by finding associated rules and
    adding their condition trees as children until no more expansions
    are possible. Protects against cycles using the `seen` set and
    avoids re-expanding a fact that already has children.
    """
    if not isinstance(parent_node, Node):
        raise TypeError("make_tree: arg should be of type Node.")
    if parent_node.get_type() != NodeTypes.FACT:
        raise ValueError("make_tree: node is not of type FACT.")
    fact = parent_node.get_value()
    associated_rules = Utils.find_associated_rules(fact, Rules)
    for rule in associated_rules:
        if rule.__str__() in Queue:
            continue
        Queue.append(rule.__str__())
        # adjust later to take into account "if and only if"
        conditions = rule.conditions
        new_child = parse_condition_into_tree(conditions)
        child_link = determine_link(fact, rule)
        parent_node.add_child(Child(new_child, child_link))
    for child in parent_node.get_children():
        child_node = child.get_node()
        leaves = child_node.get_leaves()
        for leaf in leaves:
            if leaf.get_type() != NodeTypes.FACT:
                continue
            leaf_fact = leaf.get_value().strip().upper()
            if (Facts.get(leaf_fact) is True or
                    Facts.get(leaf_fact) is None):
                continue
            leaf = make_tree(leaf)
    return parent_node


def solve_fact_node(node: Node):
    conditions = node.get_children()
    print(f"Solving query {node.get_value()} with "
          f"{len(conditions)} condition(s).")
    for condition in conditions:
        child_node = condition.get_node()
        print("solving condition:", child_node.get_value())
        type = child_node.get_type()
        match type:
            case NodeTypes.FACT:
                value = child_node.get_value()
                child_node = solve_fact_node(child_node)
                if child_node.get_type() != NodeTypes.BOOLEAN:
                    raise ValueError(
                        "Condition did not resolve to a boolean value.")
                if child_node.get_value() is True:
                    Facts[node.get_value()] = (
                        condition.get_link_type() == ChildLinkTypes.DEFAULT)
                    print(f"Fact {node.get_value()} set to True "
                          f"based on condition {condition.get_node().get_value()}.")
                    node.set_type(NodeTypes.BOOLEAN)
                    node.set_value(True)
                    return node
                # else:
                #     print(f"Condition {child_node.get_value()} evaluated "
                #           f"to False or None: {child_node.get_value()}. "
                #           f"Continuing to next condition.")
                continue
            case NodeTypes.OPERATOR:
                value = f"{child_node.get_left().get_node().get_value()} {child_node.get_value()} {child_node.get_right().get_node().get_value()}"
                print("solving operator condition:", value)
                child_node = solve_operator_node(child_node)
                if child_node.get_type() != NodeTypes.BOOLEAN:
                    raise ValueError(
                        "Condition did not resolve to a boolean value.")
                if child_node.get_value() is True:
                    Facts[node.get_value()] = (
                        condition.get_link_type() == ChildLinkTypes.DEFAULT)
                    print(f"Fact {node.get_value()} set to True "
                          f"based on condition {value}.")
                    node.set_type(NodeTypes.BOOLEAN)
                    node.set_value(True)
                    return node
                continue
            case NodeTypes.PHRASE:
                raise SystemError(
                    "Something went wrong during tree construction. "
                    "Condition node should not be of type PHRASE.")
    node.set_type(NodeTypes.BOOLEAN)
    node.set_value(Facts[node.get_value()])
    return node


def solve_operator_node(node: Node):
    type = node.get_type()
    value = node.get_value()

    if type != NodeTypes.OPERATOR:
        raise ValueError("solve_operator_node: node is not of type OPERATOR.")

    rNode = node.get_right().get_node()
    lNode = node.get_left().get_node()
    if rNode.get_type() == NodeTypes.OPERATOR:
        node.set_right(
            Child(solve_operator_node(rNode), node.get_right().link_type))
        del rNode
    if lNode.get_type() == NodeTypes.OPERATOR:
        node.set_left(
            Child(solve_operator_node(lNode), node.get_left().link_type))
        del lNode

    match value:
        case OperatorsEnum.NOT.value:
            node = solve_not(node)
        case OperatorsEnum.AND.value:
            node = solve_addition(node)
        case OperatorsEnum.OR.value:
            node = solve_or(node)
        case OperatorsEnum.XOR.value:
            node = solve_xor(node)
        case _:
            raise ValueError(f"Unknown operator: {value}")
    return node


def solve_query(query):
    if Facts[query] is True or Facts[query] is None:
        print(f"{query} is {Facts[query]}")
        return
    parent_node = Node(NodeTypes.FACT, query)
    tree = make_tree(parent_node)
    tree = solve_fact_node(tree)
    print(f"{query} is {Facts[query]}")


def solve_queries():
    for query in Queries:
        # print(f"query: {query}")
        solve_query(query)


if __name__ == "__main__":
    if len(sys.argv) != 2:
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
