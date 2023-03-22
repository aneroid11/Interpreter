class Variable:
    def __init__(self, name: str, tp: str = None):
        self.name = name
        self.type = tp

    def __str__(self):
        return f"{self.name} ({self.type})"

    def __eq__(self, other):
        return self.name == other.name
        # return self.value == other.value and self.type == other.type
