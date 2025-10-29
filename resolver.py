
from Node import Node
from Rule import Rule
from enums import ChildLinkTypes, OperatorsEnum, NodeTypes

def eval_node(node: Node, facts: dict[str, bool]) -> tuple[bool, bool]:
    if node.type == NodeTypes.FACT:
        base_val = node.value if node.value is not None else facts.get(node.name)
        derived_vals: list[bool | None] = []
        contradiction = False
        for child in node.get_children():
            child_val, child_contra = eval_node(child, facts)
            if child_contra:
                contradiction = True
            if child.link_type == ChildLinkTypes.INVERTED and child_val is not None:
                child_val = not child_val
            derived_vals.append(child_val)

        derived_val: bool | None = None
        if derived_vals:
            has_true = any(v is True for v in derived_vals)
            has_false = any(v is False for v in derived_vals)
            if has_true and has_false:
                contradiction = True
            elif has_true:
                derived_val = True
            elif all(v is False for v in derived_vals):
                derived_val = False
            else:
                derived_val = None
        if base_val is not None and derived_val is not None and base_val != derived_val:
            contradiction = True
        final_val = base_val if base_val is not None else derived_val
        return final_val, contradiction

    elif node.type == NodeTypes.OPERATOR:
        left_val, left_contra = eval_node(node.left, facts)
        right_val, right_contra = eval_node(node.right, facts)
        contradiction = left_contra or right_contra

        if node.name == '+':
            if left_val is False or right_val is False:
                result = False
            elif left_val is True and right_val is True:
                result = True
            else:
                result = None
        elif node.name == '|':
            if left_val is True or right_val is True:
                result = True
            elif left_val is False and right_val is False:
                result = False
            else:
                result = None
        elif node.name == '^':
            if left_val is None or right_val is None:
                result = None
            else:
                result = left_val != right_val

        if node.link_type == ChildLinkTypes.INVERTED and result is not None:
            result = not result

        return result, contradiction

def find_associated_rules(query: str, rules: list[Rule]) -> list[Rule]:
    associated_rules = []
    for rule in rules:
        if (query in rule.conclusions):
            associated_rules.append(rule)
    return associated_rules

def tokenize(expr: str) -> list[str]:
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        elif c.isalpha():  # variable ou nombre
            val = c
            while i + 1 < len(expr) and expr[i + 1].isalpha():
                i += 1
                val += expr[i]
            tokens.append(val)
        elif c in "+|^()!":
            tokens.append(c)
        else:
            raise ValueError(f"Caractère invalide : {c}")
        i += 1
    return tokens

def parse_expression(expr: str, facts: dict[str, bool]) -> Node:
    tokens = tokenize(expr)

    precedence = {'+': 3, '|': 2, '^': 1}

    def parse_tokens(start=0, invert_fact=False, invert_op=False):
        values = []
        ops: list[tuple[str, bool]] = []
        i = start

        def apply_last_op():
            op, inv = ops.pop()
            right = values.pop()
            left = values.pop()
            node = Node(
                op,
                NodeTypes.OPERATOR,
                left=left,
                right=right,
                link_type=ChildLinkTypes.INVERTED if inv else ChildLinkTypes.DEFAULT,
            )
            values.append(node)

        while i < len(tokens):
            token = tokens[i]

            # gestion de la négation
            if token == '!' and i + 1 < len(tokens) and tokens[i + 1] == '(':
                invert_op = True
            elif token == '!' and i + 1 < len(tokens) and tokens[i + 1].isalpha():
                invert_fact = True

            elif token.isalpha():
                values.append(
                    Node(
                        token,
                        NodeTypes.FACT,
                        value=facts[token] if not invert_fact else (not facts[token]),
                        invert=invert_fact
                    )
                )
                invert_fact = False

            elif token == '(':
                subtree, j = parse_tokens(i + 1, invert_fact, invert_op)
                values.append(subtree)
                i = j

            elif token == ')':
                invert_op = False
                break

            elif token in "+|^":
                while ops and precedence[ops[-1][0]] >= precedence[token]:
                    apply_last_op()
                ops.append((token, invert_op))

            i += 1

        while ops:
            apply_last_op()

        return values[0], i

    tree, _ = parse_tokens()
    return tree

def make_tree(query: str, rules: list[Rule], facts: dict[str, bool]) -> Node:
    """
    Recursively extend a FACT node by finding associated rules and
    adding their condition trees as children until no more expansions
    are possible. Protects against cycles using the `seen` set and
    avoids re-expanding a fact that already has children.
    """
    parent = Node(query, NodeTypes.FACT, facts.get(query))
    seen = [] # for bidirectional search

    def find_children(query: str):
        associated_rules = find_associated_rules(query, rules)
        child = []
        for rule in associated_rules:
            if rule.__str__() in seen:
                continue
            if '<=>' in rule.__str__() and rule.__str__() not in seen:
                seen.append(rule.__str__())
            new_child = parse_expression(rule.conditions, facts)
            if new_child.type == NodeTypes.FACT:
                new_child.children.extend(find_children(new_child.name))
            if new_child.type == NodeTypes.OPERATOR:
                for node in [new_child.left, new_child.right]:
                    if node.type == NodeTypes.FACT:
                        node.children.extend(find_children(node.name))
            child.append(new_child)
        return child
    
    parent.children.extend(find_children(query))
    return parent

def solve_condition(node: Node, type: OperatorsEnum):
    lvalue = node.left.value
    rvalue = node.right.value
    match type:
        case OperatorsEnum.AND:
            node.value = lvalue and rvalue
        case OperatorsEnum.OR:
            node.value = lvalue or rvalue
        case OperatorsEnum.XOR:
            node.value = lvalue ^ rvalue
        case OperatorsEnum.NOT:
            node.value = not node.value
    if node.link_type == ChildLinkTypes.INVERTED:
        node.value = not node.value

def solve_operator(node: Node) -> None:
    if node.left.type == NodeTypes.OPERATOR:
        solve_operator(node.left)
    else:
        resolve_tree(node.left)
    if node.right.type == NodeTypes.OPERATOR:
        solve_operator(node.right)
    else:
        resolve_tree(node.right)
    solve_condition(node, OperatorsEnum(node.name))


def resolve_tree(tree: Node) -> dict[str, bool]:
    for child in tree.get_children():
        if child.type == NodeTypes.OPERATOR:
            solve_operator(child)
        else:
            resolve_tree(child)
        if child.value is True:
            child.value = child.link_type == ChildLinkTypes.DEFAULT

    if len(tree.children) > 1:
        if any(child.value is True for child in tree.children):
            tree.value = True
    elif len(tree.children) == 1:
        tree.value = tree.children[0].value

def resolve(rules: list[Rule], facts: dict[str, bool], queries: list[str]) -> list[Node]:
    trees = []
    for query in queries:
        tree = make_tree(query, rules, facts)
        resolve_tree(tree)
        _, contradiction = eval_node(tree, facts)
        if contradiction:
            print("Contradiction found")
        trees.append(tree)
    return trees