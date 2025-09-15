from enums import TokensEnum


class Rule:
    conditions = []
    conclusions = []
    relation = ""

    condition_tokens = []
    conclusion_tokens = []

    def __init__(self, conditions, conclusions, relation):
        relation = relation.lower()
        if (relation != "implies") and (relation != "if and only if"):
            raise TypeError("Cannot instanciate class: wrong relation format. Please only use `implies` or `if and only if`.")
        self.conditions = conditions
        self.conclusions = conclusions
        self.relation = relation


        condition_tokens = self.tokenize(conditions)
        # print(f"tokens for {conditions}: {condition_tokens}")
        # is_condition_valid = self.validate_rule(condition_tokens)
        # print("valid tokens?", is_condition_valid)
        if (not self.validate_rule(condition_tokens)):
            raise ValueError(f"Wrong condition format: {conditions}")
        self.condition_tokens = condition_tokens

        conclusion_tokens = self.tokenize(conclusions)
        # print(f"tokens for {conclusions}: {conclusion_tokens}")
        # is_conclusion_valid = validate_rule(conclusion_tokens)
        # print("valid tokens?", is_conclusion_valid)
        if (not self.validate_rule(conclusion_tokens)):
            raise ValueError(f"Wrong conclusion format: {conclusions}") 
        self.conclusion_tokens = conclusion_tokens

    def get_conditions(self):
        return self.conditions

    def get_conclusions(self):
        return self.conclusions

    def __str__(self):
        return f"{self.conditions}{self.relation}{self.conclusions}"
    
    @staticmethod
    def tokenize(str):
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
                raise ValueError(f"Unexpected character found in rule: [{char}].")
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
                if (token[0] != TokensEnum.LETTER) and (token[0] != TokensEnum.PARENTHESIS_CLOSED):
                    return False
            elif token[0] == TokensEnum.LETTER:
                if previous_token != None and (previous_token[0] == TokensEnum.LETTER or previous_token[0] == TokensEnum.PARENTHESIS_CLOSED):
                    return False
            elif token[0] == TokensEnum.PARENTHESIS_OPEN:
                open_parenthesis_counter += 1
                if (previous_token!= None and (previous_token[0] == TokensEnum.LETTER or previous_token[0] == TokensEnum.PARENTHESIS_CLOSED)):
                    return False
            elif token[0] == TokensEnum.PARENTHESIS_CLOSED:
                closed_parenthesis_counter += 1
                if (previous_token is None or previous_token[0] != TokensEnum.LETTER):
                    return False
            elif token[0] == TokensEnum.OPERATOR_NOT:
                if (previous_token != None and (previous_token[0] == TokensEnum.LETTER or previous_token[0] == TokensEnum.PARENTHESIS_CLOSED)):
                    return False
            elif token[0] == TokensEnum.OPERATOR_AND or token[0] == TokensEnum.OPERATOR_OR or token[0] == TokensEnum.OPERATOR_XOR:
                if (previous_token is None or (previous_token[0] != TokensEnum.LETTER and previous_token[0] != TokensEnum.PARENTHESIS_CLOSED)):
                    return False
            previous_token = token
        if (open_parenthesis_counter != closed_parenthesis_counter):
            return False
        return True