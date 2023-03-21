import sys

from lexer import Lexer
from typing import List

def print_tree(root, depth: int = 0):
    if root is None:
        return

    print('\t' * depth + str(root))
    for child in root.children:
        print_tree(child, depth + 1)


def is_not_number(s: str):
    try:
        float(s)
        return False
    except ValueError:
        return True


class Parser:
    class ParserError(Exception):
        def __init__(self, message, line: int, index: int):
            self.message = message
            self.line = line
            self.index = index
            super().__init__(message)

    class Expected(ParserError):
        def __init__(self, expected: str, line: int, index: int):
            super().__init__(f"{expected} expected", line, index)

    class Node:
        def __init__(self, tbl=None, index_in_tbl=None, children=None, line: int = 0, index: int = 0):
            if children is None:
                children = []

            self.table = tbl
            self.index_in_table = index_in_tbl
            self.line = line
            self.index = index
            self.children = children

        def __str__(self):
            return str(self.table[self.index_in_table])

    def __init__(self, tokens: List[Lexer.Token], ops_tbl, idents_tbl, keywords_tbl, consts_tbl):
        self._tokens = tokens
        self._current_token_index = 0
        self._ops_tbl = ops_tbl
        self._idents_tbl = idents_tbl
        self._keywords_tbl = keywords_tbl
        self._consts_tbl = consts_tbl

        self._syntax_tree = None

    def print_syntax_tree(self):
        print_tree(self._syntax_tree)

    def _parse_number(self) -> Node:
        tok = self._tokens[self._current_token_index]
        if tok.table is not self._consts_tbl or is_not_number(tok.table[tok.index_in_table]):
            raise Parser.Expected("number", tok.line, tok.index)

        return Parser.Node(self._consts_tbl, tok.index_in_table, None, tok.line, tok.index)

    def create_syntax_tree(self):
        try:
            self._syntax_tree = self._parse_number()
        except Parser.ParserError as err:
            print(f"PARSER ERROR:\n\t{err.message} ({err.line}:{err.index})")
            sys.exit(1)
