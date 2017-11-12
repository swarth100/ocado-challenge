from point import Point

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
        cx = self.center.x
        dx = self.width / 2.0

        cy = self.center.y
        dy = self.length / 2.0

        cz = self.center.z
        dz = self.height / 2.0

        return (cx - dx < point.x < cx + dx) and (cy - dy < point.y < cy + dy) and (cz - dz < point.z < cz + dz)

    def isInRange(self, x, z):
        return not self.contains(Point(x, self.center.y, z))

    def getMaxY(self):
        return self.center.y + self.length / 2.0