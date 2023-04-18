from working_with_syntax_tree import WorkingWithSyntaxTree
from parser import Parser


class Interpreter(WorkingWithSyntaxTree):
    def __init__(self, parser_nodes: list, operators: list, identifiers: list, keywords: list,
                 consts: list, syntax_tree):
        super().__init__(parser_nodes, operators, identifiers, keywords, consts, syntax_tree)

    def _compute_string_constant(self, str_const_node: Parser.Node) -> str:
        str_to_print = str_const_node.value().value
        return bytes(str_to_print, "utf-8").decode("unicode_escape")

    def _interpret_scan(self) -> str:
        return input()

    def _interpret_to_string(self, to_str_node: Parser.Node) -> str:
        return "to_string_this"

    def _compute_string_expression(self, expr_node: Parser.Node) -> str:
        if self._is_string_constant(expr_node):
            return self._compute_string_constant(expr_node)
        elif self._is_operator(expr_node, '+'):
            return (self._compute_string_expression(expr_node.children[0]) +
                    self._compute_string_expression(expr_node.children[1]))
        elif self._is_keyword(expr_node, "scan"):
            return self._interpret_scan()
        elif self._is_keyword(expr_node, "to_string"):
            return self._interpret_to_string(expr_node)

        return "unknown string"

    def _run_print(self, print_node: Parser.Node):
        print(self._compute_string_expression(print_node.children[0]), end='')

    def _run_program(self, prog_node: Parser.Node):
        for stmt_node in prog_node.children:
            if self._is_keyword(stmt_node, "print"):
                self._run_print(stmt_node)

    def run_program(self):
        print("\n\n\n\n\n")
        self._run_program(self._syntax_tree)
