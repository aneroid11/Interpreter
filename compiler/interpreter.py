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
            ret = str(self._interpret_node(node.children[0]))
            if ret == "True":
                return "true"
            if ret == "False":
                return "false"
            return ret
        elif self._is_keyword(node, "atoi"):
            return int(self._interpret_node(node.children[0]))
        elif self._is_keyword(node, "atof"):
            return float(self._interpret_node(node.children[0]))
        elif self._is_keyword(node, "atob"):
            return bool(self._interpret_node(node.children[0]))
        elif self._is_keyword(node, "scan"):
            return input()
        elif self._is_operator(node, '+'):
            return self._interpret_node(node.children[0]) + self._interpret_node(node.children[1])
        elif self._is_operator(node, '-'):
            return self._interpret_node(node.children[0]) - self._interpret_node(node.children[1])
        elif self._is_operator(node, '*'):
            return self._interpret_node(node.children[0]) * self._interpret_node(node.children[1])
        elif self._is_operator(node, '/'):
            return self._interpret_node(node.children[0]) / self._interpret_node(node.children[1])
        elif self._is_operator(node, '%'):
            return self._interpret_node(node.children[0]) % self._interpret_node(node.children[1])
        elif self._is_operator(node, '&&'):
            return self._interpret_node(node.children[0]) and self._interpret_node(node.children[1])
        elif self._is_operator(node, '||'):
            return self._interpret_node(node.children[0]) or self._interpret_node(node.children[1])
        elif self._is_operator(node, '!'):
            return not self._interpret_node(node.children[0])
        elif self._is_operator(node, '>'):
            return self._interpret_node(node.children[0]) > self._interpret_node(node.children[1])
        elif self._is_operator(node, '<'):
            return self._interpret_node(node.children[0]) < self._interpret_node(node.children[1])
        elif self._is_operator(node, '>='):
            return self._interpret_node(node.children[0]) >= self._interpret_node(node.children[1])
        elif self._is_operator(node, '<='):
            return self._interpret_node(node.children[0]) <= self._interpret_node(node.children[1])
        elif self._is_operator(node, '=='):
            return self._interpret_node(node.children[0]) == self._interpret_node(node.children[1])
        elif self._is_operator(node, '!='):
            return self._interpret_node(node.children[0]) != self._interpret_node(node.children[1])
        else:
            print(f"Runtime error: unknown node: {node.line}:{node.index}")
            exit(1)

    def run_program(self):
        print("\n\n\n\n\n")
        self._interpret_node(self._syntax_tree)
