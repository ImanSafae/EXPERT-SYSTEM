from enums import RelationEnum, TokensEnum


class Rule:
    conditions: str = ""
    conclusions: str = ""
    relation = ""

    condition_tokens = []
    conclusion_tokens = []

    def __init__(self, conditions: str, conclusions: str, relation: RelationEnum):
        relation = relation.lower()
        self.conditions = conditions.strip()
        self.conclusions = conclusions.strip()
        self.relation = relation

        condition_tokens = self.tokenize(conditions)
        if (not self.validate_rule(condition_tokens)):
            raise ValueError(f"Wrong condition format: {conditions}")
        self.condition_tokens = condition_tokens

        conclusion_tokens = self.tokenize(conclusions)
        if (not self.validate_rule(conclusion_tokens)):
            raise ValueError(f"Wrong conclusion format: {conclusions}")
        self.conclusion_tokens = conclusion_tokens

    def __str__(self):
        return f"{self.conditions}{self.relation}{self.conclusions}"

    @staticmethod
    def tokenize(str: str) -> list[tuple[TokensEnum, str]]:
        tokens = []
        str = str.strip()
        for char in str:
            if char.isspace():
                continue
            if char.isalpha():
                tokens.append((TokensEnum.LETTER, char))
            elif char == "^":
                tokens.append((TokensEnum.OPERATOR_XOR, char))
            elif char == "!":
                tokens.append((TokensEnum.OPERATOR_NOT, char))
            elif char == "(":
                tokens.append((TokensEnum.PARENTHESIS_OPEN, char))
            elif char == ")":
                tokens.append((TokensEnum.PARENTHESIS_CLOSED, char))
            elif char == "|":
                tokens.append((TokensEnum.OPERATOR_OR, char))
            elif char == "+":
                tokens.append((TokensEnum.OPERATOR_AND, char))
            else:
                raise ValueError(f"Unexpected character found in rule: {char}")
        return tokens

    @staticmethod
    def validate_rule(tokens):
        open_parenthesis_counter = 0
        closed_parenthesis_counter = 0
        previous_token = None

        for i in range(len(tokens)):
            token = tokens[i]
            if (not isinstance(token, tuple)):
                raise TypeError("Token should be a tuple.")
            if (i == len(tokens) - 1):
                if (token[0] is not TokensEnum.LETTER
                        and token[0] is not TokensEnum.PARENTHESIS_CLOSED):
                    return False
            elif token[0] == TokensEnum.LETTER:
                if (previous_token is not None and
                    (previous_token[0] == TokensEnum.LETTER or
                     previous_token[0] == TokensEnum.PARENTHESIS_CLOSED)):
                    return False
            elif token[0] == TokensEnum.PARENTHESIS_OPEN:
                open_parenthesis_counter += 1
                if (previous_token is not None and
                    (previous_token[0] == TokensEnum.LETTER or
                     previous_token[0] == TokensEnum.PARENTHESIS_CLOSED)):
                    return False
            if token[0] == TokensEnum.PARENTHESIS_CLOSED:
                closed_parenthesis_counter += 1
                if (previous_token is None or
                        previous_token[0] is not TokensEnum.LETTER):
                    return False
            elif token[0] == TokensEnum.OPERATOR_NOT:
                if (previous_token is not None and
                    (previous_token[0] == TokensEnum.LETTER or
                     previous_token[0] == TokensEnum.PARENTHESIS_CLOSED)):
                    return False
            elif (token[0] == TokensEnum.OPERATOR_AND or
                  token[0] == TokensEnum.OPERATOR_OR or
                  token[0] == TokensEnum.OPERATOR_XOR):
                if (previous_token is None or
                    (previous_token[0] is not TokensEnum.LETTER and
                     previous_token[0] is not TokensEnum.PARENTHESIS_CLOSED)):
                    return False
            previous_token = token
        if (open_parenthesis_counter != closed_parenthesis_counter):
            # print(open_parenthesis_counter, closed_parenthesis_counter)
            return False
        return True
