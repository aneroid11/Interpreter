from compiler import Compiler


def main():
    c = Compiler("program.cpm")
    c.do_lexical_analysis()
    c.do_syntax_analysis()
    c.do_semantic_analysis()
    # c.run_program()


if __name__ == "__main__":
    main()
