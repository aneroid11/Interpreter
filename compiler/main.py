from compiler import Compiler


# def create_array(sizes: tuple):
#     if len(sizes) == 0:
#         return 0
#     return [create_array(sizes[1:])] * sizes[0]

def main():
    # arr = create_array((3, 3, 3))
    # print(arr[0][0])
    # exit(1)

    c = Compiler("program.cpm")
    c.do_lexical_analysis()
    c.do_syntax_analysis()
    c.do_semantic_analysis()
    c.run_program()


if __name__ == "__main__":
    main()
