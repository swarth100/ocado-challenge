import sys

# from prism import Prism
# from point import Point


class Point:

    def __init__(self, x, y, z):
        self.x = x
        self. y = y
        self.z = z

    def __str__(self):
        return "Center: (X: " + str(self.x) + " Y: " + str(self.y) + " Z: " + str(self.z) + ")"


class Prism:

    def __init__(self, height, length, width, center):
        self.points = []

        dh = height / 2.0
        dl = length / 2.0
        dw = width / 2.0

        x = center.x
        y = center.y
        z = center.z

        self. height = height
        self.length = length
        self.width = width

        self.center = center

        self.points.append(Point(x - dw, y - dl, z - dh))
        self.points.append(Point(x + dw, y - dl, z - dh))
        self.points.append(Point(x - dw, y + dl, z - dh))
        self.points.append(Point(x + dw, y + dl, z - dh))

        self.points.append(Point(x - dw, y - dl, z + dh))
        self.points.append(Point(x + dw, y - dl, z + dh))
        self.points.append(Point(x - dw, y + dl, z + dh))
        self.points.append(Point(x + dw, y + dl, z + dh))

    def __str__(self):
        return "Center: (X: " + str(self.center.x) + " Y: " + str(self.center.y) + " Z: " + str(self.center.z) + ")" + "\nDimensions: (h: " + str(self.height) + " l: " + str(self.length) + " w: " + str(self.width) + ")"

    def contains(self, point):
        #print "Referencing: " + str(point) + ", over PRISM: " + str(self)
        cx = self.center.x
        dx = self.width / 2.0

        cy = self.center.y
        dy = self.length / 2.0

        cz = self.center.z
        dz = self.height / 2.0

        return (cx - dx <= point.x <= cx + dx) and (cy - dy <= point.y <= cy + dy) and (cz - dz <= point.z <= cz + dz)

    def isInRange(self, x, z):
        return self.contains(Point(x, self.center.y, z))

    def getMaxY(self):
        return self.center.y + self.length / 2.0


class Container:

    def __init__(self):
        # Initialise dimensions
        self.height = 33
        self.length = 55
        self.width = 36

        self.prism = Prism(self.height, self.length, self.width, Point(self.width / 2.0, self.length / 2.0, self.height / 2.0))

        self.items = []

        self.parent = None
        self.children = []

        self.prisms = []

        # Add invisible wall prism
        self.prisms.append(Prism(self.height, 0, self.width, Point(self.height/2.0, 0, self.width/2.0)))

        self.rule5 = [1,2,3,4]
        self.rule6 = [1,2,5,6]
        self.rule7 = [1,2,3,5]

    def __len__(self):
        return len(self.items)

    def kill(self):
        if self.parent:
            try:
                self.parent.children.remove(self)
            except ValueError:
                self

    def addParent(self, parent):
        self.parent = parent
        parent.children.append(self)

    def generateChildContainer(self):
        newCont = Container()
        newCont.addParent(self)

        return newCont

    def generateSiblingContainer(self):
        newCont = Container()
        newCont.addParent(self.parent)

        return newCont

    def getCategories(self):
        res = []

        for item in self.items:
            if not (item.category in res):
                res.append(item.category)

        return res

    def getProductIDs(self):
        res = []

        for item in self.items:
            #if not (item.productID in res):
            res.append(item.productID)

        return res

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

    def getRule2Set(self):
        maxID = 0
        res = []
        buff = self.generateChildContainer()

        # Split in containers
        for item in self.items:

            # On Container INDEX change
            if (item.orderID != maxID):
                res.append(buff)
                maxID = item.orderID
                buff = self.generateChildContainer()

            buff.addItem(item)

        res.append(buff)

        return res

    def getRule5Set(self):
        return self.getRuleSet(self.rule5, self.generateChildContainer)

    def getRule5Value(self):
        return self.getRuleValue(self.getRule5Set())

    def getRule6Set(self):
        return self.getRuleSet(self.rule6, self.generateSiblingContainer)

    def getRule6Value(self):
        return self.getRuleValue(self.getRule6Set())

    def getRule7Set(self):
        return self.getRuleSet(self.rule7, self.generateSiblingContainer)

    def getRule7Value(self):
        return self.getRuleValue(self.getRule7Set())

    def getRuleSet(self, ruleSet, childFunc):
        itemsLeft = []
        itemsRight = []

        for item in self.items:
            if item.category in ruleSet:
                itemsLeft.append(item)
            else:
                itemsRight.append(item)

        containerLeft = childFunc()
        containerLeft.addItems(itemsLeft)

        containerRight = childFunc()
        containerRight.addItems(itemsRight)

        if childFunc == self.generateSiblingContainer:
            self.kill()

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

    def getNextCoord(self, func):
        return func(self.prisms)






