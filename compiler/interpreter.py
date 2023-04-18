from parser import Parser


class Interpreter:
    def __init__(self, parser_nodes: list, operators: list, identifiers: list, keywords: list,
                 consts: list, syntax_tree):
        self._parser_nodes = parser_nodes
        self._operators = operators
        self._identifiers = identifiers
        self._keywords = keywords
        self._consts = consts
        self._syntax_tree = syntax_tree

    def _run_program(self, prog_node: Parser.Node):
        for stmt_node in prog_node.children:
            if stmt_node.table == self._keywords and stmt_node.table[stmt_node.index_in_table] == "print":
                print("execute print statement")

    def run_program(self):
        self._run_program(self._syntax_tree)
