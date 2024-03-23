from enum import Enum, auto

from exceptions import UnexpectedTokenError, UnrecognizedTokenError
from tokenizer import TOKEN_TYPE, Token, Tokens

class AST_NODE_TYPE(Enum):
    EXIT = auto()
    PRINT = auto()

class ASTNode:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self) -> str:
        if self.value is not None:
            return f"ASTNode({self.type}, {self.value})"

        return f"ASTNode({self.type})"

class Parser:
    def __init__(self, tokens: Tokens):
        self.tokens = tokens.get_tokens()
        self.current = 0
        self.nodes = []

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
        self.nodes = []
        while self.current_token().type != TOKEN_TYPE.END_OF_FILE:
            if self.current_token().type == TOKEN_TYPE.EXIT:
                self.nodes.append(self.parse_exit())
            elif self.current_token().type == TOKEN_TYPE.PRINT:
                self.nodes.append(self.parse_print())
            else:
                UnrecognizedTokenError(f"Unrecognized Token Type {self.current_token().type}").raise_err()
            
        return self.nodes
    
    def parse_print(self):
        self.consume(TOKEN_TYPE.PRINT)
        self.consume(TOKEN_TYPE.OPEN_PARENTHESES)
        print_string = self.current_token().value
        self.consume(TOKEN_TYPE.CONST_STRING)
        self.consume(TOKEN_TYPE.CLOSE_PARENTHESES)
        self.consume(TOKEN_TYPE.SEMICOLON)
        return ASTNode(AST_NODE_TYPE.PRINT, str(print_string))

    def parse_exit(self):
        self.consume(TOKEN_TYPE.EXIT)
        self.consume(TOKEN_TYPE.OPEN_PARENTHESES)
        exit_code = self.current_token().value
        self.consume(TOKEN_TYPE.INTEGER)
        self.consume(TOKEN_TYPE.CLOSE_PARENTHESES)
        self.consume(TOKEN_TYPE.SEMICOLON)
        return ASTNode(AST_NODE_TYPE.EXIT, int(exit_code))
