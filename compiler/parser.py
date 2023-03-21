import sys

from lexer import Lexer
from typing import List

def print_tree(root, depth: int = 0):
    if root is None:
        return

    print('\t' * depth + str(root))
    for child in root.children:
        print_tree(child, depth + 1)


def is_number(s: str):
    try:
        float(s)
        return True
    except ValueError:
        return False


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

    def _is_addop(self, tok: Lexer.Token) -> bool:
        return tok.table is self._ops_tbl and tok.value() in ('+', '-')

    def _is_mulop(self, tok: Lexer.Token) -> bool:
        return tok.table is self._ops_tbl and tok.value() in ('*', '/', '%')

    def _match_number(self, tok: Lexer.Token):
        """Check that this token is a number."""
        if tok.table is not self._consts_tbl or not is_number(tok.table[tok.index_in_table]):
            raise Parser.Expected("number", tok.line, tok.index)

    def _match_operator(self, tok: Lexer.Token, op_str: str):
        if tok.table is not self._ops_tbl or tok.table[tok.index_in_table] != op_str:
            raise Parser.Expected("'+'", tok.line, tok.index)

    def _match_identifier(self, tok: Lexer.Token):
        if tok.table is not self._idents_tbl:
            raise Parser.Expected("identifier", tok.line, tok.index)

    def _parse_operator(self, op: str) -> Node:
        tok = self._curr_tok()
        self._match_operator(tok, op)
        ret = Parser.Node(tok.table, tok.index_in_table, line=tok.line, index=tok.index)
        self._go_to_next_tok()
        return ret

    def _parse_factor(self) -> Node:
        tok = self._curr_tok()

        if tok.table is self._ops_tbl and tok.value() == '(':
            self._go_to_next_tok()
            ret = self._parse_arithmetic_expression()
        elif tok.table is self._consts_tbl and is_number(tok.value()):
            # self._match_number(tok)
            ret = Parser.Node(self._consts_tbl, tok.index_in_table, None, tok.line, tok.index)
        else:
            self._match_identifier(tok)
            ret = Parser.Node(self._idents_tbl, tok.index_in_table, None, tok.line, tok.index)

        self._go_to_next_tok()
        return ret

    def _parse_term(self) -> Node:
        num1 = self._parse_factor()

        while not self._no_more_tokens() and self._is_mulop(self._curr_tok()):
            opval = self._curr_tok().value()
            op = self._parse_operator(opval)
            num2 = self._parse_factor()
            op.children = [num1, num2]
            num1 = op

        return num1

    def _parse_signed_term(self) -> Node:
        tok = self._curr_tok()
        sign = None
        if self._is_addop(tok):
            sign = self._parse_operator(tok.value())

        term = self._parse_term()

        if sign is None:
            return term

        sign.children = [term]
        return sign

    def _parse_arithmetic_expression(self) -> Node:
        term1 = self._parse_signed_term()

        while not self._no_more_tokens() and self._is_addop(self._curr_tok()):
            opval = self._curr_tok().value()
            op = self._parse_operator(opval)
            term2 = self._parse_term()
            op.children = [term1, term2]
            term1 = op

        return term1

    def create_syntax_tree(self):
        if len(self._tokens) == 0:
            return

        try:
            # self._syntax_tree = self._parse_number()
            self._syntax_tree = self._parse_arithmetic_expression()
        except Parser.ParserError as err:
            print(f"PARSER ERROR:\n\t{err.message} ({err.line}:{err.index})")
            sys.exit(1)
