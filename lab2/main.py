from lexer import Lexer
from typing import List


def main():
    lexer = Lexer("program.cmm")
    tokens: List[Lexer.Token] = lexer.split_program_into_tokens()

    for tok in tokens:
        print(tok.type)
        print(tok.value)
        print()

    """experiment_string = ""
    experiment_string += "hello"
    experiment_string += "\\"
    experiment_string += "n"
    experiment_string += "world"
    print("\nexperiment string:")
    print(bytes(experiment_string, "utf-8").decode("unicode_escape"))"""


if __name__ == "__main__":
    main()
