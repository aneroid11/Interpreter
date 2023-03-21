class Parser:
    class Node:
        def __init__(self):
            pass

    def __init__(self, tokens, ops_tbl, idents_tbl, keywords_tbl, consts_tbl):
        self._tokens = tokens
        self._ops_tbl = ops_tbl
        self._idents_tbl = idents_tbl
        self._keywords_tbl = keywords_tbl
        self._consts_tbl = consts_tbl

    def create_syntax_tree(self):
        print("\nhere we need to create the syntax tree and return it")
