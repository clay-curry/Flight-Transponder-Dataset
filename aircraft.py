class Aircraft:
    def __init__(self):
        self.varIndex = dict()

    def __getitem__(self, index):
        return self.__dict__[self.varIndex[index]]

    def __setitem__(self, index, value):
        self.__dict__[self.varIndex[index]] = value
