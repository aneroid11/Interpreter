from typing import List
from constant import Constant
from variable import Variable
from warnings import filterwarnings
import sys

filterwarnings("error")


def append_if_not_in(table, element):
    if element not in table:
        table.append(element)


class Lexer:
    WHITESPACES = (' ', '\t', '\n')

    SPECIAL_SYMBOLS = ['+', '-', '*', '/', '%', ',', ':', ';', '(', ')', '[', ']',
                       '{', '}', '=', '==', '<', '<=', '>', '>=', '&&', '||', '!', '!=']

    KEYWORDS = [
        "int",
        "double",
        "bool",
        "string",
        "while",
        "for",
        "if",
        "else",
        "switch",
        "case",
        "break",
        "default",
        "scan",
        "print",
        "atoi",
        "atob",
        "atof",
        "to_string",
        "true",
        "false"
    ]

    class NoMoreTokens(Exception):
        pass

    class LexerError(Exception):
        def __init__(self, message, line: int, index: int):
            self.message = message
            self.line = line
            self.index = index
            super().__init__(message)

    class Expected(LexerError):
        def __init__(self, sym: str, line: int, index: int):
            super().__init__(f"'{sym}' expected", line, index)

    class InvalidEscapeSequence(LexerError):
        def __init__(self, msg: str, line: int, index: int):
            super().__init__(msg, line, index)

    class NoMatchingLeftBrace(LexerError):
        def __init__(self, line: int, index: int):
            super().__init__("no matching left brace", line, index)

    class QuotesNotClosed(LexerError):
        def __init__(self, line: int, index: int):
            super().__init__("quotes not closed", line, index)

    class UnknownSymbol(LexerError):
        def __init__(self, symbol: str, line: int, index: int):
            super().__init__("unknown symbol: " + symbol, line, index)

    class UnexpectedNumberEnding(LexerError):
        def __init__(self, sym: str, line: int, index: int):
            super().__init__(f"unexpected number ending: {sym}", line, index)

    class Token:
        def __init__(self, table, index_in_table: int, line: int, index: int):
            self.table = table
            self.index_in_table = index_in_table
            self.line = line
            self.index = index

        def value(self):
            return self.table[self.index_in_table]

    def __init__(self, file_name: str,
                 idents_table: list,
                 keywords_table: list,
                 operators_table: list,
                 constants_table: list):
        with open(file_name) as f:
            self._program_text = f.read() + " "  # + " " IS IMPORTANT!

        # print("PROGRAM:")
        # print(self._program_text)
        # print(self._program_text[0], end="")
        # print("END PROGRAM")

        self._curr_symbol_index = 0
        self._curr_line = 1
        self._curr_index_in_line = 1
        self._text_len = len(self._program_text) - 1  # - 1 IS IMPORTANT!
        # self._text_len = len(self._program_text)

        self._idents_table = idents_table
        self._keywords_table = keywords_table
        self._operators_table = operators_table
        self._constants_table = constants_table

    def get_curr_symbol(self) -> str:
        return self._program_text[self._curr_symbol_index]

    def next_symbol(self):
        if self.get_curr_symbol() == '\n':
            self._curr_line += 1
            self._curr_index_in_line = 0

        self._curr_symbol_index += 1

        if not self.program_finished():
            self._curr_index_in_line += 1

    def program_finished(self) -> bool:
        # print(self._curr_symbol_index)
        # print(self._text_len)
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

        if curr_sym in ('&', '|'):
            # the next symbol must be the same (we don't have bitwise operations)
            line, index = self._curr_line, self._curr_index_in_line
            op_sym = curr_sym
            self.next_symbol()
            curr_sym = self.get_curr_symbol()

            if self.program_finished() or curr_sym != op_sym:
                raise Lexer.Expected(op_sym, self._curr_line, self._curr_index_in_line)

            op_sym += curr_sym

            append_if_not_in(self._operators_table, op_sym)
            next_tok = Lexer.Token(self._operators_table, self._operators_table.index(op_sym), line, index)
            self.next_symbol()
        elif curr_sym in ('>', '<', '!', '='):
            line, index = self._curr_line, self._curr_index_in_line

            # there can be a '=' after this
            op_sym = curr_sym
            self.next_symbol()
            curr_sym = self.get_curr_symbol()

            if self.program_finished() or curr_sym != '=':
                append_if_not_in(self._operators_table, op_sym)
                next_tok = Lexer.Token(self._operators_table, self._operators_table.index(op_sym), line, index)
            else:
                op_sym += curr_sym
                append_if_not_in(self._operators_table, op_sym)
                next_tok = Lexer.Token(self._operators_table, self._operators_table.index(op_sym), line, index)
                self.next_symbol()
        elif curr_sym in Lexer.SPECIAL_SYMBOLS:
            line, index = self._curr_line, self._curr_index_in_line

            append_if_not_in(self._operators_table, curr_sym)
            next_tok = Lexer.Token(self._operators_table, self._operators_table.index(curr_sym), line, index)
            self.next_symbol()
        elif curr_sym.isalpha():
            line, index = self._curr_line, self._curr_index_in_line

            # read a 'word'
            word = curr_sym
            self.next_symbol()
            curr_sym = self.get_curr_symbol()

            while (curr_sym.isalnum() or curr_sym == '_') and not self.program_finished():
                word += curr_sym
                self.next_symbol()
                curr_sym = self.get_curr_symbol()

            # we have the word. what to do now?
            if word in Lexer.KEYWORDS:
                # keyword
                append_if_not_in(self._keywords_table, word)
                next_tok = Lexer.Token(self._keywords_table, self._keywords_table.index(word), line, index)
            else:
                # identifier
                # add WORD into the symbol table
                var = Variable(word, None, 0, 0)
                append_if_not_in(self._idents_table, var)
                next_tok = Lexer.Token(self._idents_table, self._idents_table.index(var), line, index)
        elif curr_sym == '"':
            # string literal
            # next_tok = Lexer.Token(Lexer.STRING_LITERAL, "some raw string here")
            line, index = self._curr_line, self._curr_index_in_line

            string_literal = ""

            while True:
                self.next_symbol()
                if self.program_finished():
                    raise Lexer.QuotesNotClosed(line, index)

                curr_sym = self.get_curr_symbol()

                if curr_sym == '\\':
                    self.next_symbol()
                    if self.program_finished():
                        raise Lexer.QuotesNotClosed(line, index)
                    curr_sym = self.get_curr_symbol()
                    string_literal += '\\' + curr_sym
                    continue

                if curr_sym == '"':
                    self.next_symbol()
                    break

                string_literal += curr_sym

            try:
                _ = bytes(string_literal, "utf-8").decode("unicode_escape")
            except DeprecationWarning as err:
                err_str = str(err)
                msg = err_str[err_str.find("invalid escape sequence"):-1]
                raise Lexer.InvalidEscapeSequence(msg, line, index)

            # next_tok = Lexer.Token(Lexer.STRING_LITERAL, string_literal, line, index)
            # append_if_not_in(self._constants_table, string_literal)
            const = Constant(string_literal, Constant.STRING)
            append_if_not_in(self._constants_table, const)
            next_tok = Lexer.Token(self._constants_table, self._constants_table.index(const), line, index)
        elif curr_sym.isdigit():
            line, index = self._curr_line, self._curr_index_in_line

            num_str = ""
            has_dot = False

            while True:
                num_str += curr_sym
                self.next_symbol()
                if self.program_finished():
                    break

                curr_sym = self.get_curr_symbol()

                if not curr_sym.isdigit() and curr_sym != '.':
                    if curr_sym.isalpha() or curr_sym == '_':
                        raise Lexer.UnexpectedNumberEnding(curr_sym, self._curr_line, self._curr_index_in_line)
                    break
                if curr_sym == '.':
                    if not has_dot:
                        has_dot = True
                    else:
                        break

            # append_if_not_in(self._constants_table, num_str)

            if has_dot:
                const = Constant(num_str, Constant.DOUBLE)
            else:
                const = Constant(num_str, Constant.INT)

            append_if_not_in(self._constants_table, const)
            next_tok = Lexer.Token(self._constants_table, self._constants_table.index(const), line, index)
        else:
            raise Lexer.UnknownSymbol(curr_sym, self._curr_line, self._curr_index_in_line)

        return next_tok

    def split_program_into_tokens(self) -> List[Token]:
        ret = []

        while True:
            try:
                ret.append(self.get_next_token())
            except Lexer.NoMoreTokens:
                break
            except Lexer.LexerError as err:
                print(f"LEXER ERROR:\n\t{err.message} ({err.line}:{err.index})")
                sys.exit(1)

        return ret
