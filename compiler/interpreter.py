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

    def _run_assignment(self, assignment_node: Parser.Node):
        var_name_node = assignment_node.children[0]
        value_node = assignment_node.children[1]
        self._idents_tbl[var_name_node.index_in_table].value = self._interpret_node(value_node)

    def _run_declare(self, decl_node: Parser.Node):
        type_node = decl_node.children[0]

        for curr_var_node in decl_node.children[1:]:
            if self._is_operator(curr_var_node, '='):
                # var_name_node = curr_var_node.children[0]
                # value_node = curr_var_node.children[1]
                # self._idents_tbl[var_name_node.index_in_table].value = self._interpret_node(value_node)
                self._run_assignment(curr_var_node)
            else:
                if type_node.value() == "int":
                    self._idents_tbl[curr_var_node.index_in_table].value = 0
                elif type_node.value() == "double":
                    self._idents_tbl[curr_var_node.index_in_table].value = 0.0
                elif type_node.value() == "string":
                    self._idents_tbl[curr_var_node.index_in_table].value = ""
                elif type_node.value() == "bool":
                    self._idents_tbl[curr_var_node.index_in_table].value = False
                else:
                    self._idents_tbl[curr_var_node.index_in_table].value = None

    def _run_if(self, if_node: Parser.Node):
        cond_node = if_node.children[0]
        stmt_if_yes = if_node.children[1]
        stmt_if_no = None if len(if_node.children) < 3 else if_node.children[2]

        if self._interpret_node(cond_node):
            self._interpret_node(stmt_if_yes)
        elif stmt_if_no is not None:
            self._interpret_node(stmt_if_no)

    def _run_while(self, while_node: Parser.Node):
        cond_node = while_node.children[0]
        body_node = while_node.children[1]

        while self._interpret_node(cond_node):
            self._interpret_node(body_node)

    def _interpret_node(self, node: Parser.Node):
        if node.table is self._parser_nodes_tbl and \
                (node.value() == "program" or node.value() == "compound_statement"):
            for stmt_node in node.children:
                self._interpret_node(stmt_node)
        elif self._is_keyword(node, "print"):
            self._run_print(node)
        elif node.table is self._parser_nodes_tbl and node.value() == "declare":
            self._run_declare(node)
        elif self._is_operator(node, '='):
            self._run_assignment(node)
        elif self._is_string_constant(node):
            return self._compute_string_constant(node)
        elif self._is_constant_of_type(node, Constant.INT):
            return int(node.value().value)
        elif self._is_constant_of_type(node, Constant.DOUBLE):
            return float(node.value().value)
        elif self._is_keyword(node, ("true", "false")):
            return node.value() == "true"
        elif self._is_identifier(node):
            return node.value().value
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
            if len(node.children) < 2:
                return -self._interpret_node(node.children[0])
            else:
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
        elif self._is_keyword(node, "if"):
            self._run_if(node)
        elif self._is_keyword(node, "while"):
            self._run_while(node)
        else:
            print(f"Runtime error: unknown node: {node.line}:{node.index}")
            exit(1)

    def run_program(self):
        print("\n\n\n\n\n")
        self._interpret_node(self._syntax_tree)