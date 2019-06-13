import copy
import math

class vec3:

    def __init__(self, v1 = 0.0, v2 = 0.0, v3 = 0.0):
        self.vec = [v1, v2, v3]
    
    def __add__(self, other):
        aux = vec3()
        aux.vec[0] = self.vec[0] + other.vec[0]
        aux.vec[1] = self.vec[1] + other.vec[1]
        aux.vec[2] = self.vec[2] + other.vec[2]
        return aux

    def __sub__(self, other):
        aux = vec3()
        aux.vec[0] = self.vec[0] - other.vec[0]
        aux.vec[1] = self.vec[1] - other.vec[1]
        aux.vec[2] = self.vec[2] - other.vec[2]
        return aux

    def __iadd__(self, other):
        self.vec[0] += other.vec[0]
        self.vec[1] += other.vec[1]
        self.vec[2] += other.vec[2]
        return self

    def __isub__(self, other):
        self.vec[0] -= other.vec[0]
        self.vec[1] -= other.vec[1]
        self.vec[2] -= other.vec[2]
        return self

    def __neg__(self):
        aux = vec3()
        aux.vec[0] -= self.vec[0]
        aux.vec[1] -= self.vec[1]
        aux.vec[2] -= self.vec[2]
        return aux
    
    def __pos__(self):
        return self

    def __mul__(self, scalar: float):
        aux = vec3()
        aux.vec[0] = self.vec[0] * scalar
        aux.vec[1] = self.vec[1] * scalar
        aux.vec[2] = self.vec[2] * scalar
        return aux

    def __getitem__(self, key):
        return self.vec[key]
    
    def __setitem__(self, key, value):
        self.vec[key] = value
    
    def __str__(self):
        return "[%f\t %f\t %f]" % (self.vec[0], self.vec[1], self.vec[2])
    
    def length(self):
        return math.sqrt(pow(self.vec[0], 2) + pow(self.vec[1], 2) + pow(self.vec[2], 2))

    def normalize(self):
        length = self.length()
        if length is not 0.0:
            self.vec[0] /= length
            self.vec[1] /= length
            self.vec[2] /= length
        return self

    def getNorm(self):
        aux = copy.deepcopy(self)
        return aux.normalize()

    @staticmethod
    def multiply(rhs, lhs):
        return vec3(rhs[0] * lhs[0], rhs[1] * lhs[1], rhs[2] * lhs[2])

    @staticmethod
    def cross(rhs, lhs):
        aux = vec3()
        aux.vec[0] = rhs.vec[1] * lhs.vec[2] - rhs.vec[2] * lhs.vec[1]
        aux.vec[1] = rhs.vec[2] * lhs.vec[0] - rhs.vec[0] * lhs.vec[2]
        aux.vec[2] = rhs.vec[0] * lhs.vec[1] - rhs.vec[1] * lhs.vec[0]
        return aux
        
    @staticmethod
    def dot(rhs, lhs):
        aux = 0.0
        aux += rhs[0] * lhs[0]
        aux += rhs[1] * lhs[1]
        aux += rhs[2] * lhs[2]
        return aux
        