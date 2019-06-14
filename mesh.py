from vector import *
from ray import *
from hitRecorder import *
from hitableCollection import *

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

    def __init__(self, material, position, radious, second_position, time0, time1):
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

class xy_rect:

    def __init__(self, material, x0, x1, y0, y1, k):
        self.material = material
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.k = k
    
    def hit(self, r, t_min, t_max, rec):
        t = (self.k - r.getOrigin()[2]) / r.getDirection()[2]
        if t < t_min or t > t_max:
            return False
        x = r.getOrigin()[0] + t * r.getDirection()[0]
        y = r.getOrigin()[1] + t * r.getDirection()[1]
        if x < self.x0 or x > self.x1 or y < self.y0 or y > self.y1:
            return False
        rec.t = t
        rec.point = r.pointAt(rec.t)
        rec.normal = vec3(0, 0, 1)
        rec.material = self.material
        return True

class xz_rect:

    def __init__(self, material, x0, x1, z0, z1, k):
        self.material = material
        self.x0 = x0
        self.x1 = x1
        self.z0 = z0
        self.z1 = z1
        self.k = k
    
    def hit(self, r, t_min, t_max, rec):
        t = (self.k - r.getOrigin()[1]) / r.getDirection()[1]
        if t < t_min or t > t_max:
            return False
        x = r.getOrigin()[0] + t * r.getDirection()[0]
        z = r.getOrigin()[2] + t * r.getDirection()[2]
        if x < self.x0 or x > self.x1 or z < self.z0 or z > self.z1:
            return False
        rec.t = t
        rec.point = r.pointAt(rec.t)
        rec.normal = vec3(0, 1, 0)
        rec.material = self.material
        return True

class yz_rect:

    def __init__(self, material, y0, y1, z0, z1, k):
        self.material = material
        self.y0 = y0
        self.y1 = y1
        self.z0 = z0
        self.z1 = z1
        self.k = k
    
    def hit(self, r, t_min, t_max, rec):
        t = (self.k - r.getOrigin()[0]) / r.getDirection()[0]
        if t < t_min or t > t_max:
            return False
        y = r.getOrigin()[1] + t * r.getDirection()[1]
        z = r.getOrigin()[2] + t * r.getDirection()[2]
        if y < self.y0 or y > self.y1 or z < self.z0 or z > self.z1:
            return False
        rec.t = t
        rec.point = r.pointAt(rec.t)
        rec.normal = vec3(1, 0, 0)
        rec.material = self.material
        return True

class flipNormal:

    def __init__(self, hitable):
        self.hitable = hitable

    def hit(self, r, t_min, t_max, rec):
        if self.hitable.hit(r, t_min, t_max, rec):
            rec.normal = -rec.normal
            return True

class cube:

    def __init__(self, material, p0, p1):
        self.faces = hitableCollection()
        self.faces.insert(xy_rect(material, p0[0], p1[0], p0[1], p1[1], p1[2]))
        self.faces.insert(flipNormal(xy_rect(material, p0[0], p1[0], p0[1], p1[1], p0[2])))
        self.faces.insert(xz_rect(material, p0[0], p1[0], p0[2], p1[2], p1[1]))
        self.faces.insert(flipNormal(xy_rect(material, p0[0], p1[0], p0[1], p1[1], p0[2])))
        self.faces.insert(yz_rect(material, p0[1], p1[1], p0[2], p1[2], p1[0]))
        self.faces.insert(flipNormal(xy_rect(material, p0[0], p1[0], p0[1], p1[1], p0[2])))

    def hit(self, r, t_min, t_max, rec):
        return self.faces.hit(r, t_min, t_max, rec)
