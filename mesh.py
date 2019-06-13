from vector import *
from ray import *
from hitRecorder import *

class sphere:

    def __init__(self, material = Lambertian(), position = vec3(0.0, 0.0, -1.0), radious = 0.5):
        self.__material = material
        self.__position = position
        self.__radious = radious
    
    def hit(self, r, t_min, t_max, rec):
        lightdirection = r.getOrigin() - self.__position
        a = vec3.dot(r.getDirection(), r.getDirection())
        b = vec3.dot(lightdirection, r.getDirection())
        c = vec3.dot(lightdirection, lightdirection) - self.__radious * self.__radious
        discriminant = b*b - a*c
        if discriminant > 0:
            temp = (-b - math.sqrt(discriminant)) / a
            if temp < t_max and temp > t_min:
                rec.t = temp
                rec.point = r.pointAt(rec.t)
                rec.normal = (rec.point - self.__position) * (1.0 / self.__radious)
                rec.material = self.__material
                return True
            temp = (-b + math.sqrt(discriminant)) / a
            if temp < t_max and temp > t_min:
                rec.t = temp
                rec.point = r.pointAt(rec.t)
                rec.normal = (rec.point - self.__position) * (1.0 / self.__radious)
                rec.material = self.__material 
                return True 
        return False

    def getColor(self):
        return self.__material

    def setColor(self, material):
        self.__material = material

    def getPosition(self):
        return self.__position

    def setPosition(self, position):
        self.__position = position

    def getRadious(self):
        return self.__position

    def setRadious(self, radious):
        self.__radious = radious


        