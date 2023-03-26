from compiler import Compiler


def main():
    # print(0 == 0.0)

    c = Compiler("program.cmm")
    c.do_lexical_analysis()
    c.do_syntax_analysis()
    c.do_semantic_analysis()


if __name__ == "__main__":
    main()
