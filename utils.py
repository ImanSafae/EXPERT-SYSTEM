import string
from Rule import Rule


class Utils:
    authorized_symbols = "!=><+|^()?# "

    @staticmethod
    def resolve_fact(Facts, fact, status):
        if status is not True and status is not False and status is not None:
            raise ValueError("Status must be True, False, or None")
        Facts[fact] = status

    @staticmethod
    def get_associated_rules(rules, fact):
        associated_rules = []
        for rule in rules:
            conclusion = rule.get_conclusion()
            if conclusion.get_fact() == fact:
                associated_rules.append(rule)
        return associated_rules

    @staticmethod
    def remove_query(queries, query_to_remove):
        return [query for query in queries if query != query_to_remove]

    @staticmethod
    def remove_comments(line):
        if ('#' in line):
            line = line.split("#")
            line = line[0]
        return line

    @staticmethod
    def is_string_valid(line):
        for char in line:
            if ((char not in string.ascii_letters)
                    and (char not in Utils.authorized_symbols)):
                print(f"Invalid character found: {char}")
                return False
        return True

    @staticmethod
    def is_rule_valid(rule):
        if (("<=>" not in rule) and ("=>" not in rule)):
            return False
        if (not rule[0].isalpha()):
            return False
        if (rule.isalpha()):
            return False
        return True

    @staticmethod
    def is_char(char):
        return char.isalpha() and len(char) == 1

    @staticmethod
    def find_associated_rules(query: str, Rules: list[Rule]):
        if not Utils.is_char(query):
            raise TypeError("""Wrong argument: expected a
                    character and an array of Rule objects.""")
        associated_rules = []
        for rule in Rules:
            if (query in rule.conclusions):
                associated_rules.append(rule)
                continue
        return associated_rules

    @staticmethod
    def find_all_indexes(str, char):
        indexes = []
        for i in range(len(str)):
            if str[i] == char:
                indexes.append(i)
        return indexes
