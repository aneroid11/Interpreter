class Variable:
    def __init__(self, name: str, tp: [str, None], nest_level: int, block_on_level: int):
        self.name = name
        self.type = tp
        self.nest_level = nest_level
        self.block_on_level = block_on_level
        self.value = None

    def __str__(self):
        return f"{self.name} ({self.type} in [{self.nest_level}, {self.block_on_level}] block)"

    def __eq__(self, other):
        return self.name == other.name and \
            (self.nest_level == other.nest_level and self.block_on_level == other.block_on_level)
        # return self.value == other.value and self.type == other.type
