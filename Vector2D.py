"""
Vector2D class

Operators:
    + - * / ** negative abs() str()
    These will not modify the original location instance(s)

Methods:
    copy
    length
    normalize (this will modify the location instance in-place)
"""

from math import cos, sin, pi, atan2

class Vector2D(object):
    
    def __init__(self, x=0.0, y=0.0):
        self.x, self.y = x, y
        
    # Return an immutable tuple for use as a key in dictionaries    
    def toTuple(self):
        return (self.x, self.y)
    def toIntTuple(self):
        return (int(self.x), int(self.y))
    
    """
    Addition
    """
    def __add__(self, other):
        new = self.copy()
        if isinstance(other, (int, long, float, complex)):
            new.x += other
            new.y += other
        else:
            new.x += other.x
            new.y += other.y
        return new
    def __radd__(self, other):
        return self + other
    def __ladd__(self, other):
        return self + other
        
    """
    Subtraction
    """
    def __sub__(self, other):
        return self + (-other)
    def __rsub__(self, other):
        return (-self) + other     
    def __lsub__(self, other):
        return self + (-other)
    
    """
    Multiplication
    """
    def __mul__(self, other):
        new = self.copy()
        if isinstance(other, (int, long, float, complex)):
            new.x *= other
            new.y *= other
        else:
            new.x *= other.x
            new.y *= other.y
        return new
    def __rmul__(self, other):
        return self * other     
    def __lmul__(self, other):
        return self * other  
         
    """
    Division
    """   
    def __div__(self, other):
        new = self.copy()
        if isinstance(other, (int, long, float, complex)):
            new.x /= other
            new.y /= other
        else:
            new.x /= other.x
            new.y /= other.y
        return new
    def __rdiv__(self, other):
        new = self.copy()
        if isinstance(other, (int, long, float, complex)):
            new.x = other / self.x
            new.y = other / self.y
        else:
            new.x = other.x / self.x
            new.y = other.y / self.y
        return new   
    def __ldiv__(self, other):
        return self / other  
    
    def __pow__(self, other):
        return Vector2D(self.x**other, self.y**other)
    def __abs__(self):
        return Vector2D(abs(self.x), abs(self.y))
    def __neg__(self):
        return Vector2D(-self.x, -self.y)
    def __eq__(self, other):
        if isinstance(other, Vector2D):
            if self.x == other.x and self.y == other.y: 
                return True
        return False
    def __ne__(self, other):
        return not(self == other)
    
    def roundedIntCopy(self):
        return Vector2D(int(round(self.x)), int(round(self.y)))
    def roundedCopy(self):
        return Vector2D(round(self.x), round(self.y))
    def intCopy(self):
        return Vector2D(int(self.x), int(self.y))
    def copy(self):
        return Vector2D(self.x, self.y)
    def length(self):
        return (self.x**2.0 + self.y**2.0)**0.5
    def normalize(self):
        vector_length = self.length()        
        self.x /= vector_length  
        self.y /= vector_length
        return self
    
    """
    Calculate the angluar heading from self to other 
    Returns an angle (0-360) measured counter-clockwise from positive x-axis
    """
    def angleHeadingTo(self, other):
        vector = other-self
        angle = atan2(vector.y, vector.x) * 180.0/pi
        angle = angle % 360 #Bound angle = [0, 359]
#        if angle < 0:       
#            angle += 360.0
#        if angle >= 360: 
#            angle -= 360
        return angle
        
    def unitHeadingTo(self, other):
        vector = other-self
        vector.normalize()
        return vector
    
    @classmethod
    def calculateCentroid(classReference, locations_list):
        total = Vector2D(0, 0)
        total = sum(locations_list, total)
        return total/len(locations_list)
    
    @classmethod
    def generateHeadingFromAngle(classReference, angle):
        return Vector2D(cos(angle * pi/180.0), sin(angle * pi/180.0))
        
        
    def distanceTo(self, other):
        return ((self.x-other.x)**2.0 + (self.y-other.y)**2.0)**0.5
    
    def __str__(self):
        return "({0:.3f}, {1:.3f})".format(self.x, self.y)
