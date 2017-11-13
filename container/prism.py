from point import Point

class Prism:

    def __init__(self, height, length, width, center):
        self.points = []

        self.x = center.x
        self.y = center.y
        self.z = center.z

        self. height = height
        self.length = length
        self.width = width

        self.center = center

        self.setDimension()

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

    def setDimension(self):
        dh = self.height / 2.0
        dl = self.length / 2.0
        dw = self.width / 2.0
        self.points = []
        self.points.append(Point(self.x - dw, self.y - dl, self.z - dh))
        self.points.append(Point(self.x + dw, self.y - dl, self.z - dh))
        self.points.append(Point(self.x - dw, self.y + dl, self.z - dh))
        self.points.append(Point(self.x + dw, self.y + dl, self.z - dh))

        self.points.append(Point(self.x - dw, self.y - dl, self.z + dh))
        self.points.append(Point(self.x + dw, self.y - dl, self.z + dh))
        self.points.append(Point(self.x - dw, self.y + dl, self.z + dh))
        self.points.append(Point(self.x + dw, self.y + dl, self.z + dh))


    def rotateVerticle(self):
        temp_height = self.height
        self.height = self.length
        self.length = temp_height
        self.setDimension()

    def rotateHorizontal(self):
        temp_length = self.length
        self.length = self.width
        self.width = temp_length
        self.setDimension()

    def rotateDepth(self):
        temp_width = self.width
        self.width = self.height
        self.height = temp_width
        self.setDimension()
