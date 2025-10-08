from enum import Enum


class OperatorsEnum(Enum):
    AND = "+"
    OR = "|"
    NOT = "!"
    XOR = "^"


class TokensEnum(Enum):
    LETTER = 1
    OPERATOR_AND = 2
    OPERATOR_OR = 3
    OPERATOR_NOT = 4
    OPERATOR_XOR = 5
    PARENTHESIS_OPEN = 6
    PARENTHESIS_CLOSED = 7


class RelationEnum(Enum):
    IMPLICATION = "=>"
    BICONDITIONAL = "<=>"
