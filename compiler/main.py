from lexer import Lexer
from typing import List


def main():
    lexer = Lexer("program.cmm")
    tokens = lexer.split_program_into_tokens()

    print("TOKENS\n")
    for tok in tokens:
        print(f"[{Lexer.TYPES_OF_TOKENS[tok.type]}, {tok.value}] {tok.line, tok.index}", end="\n")


if __name__ == "__main__":
    main()
