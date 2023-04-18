from working_with_syntax_tree import WorkingWithSyntaxTree
from parser import Parser


class Interpreter(WorkingWithSyntaxTree):
    def __init__(self, parser_nodes: list, operators: list, identifiers: list, keywords: list,
                 consts: list, syntax_tree):
        super().__init__(parser_nodes, operators, identifiers, keywords, consts, syntax_tree)

    def _run_program(self, prog_node: Parser.Node):
        for stmt_node in prog_node.children:
            if self._is_keyword(stmt_node, "print"):
                print("execute print statement")

    def run_program(self):
        self._run_program(self._syntax_tree)
