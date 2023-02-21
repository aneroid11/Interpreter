from typing import List


class Lexer:
    # types of tokens
    INT, DOUBLE, BOOL, STRING, WHILE, FOR, IF, ELSE, SWITCH, CASE, BREAK, DEFAULT,\
        SCAN, PRINT, ATOI, ATOB, ATOF, TO_STRING, TRUE, FALSE, PLUS, MINUS, MULT, DIV, MOD, \
        COMMA, SEMICOLON, LBRACKET, RBRACKET, LBRACE, RBRACE, EQUAL, LESS, MORE, \
        IDENTIFIER, NUM_INT, NUM_DOUBLE = range(37)

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
        self._text_len = len(self._program_text)

    def get_next_token(self) -> Token:
        raise Lexer.NoMoreTokens()

    def split_program_into_tokens(self) -> List[Token]:
        ret = []

        while True:
            try:
                ret += self.get_next_token()
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
