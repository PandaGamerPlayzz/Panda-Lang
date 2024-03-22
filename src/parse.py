from enum import Enum, auto

from exceptions import UnexpectedTokenError
from tokenizer import TOKEN_TYPE, Token, Tokens

class AST_NODE_TYPE(Enum):
    EXIT = auto()

class ASTNode:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

class Parser:
    def __init__(self, tokens: Tokens):
        self.tokens = tokens.get_tokens()
        self.current = 0

    def current_token(self):
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        else:
            return Token(TOKEN_TYPE.END_OF_FILE)

    def consume(self, expected_type):
        if self.current_token().type == expected_type:
            self.current += 1
        else:
            UnexpectedTokenError(f"Expected {expected_type}, but got {self.current_token().type}").raise_err()

    def parse(self):
        nodes = []
        while self.current_token().type != TOKEN_TYPE.END_OF_FILE:
            if self.current_token().type == TOKEN_TYPE.EXIT:
                nodes.append(self.parse_exit())
            else:
                SyntaxError("Syntax Error").raise_err()
            
        return nodes

    def parse_exit(self):
        self.consume(TOKEN_TYPE.EXIT)
        self.consume(TOKEN_TYPE.OPEN_PARENTHESES)
        exit_code = self.current_token().value
        self.consume(TOKEN_TYPE.INTEGER)
        self.consume(TOKEN_TYPE.CLOSE_PARENTHESES)
        self.consume(TOKEN_TYPE.SEMICOLON)
        return ASTNode(AST_NODE_TYPE.EXIT, int(exit_code))
