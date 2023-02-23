from typing import List, Tuple
from symbol import Symbol
import sys


class Lexer:
    # types of tokens
    INT, DOUBLE, BOOL, STRING, WHILE, FOR, IF, ELSE, SWITCH, CASE, BREAK, DEFAULT,\
        SCAN, PRINT, ATOI, ATOB, ATOF, TO_STRING, TRUE, FALSE, PLUS, MINUS, MULT, DIV, MOD, \
        COMMA, SEMICOLON, LBRACKET, RBRACKET, LBRACE, RBRACE, EQUAL, LESS, MORE, AND, OR, NOT, \
        IDENTIFIER, NUM_INT, NUM_DOUBLE, STRING_LITERAL = range(41)

    WHITESPACES = (' ', '\t', '\n')

    SPECIAL_SYMBOLS = {
        '+': PLUS,
        '-': MINUS,
        '*': MULT,
        '/': DIV,
        '%': MOD,
        ',': COMMA,
        ';': SEMICOLON,
        '(': LBRACKET,
        ')': RBRACKET,
        '{': LBRACE,
        '}': RBRACE,
        '=': EQUAL,
        '<': LESS,
        '>': MORE,
        '&': AND,
        '|': OR,
        '!': NOT
    }

    KEYWORDS = {
        "int": INT,
        "double": DOUBLE,
        "bool": BOOL,
        "string": STRING,
        "while": WHILE,
        "for": FOR,
        "if": IF,
        "else": ELSE,
        "switch": SWITCH,
        "case": CASE,
        "break": BREAK,
        "default": DEFAULT,
        "scan": SCAN,
        "print": PRINT,
        "atoi": ATOI,
        "atob": ATOB,
        "atof": ATOF,
        "to_string": TO_STRING,
        "true": TRUE,
        "false": FALSE
    }

    class NoMoreTokens(Exception):
        pass

    class LexerError(Exception):
        def __init__(self, message, line: int, index: int):
            self.message = message
            self.line = line
            self.index = index
            super().__init__(message)

    class QuotesNotClosed(LexerError):
        def __init__(self, line: int, index: int):
            self.message = "quotes not closed"
            self.line = line
            self.index = index
            super().__init__(self.message, line, index)

    class UnknownSymbol(LexerError):
        def __init__(self, symbol: str, line: int, index: int):
            self.line = line
            self.index = index
            self.message = "unknown symbol: " + symbol
            super().__init__(self.message, line, index)

    class Token:
        def __init__(self, tp=None, vl=None):
            self.type = tp
            self.value = vl

    def __init__(self, file_name: str):
        with open(file_name) as f:
            self._program_text = f.read()

        self._curr_symbol_index = 0
        self._curr_line = 1
        self._curr_index_in_line = 1
        self._text_len = len(self._program_text) - 1  # EOF in the end?

        # print("END SYMBOL: " + str(ord(self._program_text[self._text_len])))

    def get_curr_symbol(self) -> str:
        return self._program_text[self._curr_symbol_index]

    def next_symbol(self):
        self._curr_symbol_index += 1

        if not self.program_finished():
            self._curr_index_in_line += 1

            if self.get_curr_symbol() == '\n':
                self._curr_line += 1
                self._curr_index_in_line = 0

    def program_finished(self) -> bool:
        return self._curr_symbol_index >= self._text_len

    def get_next_token(self) -> Token:
        # get the WHOLE TOKEN
        if self.program_finished():
            raise Lexer.NoMoreTokens()

        curr_sym = self.get_curr_symbol()
        while curr_sym in Lexer.WHITESPACES:
            self.next_symbol()
            curr_sym = self.get_curr_symbol()

            if self.program_finished():
                raise Lexer.NoMoreTokens()

        # print("curr_sym = " + curr_sym)

        if curr_sym in Lexer.SPECIAL_SYMBOLS.keys():
            next_tok = Lexer.Token(Lexer.SPECIAL_SYMBOLS[curr_sym], None)
            self.next_symbol()
        elif curr_sym.isalpha():
            # read a 'word'
            word = curr_sym
            self.next_symbol()
            curr_sym = self.get_curr_symbol()

            while (curr_sym.isalnum() or curr_sym == '_') and not self.program_finished():
                word += curr_sym
                self.next_symbol()
                curr_sym = self.get_curr_symbol()

            # we have the word. what to do now?
            if word in Lexer.KEYWORDS.keys():
                # keyword
                next_tok = Lexer.Token(Lexer.KEYWORDS[word], None)
            else:
                # identifier
                next_tok = Lexer.Token(Lexer.IDENTIFIER, word)
        elif curr_sym == '"':
            # string literal
            # next_tok = Lexer.Token(Lexer.STRING_LITERAL, "some raw string here")
            first_quote_line = self._curr_line
            first_quote_index_in_line = self._curr_index_in_line
            string_literal = ""

            while True:
                self.next_symbol()
                if self.program_finished():
                    raise Lexer.QuotesNotClosed(first_quote_line, first_quote_index_in_line)

                curr_sym = self.get_curr_symbol()

                if curr_sym == '\\':
                    self.next_symbol()
                    if self.program_finished():
                        raise Lexer.QuotesNotClosed(first_quote_line, first_quote_index_in_line)
                    curr_sym = self.get_curr_symbol()
                    string_literal += '\\' + curr_sym
                    continue

                if curr_sym == '"':
                    self.next_symbol()
                    break

                string_literal += curr_sym

            next_tok = Lexer.Token(Lexer.STRING_LITERAL, string_literal)
        elif curr_sym.isdigit():
            num_str = ""
            has_dot = False

            while True:
                num_str += curr_sym
                self.next_symbol()
                if self.program_finished():
                    break

                curr_sym = self.get_curr_symbol()

                if not curr_sym.isdigit() and curr_sym != '.':
                    break
                if curr_sym == '.':
                    if not has_dot:
                        has_dot = True
                    else:
                        break

            if has_dot:
                next_tok = Lexer.Token(Lexer.NUM_DOUBLE, num_str)
            else:
                next_tok = Lexer.Token(Lexer.NUM_INT, num_str)
        else:
            raise Lexer.UnknownSymbol(curr_sym, self._curr_line, self._curr_index_in_line)

        return next_tok

    def create_symbol_table(self, tokens: List[Token]) -> List[Symbol]:
        # change the list of tokens so the value for identifiers will be an index in the symbol table
        return []

    def split_program_into_tokens(self) -> Tuple[List[Token], List[Symbol]]:
        ret = []

        while True:
            try:
                ret.append(self.get_next_token())
            except Lexer.NoMoreTokens:
                break
            except Lexer.LexerError as err:
                print(f"LEXER ERROR:\n\t{err.message} ({err.line}:{err.index})")
                sys.exit(1)

        symbol_table = self.create_symbol_table(ret)
        return ret, symbol_table
    