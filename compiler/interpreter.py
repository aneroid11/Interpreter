from working_with_syntax_tree import WorkingWithSyntaxTree
from parser import Parser
from constant import Constant


class Interpreter(WorkingWithSyntaxTree):
    def __init__(self, parser_nodes: list, operators: list, identifiers: list, keywords: list,
                 consts: list, syntax_tree):
        super().__init__(parser_nodes, operators, identifiers, keywords, consts, syntax_tree)

    def _compute_string_expression(self, expr_node: Parser.Node) -> str:
        if expr_node.table is self._consts_tbl and expr_node.value().type == Constant.STRING:
            str_to_print = expr_node.value().value
            return bytes(str_to_print, "utf-8").decode("unicode_escape")

        return "unknown string"

    def _run_print(self, print_node: Parser.Node):
        print(self._compute_string_expression(print_node.children[0]), end='')

    def _run_program(self, prog_node: Parser.Node):
        for stmt_node in prog_node.children:
            if self._is_keyword(stmt_node, "print"):
                self._run_print(stmt_node)

    def run_program(self):
        self._run_program(self._syntax_tree)
