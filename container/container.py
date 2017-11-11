import sys

class Container:

    def __init__(self):
        # Initialise dimensions
        self.height = sys.maxsize
        self.length = sys.maxsize
        self.width = sys.maxsize

        self.items = []

    def addItem(self, item):
        self.items.append(item)

    def getLastItemOrder(self):
        if len(self.items) >= 1:
            return self.items[-1].orderID
        return 0

    def getItemWeights(self):
        res = 0

        for item in self.items:
            res += item.weight

        return res



