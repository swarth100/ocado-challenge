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

        self.points.append(Point(x - dw, y - dl, z - dh))
        self.points.append(Point(x + dw, y - dl, z - dh))
        self.points.append(Point(x - dw, y + dl, z - dh))
        self.points.append(Point(x + dw, y + dl, z - dh))

        self.points.append(Point(x - dw, y - dl, z + dh))
        self.points.append(Point(x + dw, y - dl, z + dh))
        self.points.append(Point(x - dw, y + dl, z + dh))
        self.points.append(Point(x + dw, y + dl, z + dh))