import sys

from parser import Parser
from constant import Constant


class SemanticAnalyzer:
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

    def __init__(self, parser_nodes: list, operators: list, identifiers: list, keywords: list,
                 consts: list, syntax_tree):
        self._parser_nodes = parser_nodes
        self._operators = operators
        self._identifiers = identifiers
        self._keywords = keywords
        self._consts = consts
        self._syntax_tree = syntax_tree

    def _traverse_tree(self, root: Parser.Node):
        if root is None:
            return

        if root.table is self._operators and root.value() == "/":
            divisor = root.children[1]

            if divisor.table is self._consts and divisor.value().type in (Constant.DOUBLE, Constant.INT) \
                and float(divisor.value().value) == 0:
                raise SemanticAnalyzer.DivisionByZero(divisor.line, divisor.index)

        for child in root.children:
            self._traverse_tree(child)

    def check_for_semantic_errors(self):
        print("\nSEMANTIC ANALYSIS")

        try:
            self._traverse_tree(self._syntax_tree)
        except SemanticAnalyzer.SemanticError as err:
            print(f"SEMANTIC ERROR:\n{err}")
            sys.exit(1)

        print("No semantic errors found")