from lexer import Lexer


class Compiler:
    def __init__(self, program_name: str):
        self.lexer = Lexer("program.cmm")

    def do_lexical_analysis(self):
        tokens = self.lexer.split_program_into_tokens()

        print("TOKENS\n")
        for tok in tokens:
            print(f"[{Lexer.TYPES_OF_TOKENS[tok.type]}, {tok.value}] {tok.line, tok.index}", end="\n")