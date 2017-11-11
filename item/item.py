
class Item:

    def __init__(self, rule, data):
        # Initialise dimensions
        self.height = 0
        self.length = 0
        self.width = 0

        # Keep track of rule
        self.rule = rule

        self.ID = 0
        self.orderID = 0
        self.weight = 0

        self.parseData(data)

    def parseData(self, data):
        (productID, height, length, width, self.weight, volume, category, self.orderID, productID) = data

        self.ID = productID
