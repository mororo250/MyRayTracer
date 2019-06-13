from vector import *
from ray import *
from hitRecorder import *

class sphere:
    def __init__(self, material = Lambertian(), position = vec3(0.0, 0.0, -1.0), radious = 0.5):
        self._material = material
        self._position = position
        self._radious = radious
    
    def hit(self, r, t_min, t_max, rec):
        lightdirection = r.getOrigin() - self._position
        a = vec3.dot(r.getDirection(), r.getDirection())
        b = vec3.dot(lightdirection, r.getDirection())
        c = vec3.dot(lightdirection, lightdirection) - self._radious * self._radious
        discriminant = b*b - a*c
        if discriminant > 0:
            temp = (-b - math.sqrt(discriminant)) / a
            if temp < t_max and temp > t_min:
                rec.t = temp
                rec.point = r.pointAt(rec.t)
                rec.normal = (rec.point - self._position) * (1.0 / self._radious)
                rec.material = self._material
                return True
            temp = (-b + math.sqrt(discriminant)) / a
            if temp < t_max and temp > t_min:
                rec.t = temp
                rec.point = r.pointAt(rec.t)
                rec.normal = (rec.point - self._position) * (1.0 / self._radious)
                rec.material = self._material 
                return True 
        return False

    def getMaterial(self):
        return self._material

    def setMaterial(self, material):
        self._material = material

    def getPosition(self):
        return self._position

    def setPosition(self, position):
        self._position = position

    def getRadious(self):
        return self._radious

    def setRadious(self, radious):
        self._radious = radious

class movingSphere(sphere):
    
    def __init__(self,  material, position, radious, second_position, time0, time1):
        sphere.__init__(self, material, position, radious)
        self.__time0 = time0
        self.__time1 = time1
        self.__second_position = second_position
    
    def hit(self, r, t_min, t_max, rec):
        lightdirection = r.getOrigin() - self.__getCurrentPosition(r.getTime())
        a = vec3.dot(r.getDirection(), r.getDirection())
        b = vec3.dot(lightdirection, r.getDirection())
        c = vec3.dot(lightdirection, lightdirection) - self._radious * self._radious
        discriminant = b*b - a*c
        if discriminant > 0:
            temp = (-b - math.sqrt(discriminant)) / a
            if temp < t_max and temp > t_min:
                rec.t = temp
                rec.point = r.pointAt(rec.t)
                rec.normal = (rec.point - self.__getCurrentPosition(r.getTime())) * (1.0 / self._radious)
                rec.material = self._material
                return True
            temp = (-b + math.sqrt(discriminant)) / a
            if temp < t_max and temp > t_min:
                rec.t = temp
                rec.point = r.pointAt(rec.t)
                rec.normal = (rec.point - self.__getCurrentPosition(r.getTime())) * (1.0 / self._radious)
                rec.material = self._material 
                return True 
        return False
    
    def __getCurrentPosition(self, time):
        return self._position + (self._position - self.__second_position) * ((time - self.__time0) / (self.__time1 - self.__time0))
    