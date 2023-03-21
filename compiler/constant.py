class Constant:
    INT, DOUBLE, STRING = range(3)

    def __init__(self, value, tp: int):
        self.value = value
        self.type = tp

    def __str__(self):
        if self.type in (Constant.INT, Constant.DOUBLE):
            return self.value
        return f"'{self.value}'"

    def __eq__(self, other):
        return self.value == other.value and self.type == other.type
