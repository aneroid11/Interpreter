from lexer import Lexer
from typing import List
from warnings import filterwarnings

filterwarnings("error")


def main():
    """lexer = Lexer("program.cmm")
    tokens = lexer.split_program_into_tokens()

    print("TOKENS\n")
    for tok in tokens:
        print(f"[{Lexer.TYPES_OF_TOKENS[tok.type]}, {tok.value}] {tok.line, tok.index}", end="\n")"""

    """
    print("\n\nSYMBOL TABLE\n")
    idx = 0
    for sym in symbol_table:
        print(f"{idx}: name: {sym.identifier}, scope: {sym.scope}")
        idx += 1
    """

    """experiment_string = ""
    experiment_string += "hello"
    experiment_string += "\\"
    experiment_string += "n"
    experiment_string += "world"""
    experiment_string = "\h"

    try:
        print(bytes(experiment_string, "utf-8").decode("unicode_escape"))
    except DeprecationWarning as err:
        err_str = str(err)

        # display string from character 65
        print(err_str[err_str.find("invalid escape sequence"):-1])


if __name__ == "__main__":
    main()
