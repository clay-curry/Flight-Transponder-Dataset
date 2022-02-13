class Aircraft:
    def __init__(self):
        self.attr = dict()

    def __getitem__(self, index):
        return self.__dict__[self.attr[index]]

    def __setitem__(self, index, value):
        self.__dict__[self.attr[index]] = value

    def __str__(self) -> str:
        return str(hex(id(self)))


if __name__ == "__main__":
    print("Unit Test: Aircraft Class")
    ac = Aircraft()
    ac.hi = "hi there"
    print(ac.__dict__)
