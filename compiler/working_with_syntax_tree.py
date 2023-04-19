from lexer import Lexer
from constant import Constant


class WorkingWithSyntaxTree:
    def __init__(self, parser_nodes: list, operators: list, identifiers: list, keywords: list,
                 consts: list, syntax_tree):
        self._parser_nodes_tbl = parser_nodes
        self._ops_tbl = operators
        self._idents_tbl = identifiers
        self._keywords_tbl = keywords
        self._consts_tbl = consts
        self._syntax_tree = syntax_tree

    def _is_addop(self, tok: Lexer.Token) -> bool:
        return tok.table is self._ops_tbl and tok.value() in ('+', '-')

    def _is_mulop(self, tok: Lexer.Token) -> bool:
        return tok.table is self._ops_tbl and tok.value() in ('*', '/', '%')

    def _is_operator(self, tok: Lexer.Token, op) -> bool:
        if tok.table is not self._ops_tbl:
            return False

        if isinstance(op, tuple):
            return tok.value() in op
        return tok.value() == op

    def _is_keyword(self, tok: Lexer.Token, keyword: [str, tuple]) -> bool:
        if tok.table is not self._keywords_tbl:
            return False

        if isinstance(keyword, tuple):
            return tok.value() in keyword
        return tok.value() == keyword

    def _is_identifier(self, tok: Lexer.Token) -> bool:
        return tok.table is self._idents_tbl

    def _is_identifier_of_type(self, tok: Lexer.Token, type: [str, tuple]) -> bool:
        if isinstance(type, tuple):
            return self._is_identifier(tok) and tok.value().type in type

        return self._is_identifier(tok) and tok.value().type == type

    def _is_constant_of_type(self, tok: Lexer.Token, tp: int) -> bool:
        return tok.table is self._consts_tbl and tok.value().type == tp

    def _is_string_constant(self, tok: Lexer.Token) -> bool:
        return tok.table is self._consts_tbl and tok.value().type == Constant.STRING
