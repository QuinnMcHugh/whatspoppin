'''
Circle with radius and center point.
'''
class Circle:
    '''
    Constructor.
    '''
    def __init__(self, x, y, radius):
        self.center_x = x
        self.center_y = y
        self.radius = radius

    
    def __str__(self):
        return "{ x: " + str(self.center_x) + ", y: " + str(self.center_y) + ", r: " + str(self.radius) + " }"