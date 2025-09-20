import string
from Rule import Rule

class Utils:
    authorized_symbols = "!=><+|^()?# "

    @staticmethod
    def resolve_fact(Facts, fact, status):
        if status != True and status != False and status != None:
            raise ValueError("Status must be True, False, or None")
        Facts[fact] = status

    @staticmethod
    def get_associated_rules(rules, fact):
        associated_rules = []
        for rule in rules:
            conclusion = rule.get_conclusion()
            # will depend on how rule is parsed and implemented
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
            if ((not char in string.ascii_letters) and (not char in Utils.authorized_symbols)):
                print(f"Invalid character found: {char}")
                return False
        return True

    @staticmethod    
    def is_rule_valid(rule):
        if ((not "<=>" in rule) and (not "=>" in rule)):
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
    def find_associated_rules(query, Rules):
        if (not (isinstance(Rules, list) and all(isinstance(r, Rule) for r in Rules))) or (not Utils.is_char(query)):
            raise TypeError("Wrong argument: expected a character and an array of Rule objects.")
        associated_rules = []
        for rule in Rules:
            if (query in rule.conclusions):
                associated_rules.append(rule)
                continue
            if (rule.relation == "if and only if" and query in rule.conditions):
                associated_rules.append(rule)
        return associated_rules
    
    @staticmethod
    def find_all_indexes(str, char):
        indexes = []
        for i in range(len(str)):
            if str[i] == char:
                indexes.append(i)
        return indexes
