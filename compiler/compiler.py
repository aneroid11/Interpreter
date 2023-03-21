from lexer import Lexer
from parser import Parser


def print_table(table):
    sz = len(table)

    for i in range(sz):
        print(f"{i}: {table[i]}")


class Compiler:
    def __init__(self, program_name: str):
        self._program_name = program_name

        self._identifiers_table = []
        self._keywords_table = []
        self._operators_table = []
        self._constants_table = []

        self._tokens_list = []

    def do_lexical_analysis(self):
        lexer = Lexer(self._program_name,
                      self._identifiers_table,
                      self._keywords_table,
                      self._operators_table,
                      self._constants_table)
        self._tokens_list = lexer.split_program_into_tokens()

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

    def do_syntax_analysis(self):
        parser = Parser(self._tokens_list,
                        self._operators_table,
                        self._identifiers_table,
                        self._keywords_table,
                        self._constants_table)
        parser.create_syntax_tree()
        print("\nSYNTAX TREE")
        parser.print_syntax_tree()
