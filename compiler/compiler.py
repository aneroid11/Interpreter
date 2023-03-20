from lexer import Lexer


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

        print("TOKENS\n")

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
            # print(f"[{tok.table}, {tok.index_in_table}]", end="\n")
        # for tok in self.tokens_list:
        #     print(f"[{Lexer.TYPES_OF_TOKENS[tok.type]}, {tok.value}] {tok.line, tok.index}", end="\n")