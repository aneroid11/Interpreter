from compiler import Compiler


def main():
    c = Compiler("program.cmm")
    c.do_lexical_analysis()


if __name__ == "__main__":
    main()
