import os
from enum import Enum, auto

from exceptions import UnrecognizedTokenError

class TOKEN_TYPE(Enum):
    # Data Types
    INTEGER = auto() # Example: 123
    FLOAT = auto() # Example: 1.23

    # Symbols
    OPEN_PARENTHESES = auto() # (
    CLOSE_PARENTHESES = auto() # )
    OPEN_CURLY_BRACKET = auto() # {
    CLOSE_CURLY_BRACKET = auto() # }
    OPEN_BRACKET = auto() # [
    CLOSE_BRACKET = auto() # ]
    SEMICOLON = auto() # ;

    # Math Symbols
    PLUS = auto() # +
    MINUS = auto() # -
    MULTIPLY = auto() # *
    DIVIDE = auto() # /

    # Key words
    LET = auto()
    VAR = auto()

    # Built ins
    EXIT = auto()

    # Other
    END_OF_FILE = auto()

class Token:
    def __init__(self, type_, value=None) -> None:
        self.type = type_
        self.value = value
    
    def __repr__(self) -> str:
        if self.value is not None:
            return f"Token({self.type}, {self.value})"

        return f"Token({self.type})"

class Tokens:
    def __init__(self) -> None:
        self.tokens = []

    def add_token(self, token: Token) -> None:
        self.tokens.append(token)

    def get_tokens(self) -> list[Token]:
        return self.tokens
    
    def __iter__(self):
        return iter(self.tokens)

class Tokenizer:
    def __init__(self) -> None:
        self.tokens = Tokens()
        self.single_character_handlers = {
            '(': self.gen_handler(TOKEN_TYPE.OPEN_PARENTHESES),
            ')': self.gen_handler(TOKEN_TYPE.CLOSE_PARENTHESES),
            '{': self.gen_handler(TOKEN_TYPE.OPEN_CURLY_BRACKET),
            '}': self.gen_handler(TOKEN_TYPE.CLOSE_CURLY_BRACKET),
            '[': self.gen_handler(TOKEN_TYPE.OPEN_BRACKET),
            ']': self.gen_handler(TOKEN_TYPE.CLOSE_BRACKET),
            ';': self.gen_handler(TOKEN_TYPE.SEMICOLON),
        }
        self.multi_character_handlers = {
            'exit': self.gen_handler(TOKEN_TYPE.EXIT, word_length=4),
        }

    def peek_characters(self, raw_source, current_index, number_of_characters):
        return raw_source[current_index:current_index + number_of_characters]

    def tokenize(self, source: str) -> Tokens:
        raw_source = source
        if os.path.exists(source):
            with open(source, 'r') as f: 
                raw_source = f.read()

        i = 0
        while i < len(raw_source):
            current_index = i

            for seq, handler in self.multi_character_handlers.items():
                if raw_source[i:i+len(seq)] == seq:
                    i = handler(raw_source, i)
                    break
            else:
                char = raw_source[i]
                if char in self.single_character_handlers:
                    i = self.single_character_handlers[char](raw_source, i)
                elif char.isdigit():
                    i = self.handle_number(raw_source, i)
                elif char.isspace():
                    i += 1
                else:
                    i = self.handle_unrecognized(raw_source, i)

            if i == current_index:
                line_info = self.find_line_info(raw_source, i)
                UnrecognizedTokenError(message=f'Tokenizer was not able to make progress with "{raw_source[i]}" encountered at {line_info[0]}:{line_info[1]}').raise_err()

        self.tokens.add_token(Token(TOKEN_TYPE.END_OF_FILE))

        return self.tokens
    
    def gen_handler(self, token_type: TOKEN_TYPE, word_length: int = 1):
        def handler(raw_source, i):
            self.tokens.add_token(Token(token_type))
            return i + word_length

        return handler

    def handle_open_parentheses(self, raw_source, i):
        self.tokens.add_token(Token(TOKEN_TYPE.OPEN_PARENTHESES))
        return i + 1

    def handle_close_parentheses(self, raw_source, i):
        self.tokens.add_token(Token(TOKEN_TYPE.CLOSE_PARENTHESES))
        return i + 1

    def handle_open_curly_bracket(self, raw_source, i):
        self.tokens.add_token(Token(TOKEN_TYPE.OPEN_CURLY_BRACKET))
        return i + 1

    def handle_close_curly_bracket(self, raw_source, i):
        self.tokens.add_token(Token(TOKEN_TYPE.CLOSE_CURLY_BRACKET))
        return i + 1

    def handle_open_bracket(self, raw_source, i):
        self.tokens.add_token(Token(TOKEN_TYPE.OPEN_BRACKET))
        return i + 1

    def handle_close_bracket(self, raw_source, i):
        self.tokens.add_token(Token(TOKEN_TYPE.CLOSE_BRACKET))
        return i + 1

    def handle_semicolon(self, raw_source, i):
        self.tokens.add_token(Token(TOKEN_TYPE.SEMICOLON))
        return i + 1
    
    def handle_number(self, raw_source, i):
        num_str = raw_source[i]
        is_float = False
        while i + 1 < len(raw_source) and (raw_source[i + 1].isdigit() or raw_source[i + 1] == '.' or raw_source[i + 1] == '_'):
            i += 1

            if raw_source[i] == '_': 
                continue
            elif raw_source[i] == '.' and is_float == True: 
                lineInfo = self.find_line_info(raw_source, i)
                UnrecognizedTokenError(message=f'Unrecognized token "{raw_source[i]}" encountered at {lineInfo[0]}:{lineInfo[1]}').raiseErr()
            elif raw_source[i] == '.': 
                is_float = True
            num_str += raw_source[i]

        self.tokens.add_token(Token(is_float and TOKEN_TYPE.FLOAT or TOKEN_TYPE.INTEGER, (is_float and float or int)(num_str)))
        return i + 1
    
    def handle_exit(self, raw_source, i):
        self.tokens.add_token(Token(TOKEN_TYPE.EXIT))
        return i + 4

    def handle_unrecognized(self, raw_source, i):
        line_info = self.find_line_info(raw_source, i)
        UnrecognizedTokenError(message=f'Unrecognized token "{raw_source[i]}" encountered at {line_info[0]}:{line_info[1]}').raise_err()
        return i + 1
    
    def find_line_info(self, raw_source, index) -> tuple[int]:
        """
        Find the line number and column position for a given index in the source string.

        :param raw_source: The complete source code as a string.
        :param index: The index in the source code for which to find line and column.
        :return: A tuple containing the line number and column position.
        """
        line_number = 1  # Lines start at 1
        line_start = 0  # Index where the current line starts

        for i, char in enumerate(raw_source):
            if i == index:
                column = index - line_start
                return line_number, column + 1  # +1 since columns start at 1
            elif char == '\n':
                line_number += 1
                line_start = i + 1  # The next line starts after the newline character

        return -1, -1
