from typing import List


class Lexer:
    # types of tokens
    INT, DOUBLE, BOOL, STRING, WHILE, FOR, IF, ELSE, SWITCH, CASE, BREAK, DEFAULT,\
        SCAN, PRINT, ATOI, ATOB, ATOF, TO_STRING, TRUE, FALSE, PLUS, MINUS, MULT, DIV, MOD, \
        COMMA, SEMICOLON, LBRACKET, RBRACKET, LBRACE, RBRACE, EQUAL, LESS, MORE, AND, OR, NOT, \
        IDENTIFIER, NUM_INT, NUM_DOUBLE = range(40)

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

    class NoMoreTokens(Exception):
        pass

    class Token:
        def __init__(self, tp=None, vl=None):
            self.type = tp
            self.value = vl

    def __init__(self, file_name: str):
        with open(file_name) as f:
            self._program_text = f.read()

        self._curr_symbol_index = 0
        self._text_len = len(self._program_text) - 1  # EOF in the end?

    def get_curr_symbol(self) -> str:
        return self._program_text[self._curr_symbol_index]

    def next_symbol(self):
        self._curr_symbol_index += 1

    def program_finished(self) -> bool:
        return self._curr_symbol_index >= self._text_len

    def get_next_token(self) -> Token:
        if self.program_finished():
            raise Lexer.NoMoreTokens()

        curr_sym = self.get_curr_symbol()

        if curr_sym in Lexer.SPECIAL_SYMBOLS.keys():
            next_tok = Lexer.Token(Lexer.SPECIAL_SYMBOLS[curr_sym], None)
        else:
            next_tok = Lexer.Token(Lexer.INT, curr_sym)

        self.next_symbol()
        return next_tok

    def split_program_into_tokens(self) -> List[Token]:
        ret = []

        while True:
            try:
                ret.append(self.get_next_token())
            except Lexer.NoMoreTokens:
                break

        return ret


def main():
    lexer = Lexer("program.cmm")
    tokens: List[Lexer.Token] = lexer.split_program_into_tokens()

    for tok in tokens:
        print(tok.type)
        print(tok.value)
        print()


if __name__ == "__main__":
    main()
