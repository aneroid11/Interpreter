from lexer import Lexer
from typing import List


def main():
    lexer = Lexer("program.cmm")
    tokens, symbol_table = lexer.split_program_into_tokens()

    print("TOKENS\n")
    for tok in tokens:
        print(f"{tok.type}\n{tok.value}\n")

    print("SYMBOL TABLE\n")
    for sym in symbol_table:
        print(f"name: {sym.identifier}, scope: {sym.scope}, data type: {sym.data_type}")

    """experiment_string = ""
    experiment_string += "hello"
    experiment_string += "\\"
    experiment_string += "n"
    experiment_string += "world"
    print("\nexperiment string:")
    print(bytes(experiment_string, "utf-8").decode("unicode_escape"))"""


if __name__ == "__main__":
    main()
