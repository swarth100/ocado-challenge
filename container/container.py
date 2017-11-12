import sys

class Container:

    def __init__(self):
        # Initialise dimensions
        self.height = sys.maxsize
        self.length = sys.maxsize
        self.width = sys.maxsize

        self.items = []

        self.rule5 = [1,2,3,4]
        self.rule6 = [1,2,5,6]
        self.rule7 = [1,2,3,5]

    def __len__(self):
        return len(self.items)

    def addItem(self, item):
        self.items.append(item)

    def addItems(self, items):
        for item in items:
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

    def getItemVolumes(self):
        res = 0

        for item in self.items:
            res += item.volume

        return res

    def getRule5Set(self):
        return self.getRuleSet(self.rule5)

    def getRule5Value(self):
        return self.getRuleValue(self.getRule5Set())

    def getRule6Set(self):
        return self.getRuleSet(self.rule6)

    def getRule6Value(self):
        return self.getRuleValue(self.getRule6Set())

    def getRule7Set(self):
        return self.getRuleSet(self.rule7)

    def getRule7Value(self):
        return self.getRuleValue(self.getRule7Set())

    def getRuleSet(self, ruleSet):
        itemsLeft = []
        itemsRight = []

        for item in self.items:
            if item.category in ruleSet:
                itemsLeft.append(item)
            else:
                itemsRight.append(item)
                
        containerLeft = Container()
        containerLeft.addItems(itemsLeft)

        containerRight = Container()
        containerRight.addItems(itemsRight)

        return containerLeft, containerRight

    # 0 -> l1 only
    # 1 -> l2 only
    # 2 -> l1 and l2
    # 3 -> empty
    def getRuleValue(self, vals):
        l1 = len(vals[0].items)
        l2 = len(vals[1].items)

        if (l1 > 0):
            if (l2 > 0):
                return 2
            else:
                return 0
        if (l2 > 0):
            return 1
        return 3




