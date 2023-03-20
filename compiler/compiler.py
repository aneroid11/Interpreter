from lexer import Lexer


def print_table(table):
    sz = len(table)

    for i in range(sz):
        print(f"{i}: {table[i]}")


class Compiler:
    def __init__(self, program_name: str):
        self._identifiers_table = []
        self._keywords_table = []
        self._operators_table = []
        self._constants_table = []

        self._lexer = Lexer(program_name,
                            self._identifiers_table,
                            self._keywords_table,
                            self._operators_table,
                            self._constants_table)
        self._tokens_list = None

    def do_lexical_analysis(self):
        self._tokens_list = self._lexer.split_program_into_tokens()

        print("KEYWORDS")
        print_table(self._keywords_table)

        print("\nIDENTIFIERS")
        print_table(self._identifiers_table)

        print("\nCONSTANTS")
        print_table(self._constants_table)

        print("\nOPERATORS")
        print_table(self._operators_table)

        print("\nTOKENS LIST\n")

        for tok in self._tokens_list:
            if tok.table is self._operators_table:
                tp = "operator"
            elif tok.table is self._constants_table:
                tp = "constant"
            elif tok.table is self._keywords_table:
                tp = "keyword"
            else:
                tp = "identifier"

            print(f"[{tp}, {tok.index_in_table}], ({tok.line}, {tok.index})", end="\n")