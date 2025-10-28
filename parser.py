
from Rule import Rule
from enums import RelationEnum

def init_facts() -> dict[str, bool]:
    facts: dict[str, bool] = {}
    ord_a = ord("A")

    for i in range(26):
        letter = chr(ord_a + i)
        facts[letter] = False
    return facts

def parse_user_input(exp: str) -> tuple[dict[str, bool] | None, list[str] | None]:
    queries = None
    facts = None
    if exp.startswith('?'):
        queries = parse_query(exp)
    if exp.startswith('='):
        facts = init_facts()
        parse_facts(exp, facts)
    return facts, queries

def extract_rule(line) -> list[Rule]:
    rules: list[Rule] = []
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
        return []
    newRule = Rule(condition, conclusion, relation)
    rules.append(newRule)
    if relation == RelationEnum.BICONDITIONAL.value:
        reverseRule = Rule(conclusion, condition, relation)
        rules.append(reverseRule)
    return rules

def parse_query(exp: str) -> list[str]:
    queries: list[str] = []
    exp = exp[1:].strip()
    if len(exp) == 0:
        return []
    for index, query in enumerate(exp):
        if not query.isalpha():
            raise SyntaxError(f"Wrong query format found at index {index}: \"{query}\".")
        queries.append(query)
    return queries

def parse_facts(exp: str, facts: dict[str, bool]) -> None:
    exp = exp[1:].strip()
    if len(exp) != 0:
        for index, fact in enumerate(exp):
            if not fact.isalpha():
                raise SyntaxError(f"Wrong fact format found at index {index}: \"{fact}\".")
            facts[fact.upper()] = True

def parse(file: str) -> tuple[list[Rule], dict[str, bool], list[str]]:
    lines = file.split('\n')
    rules: list[Rule] = []
    queries: list[str] = []
    facts: dict[str, bool] = init_facts()
    have_init_facts = False
    have_query = False
    for line in lines:
        line = line.strip()
        if '#' in line:
            line = line.split('#')[0].strip()
        if line:
            if line.startswith('='):
                have_init_facts = True
                parse_facts(line, facts)
            elif line.startswith('?'):
                have_query = True
                queries.extend(parse_query(line))
            else:
                rules.extend(extract_rule(line))
    if not have_init_facts:
        raise SyntaxError("No initial facts provided.")
    if not have_query:
        raise SyntaxError("No queries provided.")
    return rules, facts, queries
            