from working_with_syntax_tree import WorkingWithSyntaxTree
from parser import Parser
from constant import Constant


class Interpreter(WorkingWithSyntaxTree):
    def __init__(self, parser_nodes: list, operators: list, identifiers: list, keywords: list,
                 consts: list, syntax_tree):
        super().__init__(parser_nodes, operators, identifiers, keywords, consts, syntax_tree)

    def _compute_string_constant(self, str_const_node: Parser.Node) -> str:
        str_to_print = str_const_node.value().value
        return bytes(str_to_print, "utf-8").decode("unicode_escape")

    def _interpret_scan(self) -> str:
        return input()

    def _compute_bool_expr(self, expr_node: Parser.Node) -> bool:
        if self._is_keyword(expr_node, ("true", "false")):
            return expr_node.value() == "true"
        elif self._is_operator(expr_node, '||'):
            return self._compute_bool_expr(expr_node.children[0]) or \
                   self._compute_bool_expr(expr_node.children[1])
        elif self._is_operator(expr_node, '&&'):
            return self._compute_bool_expr(expr_node.children[0]) and \
                   self._compute_bool_expr(expr_node.children[1])
        elif self._is_operator(expr_node, '!'):
            return not self._compute_bool_expr(expr_node.children[0])

        return False

    def _compute_bool_arithm_or_string_expr(self, expr_node: Parser.Node):
        if self._is_operator(expr_node, ('||', '&&', '!', '>', '<', '>=', '<=', '==', '!=')) or \
            self._is_keyword(expr_node, ("true", "false")):  # or \
            # self._is_identifier_of_type(expr_node, "bool"):
            return self._compute_bool_expr(expr_node)

        return "BAS_expr"

    def _interpret_to_string(self, to_str_node: Parser.Node) -> str:
        expr_result = self._compute_bool_arithm_or_string_expr(to_str_node.children[0])
        return str(expr_result)

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
        print(self._interpret_node(print_node.children[0]), end='')

    def _interpret_node(self, node: Parser.Node):
        if node.table is self._parser_nodes_tbl and node.value() == "program":
            for stmt_node in node.children:
                self._interpret_node(stmt_node)
        elif self._is_keyword(node, "print"):
            self._run_print(node)
        elif self._is_string_constant(node):
            return self._compute_string_constant(node)
        elif self._is_constant_of_type(node, Constant.INT):
            return int(node.value().value)
        elif self._is_constant_of_type(node, Constant.DOUBLE):
            return float(node.value().value)
        elif self._is_keyword(node, ("true", "false")):
            return node.value() == "true"
        elif self._is_keyword(node, "to_string"):
            return str(self._interpret_node(node.children[0]))
        else:
            print("UNKNOWN NODE!!!")
            exit(1)

    def run_program(self):
        print("\n\n\n\n\n")
        self._interpret_node(self._syntax_tree)
