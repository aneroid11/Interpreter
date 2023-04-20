import sys

from working_with_syntax_tree import WorkingWithSyntaxTree
from parser import Parser
from constant import Constant


class SemanticAnalyzer(WorkingWithSyntaxTree):
    class SemanticError(Exception):
        def __init__(self, message: str, line: int, index: int):
            self.message = message
            self.line = line
            self.index = index
            super().__init__(message)

        def __str__(self) -> str:
            return f"{self.message} ({self.line}:{self.index})"

    class DivisionByZero(SemanticError):
        def __init__(self, line: int, index: int):
            super().__init__("division by zero", line, index)

    class InvalidModOperands(SemanticError):
        def __init__(self, line: int, index: int):
            super().__init__("operand of % is not int", line, index)

    class InvalidExpressionInSwitch(SemanticError):
        def __init__(self, line: int, index: int):
            super().__init__("only int and string expressions are allowed in switch", line, index)

    class DoubleDefaultInSwitch(SemanticError):
        def __init__(self, line: int, index: int):
            super().__init__("only one default is allowed in switch", line, index)

    def __init__(self, parser_nodes: list, operators: list, identifiers: list, keywords: list,
                 consts: list, syntax_tree):
        super().__init__(parser_nodes, operators, identifiers, keywords, consts, syntax_tree)

    def _check_int_expression(self, root: Parser.Node):
        if root is None:
            return

        if root.table is self._consts_tbl and root.value().type == Constant.DOUBLE:
            raise SemanticAnalyzer.InvalidModOperands(root.line, root.index)
        if root.table is self._keywords_tbl and root.value() == "atof":
            raise SemanticAnalyzer.InvalidModOperands(root.line, root.index)
        if root.table is self._keywords_tbl and root.value() == "atoi":
            return
        if root.table is self._idents_tbl and root.value().type == "double":
            raise SemanticAnalyzer.InvalidModOperands(root.line, root.index)

        for child in root.children:
            self._check_int_expression(child)

    def _check_not_double_expression(self, root: Parser.Node):
        if root is None:
            return

        if root.table is self._consts_tbl and root.value().type == Constant.DOUBLE:
            raise SemanticAnalyzer.InvalidExpressionInSwitch(root.line, root.index)
        if root.table is self._keywords_tbl and root.value() in ("atof", "atob"):
            raise SemanticAnalyzer.InvalidExpressionInSwitch(root.line, root.index)
        if root.table is self._keywords_tbl and root.value() in ("atoi", "to_string", "scan"):
            return
        if root.table is self._idents_tbl and root.value().type == "double":
            raise SemanticAnalyzer.InvalidExpressionInSwitch(root.line, root.index)

        for child in root.children:
            self._check_int_expression(child)

    def _check_double_default(self, root: Parser.Node, defaults_found: int):
        for stmt in root.children:
            if not self._is_keyword(stmt, "switch"):
                if self._is_keyword(stmt, "default"):
                    defaults_found += 1
                    if defaults_found > 1:
                        raise SemanticAnalyzer.DoubleDefaultInSwitch(stmt.line, stmt.index)
                else:
                    self._check_double_default(stmt, defaults_found)

    def _traverse_tree(self, root: Parser.Node):
        if root is None:
            return

        if root.table is self._ops_tbl and root.value() == "/":
            divisor = root.children[1]

            if divisor.table is self._consts_tbl and divisor.value().type in (Constant.DOUBLE, Constant.INT) \
                and float(divisor.value().value) == 0:
                raise SemanticAnalyzer.DivisionByZero(divisor.line, divisor.index)
        elif root.table is self._ops_tbl and root.value() == "%":
            self._check_int_expression(root.children[0])
            self._check_int_expression(root.children[1])
            return
        elif root.table is self._keywords_tbl and root.value() in ("switch", "case"):
            self._check_not_double_expression(root.children[0])

            if self._is_keyword(root, "switch"):
                self._check_double_default(root.children[1], 0)

        for child in root.children:
            self._traverse_tree(child)

    def check_for_semantic_errors(self):
        try:
            self._traverse_tree(self._syntax_tree)
        except SemanticAnalyzer.SemanticError as err:
            print(f"SEMANTIC ERROR:\n{err}")
            sys.exit(1)
