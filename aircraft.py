class Aircraft:
    def __init__(self):
        print(f'Creating a new Aircraft ({self}) object')
        self.attr = dict()

    def __getitem__(self, index):
        print(f"getting Aircraft ({self}) attribute at index {index}")
        return self.__dict__[self.attr[index]]

    def __setitem__(self, index, value):
        print(
            f"setting Aircraft ({self}) item at index {index} with value {value}")
        self.__dict__[self.attr[index]] = value

    def __str__(self) -> str:
        return str(hex(id(self)))


if __name__ == "__main__":
    print("Unit Test: Aircraft Class")
    ac = Aircraft()
    ac.hi = "hi there"
    print(ac.__dict__())
