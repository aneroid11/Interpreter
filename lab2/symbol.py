class Symbol:
    def __init__(self, identifier: str, scope: str, data_type=None):
        self.identifier = identifier
        self.scope = scope
        self.data_type = data_type
