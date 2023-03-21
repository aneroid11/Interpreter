def print_tree(root, depth: int = 0):
    if root is None:
        return

    print('\t' * depth + str(root))
    for child in root.children:
        print_tree(child, depth + 1)


class Parser:
    class Node:
        def __init__(self, value=None, children=None):
            if children is None:
                children = []

            self.value = value
            self.children = children

        def __str__(self):
            return str(self.value)

    def __init__(self, tokens, ops_tbl, idents_tbl, keywords_tbl, consts_tbl):
        self._tokens = tokens
        self._ops_tbl = ops_tbl
        self._idents_tbl = idents_tbl
        self._keywords_tbl = keywords_tbl
        self._consts_tbl = consts_tbl

        self._syntax_tree = None

    def print_syntax_tree(self):
        print_tree(self._syntax_tree)

    def create_syntax_tree(self):
        self._syntax_tree = Parser.Node("+", [
            Parser.Node("atoi", [Parser.Node("44")]),
            Parser.Node("66")
        ])
        pass
