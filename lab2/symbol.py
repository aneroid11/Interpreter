class Symbol:
    def __init__(self, identifier: str, scope: int, data_type: int):
        self.identifier = identifier
        self.scope = scope
        self.data_type = data_type