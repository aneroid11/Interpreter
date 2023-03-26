from parser import Parser


class SemanticAnalyzer:
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

        if root.table is self._keywords and root.value() == "for":
            print("I found for!")

        for child in root.children:
            self._traverse_tree(child)

    def check_for_semantic_errors(self):
        print("\nSEMANTIC ANALYSIS")
        self._traverse_tree(self._syntax_tree)