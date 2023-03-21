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
        def __init__(self, message: str, line: int, index: int):
            self.message = message
            self.line = line
            self.index = index
            super().__init__(message)

    class Expected(ParserError):
        def __init__(self, expected: str, line: int, index: int):
            super().__init__(f"{expected} expected", line, index)

    class Unexpected(ParserError):
        def __init__(self, what_is_unexpected: str, line: int, index: int):
            super().__init__(f"unexpected {what_is_unexpected}", line, index)

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

    def _go_to_next_tok(self):
        self._current_token_index += 1

    def _no_more_tokens(self):
        return self._current_token_index >= len(self._tokens)

    def _curr_tok(self) -> Lexer.Token:
        if self._no_more_tokens():
            tok = self._tokens[len(self._tokens) - 1]
            line = tok.line
            index = tok.index + len(tok.table[tok.index_in_table])
            raise Parser.Unexpected("end of file", line, index)

        return self._tokens[self._current_token_index]

    def print_syntax_tree(self):
        print_tree(self._syntax_tree)

    def _match_number(self, tok: Lexer.Token):
        """Check that this token is a number."""
        if tok.table is not self._consts_tbl or is_not_number(tok.table[tok.index_in_table]):
            raise Parser.Expected("number", tok.line, tok.index)

    def _match_operator(self, tok: Lexer.Token, op_str: str):
        if tok.table is not self._ops_tbl or tok.table[tok.index_in_table] != op_str:
            raise Parser.Expected("'+'", tok.line, tok.index)

    def _parse_number(self) -> Node:
        tok = self._curr_tok()
        self._match_number(tok)
        ret = Parser.Node(self._consts_tbl, tok.index_in_table, None, tok.line, tok.index)
        self._go_to_next_tok()
        return ret

    def _parse_plus(self) -> Node:
        tok = self._curr_tok()
        self._match_operator(tok, '+')
        ret = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()
        return ret

    def _parse_minus(self) -> Node:
        tok = self._curr_tok()
        self._match_operator(tok, '-')
        ret = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()
        return ret

    def _is_addop(self, tok: Lexer.Token) -> bool:
        return tok.table is self._ops_tbl and tok.table[tok.index_in_table] in ('+', '-')

    def _parse_arithmetic_expression(self) -> Node:
        # for now, an arithmetic expression is <number> +/- <number>
        num1 = self._parse_number()

        while not self._no_more_tokens() and self._is_addop(self._curr_tok()):
            op = self._parse_plus() if self._curr_tok().value() == '+' else self._parse_minus()
            num2 = self._parse_number()
            op.children = [num1, num2]
            num1 = op

        return num1

    def create_syntax_tree(self):
        if len(self._tokens) == 0:
            return

        try:
            # self._syntax_tree = self._parse_number()
            self._syntax_tree = self._parse_arithmetic_expression()
        except Parser.ParserError as err:
            print(f"PARSER ERROR:\n\t{err.message} ({err.line}:{err.index})")
            sys.exit(1)
