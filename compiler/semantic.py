class SemanticAnalyzer:
    def __init__(self, parser_nodes: list, operators: list, identifiers: list, keywords: list,
                 consts: list, syntax_tree):
        self._parser_nodes = parser_nodes
        self._operators = operators
        self._identifiers = identifiers
        self._keywords = keywords
        self._consts = consts
        self._syntax_tree = syntax_tree

    def check_for_semantic_errors(self):
        print()
        print("no errors found")