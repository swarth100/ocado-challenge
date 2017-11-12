
class Point:

    def __init__(self, x, y, z):
        self.x = x
        self. y = y
        self.z = z

    def __str__(self):
        return "Center: (X: " + str(self.x) + " Y: " + str(self.y) + " Z: " + str(self.z) + ")"

