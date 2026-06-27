class Counter:
    def __init__(self, start: int):
        self.value: int = start

    def bump(self) -> int:
        self.value = self.value + 1
        return self.value

    def bump_twice(self) -> int:
        self.bump()
        return self.bump()
