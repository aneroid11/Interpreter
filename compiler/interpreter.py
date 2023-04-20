from working_with_syntax_tree import WorkingWithSyntaxTree
from parser import Parser
from constant import Constant


class Interpreter(WorkingWithSyntaxTree):
    class Break(Exception):
        pass

    def __init__(self, parser_nodes: list, operators: list, identifiers: list, keywords: list,
                 consts: list, syntax_tree):
        super().__init__(parser_nodes, operators, identifiers, keywords, consts, syntax_tree)

    def _compute_string_constant(self, str_const_node: Parser.Node) -> str:
        str_to_print = str_const_node.value().value
        return bytes(str_to_print, "utf-8").decode("unicode_escape")

    def _run_print(self, print_node: Parser.Node):
        print(self._interpret_node(print_node.children[0]), end='')

    def _run_assignment(self, assignment_node: Parser.Node):
        left_node = assignment_node.children[0]
        value_node = assignment_node.children[1]
        value = self._interpret_node(value_node)

        if not self._is_parser_node(left_node, "indexation"):
            self._idents_tbl[left_node.index_in_table].value = value
        else:
            arr_to_assign = self._idents_tbl[left_node.children[0].index_in_table].value
            # print(arr_to_assign)

            for index_node in left_node.children[1:-1]:
                idx = self._interpret_node(index_node)
                arr_to_assign = arr_to_assign[idx]

            arr_to_assign[self._interpret_node(left_node.children[len(left_node.children) - 1])] = value

    def _get_default_value(self, tp: str):
        if tp == "int":
            return 0
        if tp == "double":
            return 0.0
        if tp == "string":
            return ""
        if tp == "bool":
            return False
        return None

    def _create_array(self, sizes: list, default_value):
        if len(sizes) == 0:
            return default_value
        return [self._create_array(sizes[1:], default_value)] * sizes[0]

    def _run_declare(self, decl_node: Parser.Node):
        for curr_var_node in decl_node.children:
            if self._is_operator(curr_var_node, '='):
                self._run_assignment(curr_var_node)
            else:
                var_type = curr_var_node.value().type

                if not isinstance(var_type, list):
                    self._idents_tbl[curr_var_node.index_in_table].value = self._get_default_value(var_type)
                else:
                    # this is an array
                    default_value = self._get_default_value(var_type[0])
                    self._idents_tbl[curr_var_node.index_in_table].value = \
                        self._create_array(var_type[1:], default_value)

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
            try:
                self._interpret_node(body_node)
            except Interpreter.Break:
                break

    def _run_for(self, for_node: Parser.Node):
        init_node = for_node.children[0]
        cond_node = for_node.children[1]
        incr_node = for_node.children[2]
        body_node = for_node.children[3]

        if init_node is not None:
            self._interpret_node(init_node)

        while cond_node is None or self._interpret_node(cond_node):
            try:
                self._interpret_node(body_node)
            except Interpreter.Break:
                break

            if incr_node is not None:
                self._interpret_node(incr_node)

    def _find_all_cases_and_default(self, node: Parser.Node, ret: list):
        if node is None:
            return

        children_len = len(node.children)

        for i in range(children_len):
            stmt = node.children[i]
            if self._is_keyword(stmt, ("case", "default")):
                ret.append((stmt, node, i))
            elif not self._is_keyword(stmt, "switch"):
                self._find_all_cases_and_default(stmt, ret)

    def _run_switch(self, switch_node: Parser.Node):
        check_var_node = switch_node.children[0]
        statement_node = switch_node.children[1]

        var_val = self._interpret_node(check_var_node)
        cases_and_default = []
        self._find_all_cases_and_default(statement_node, cases_and_default)

        if len(cases_and_default) == 0:
            return

        default_info = None
        needed_node_info = None

        for node_info in cases_and_default:
            if self._is_keyword(node_info[0], "default"):
                default_info = node_info
            else:
                if var_val == self._interpret_node(node_info[0].children[0]):
                    needed_node_info = node_info
                    break

        if default_info is None and needed_node_info is None:
            return
        if needed_node_info is None and default_info is not None:
            needed_node_info = default_info

        parent, idx = needed_node_info[1], needed_node_info[2]

        for i in range(idx, len(parent.children)):
            try:
                self._interpret_node(parent.children[i])
            except Interpreter.Break:
                break

    def _run_compound_statement(self, node: Parser.Node):
        for stmt_node in node.children:
            self._interpret_node(stmt_node)

    def _run_indexation(self, node: Parser.Node):
        val = self._idents_tbl[node.children[0].index_in_table].value

        for index_node in node.children[1:]:
            idx = self._interpret_node(index_node)
            val = val[idx]

        return val

    def _interpret_node(self, node: Parser.Node):
        if node.table is self._parser_nodes_tbl and node.value() == "program":
            for stmt_node in node.children:
                self._interpret_node(stmt_node)
        elif node.table is self._parser_nodes_tbl and node.value() == "compound_statement":
            self._run_compound_statement(node)
        elif self._is_keyword(node, "print"):
            self._run_print(node)
        elif node.table is self._parser_nodes_tbl and node.value() == "declare":
            self._run_declare(node)
        elif self._is_parser_node(node, "indexation"):
            return self._run_indexation(node)
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
            if len(node.children) < 2:
                return self._interpret_node(node.children[0])
            else:
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
        elif self._is_keyword(node, "for"):
            self._run_for(node)
        elif self._is_keyword(node, "switch"):
            self._run_switch(node)
        elif self._is_keyword(node, ("case", "default")):
            return
        elif self._is_keyword(node, "break"):
            raise Interpreter.Break()
        else:
            print(f"Runtime error: unknown node: {node.line}:{node.index}")
            exit(1)

    def run_program(self):
        print("\n\n\n\n\n")
        self._interpret_node(self._syntax_tree)
