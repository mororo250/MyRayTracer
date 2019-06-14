import random

from vector import *
from ray import *

def randomInUnitSphere():
    p = vec3(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)) * 2.0 - vec3(1, 1, 1)
    while p.length() >= 1.0:
        p = vec3(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)) * 2.0 - vec3(1, 1, 1)
    return p

def reflect(vector, normal):
    return vector - normal * vec3.dot(vector, normal) * 2.0

def refract(vector, normal, ni_over_nt, refracted):
    uv = vector.getNorm()
    dt = vec3.dot(uv, normal)
    discriminant = 1.0 - ni_over_nt * ni_over_nt*(1 - dt*dt)
    if (discriminant > 0):
        refracted.__dict__ = ((uv - normal*dt)*ni_over_nt - normal*math.sqrt(discriminant)).__dict__
        return True
    else:
        return False
        
def schlick(cosine, ref_idx):
    r0 = (1 - ref_idx) / (1 + ref_idx)
    r0 = r0*r0
    return r0 + (1 - r0)*pow((1 - cosine), 5)

class Lambertian:

    def __init__(self, albedo = vec3(1.0, 1.0, 1.0)):
        self.__albedo = albedo

    def scatter(self, r_in, rec, attenuation, scattered):
        target = rec.point + rec.normal + randomInUnitSphere()
        scattered.__dict__ = ray(rec.point, target - rec.point, r_in.getTime()).__dict__.copy()
        attenuation.__dict__ = self.__albedo.__dict__.copy()
        return True


class Metal:

    def __init__(self, albedo = vec3(1.0, 1.0, 1.0), fuzz = 1.0):
        if fuzz < 1.0:
            self.__fuzz = fuzz
        else:
            self.__fuzz = 1.0
        self.__albedo = albedo

    def scatter(self, r_in, rec, attenuation, scattered):
        reflected = reflect(r_in.getDirection().getNorm(), rec.normal)
        scattered.__dict__ = ray(rec.point, reflected +  randomInUnitSphere() * self.__fuzz, r_in.getTime()).__dict__.copy()
        attenuation.__dict__ = self.__albedo.__dict__.copy()
        return (vec3.dot(scattered.getDirection(), rec.normal) > 0)

class Dieletric:
    
    def __init__(self, ri):
        self.ref_idx = ri

    def scatter(self, r_in, rec, attenuation, scattered):
        reflected = reflect(r_in.getDirection().getNorm(), rec.normal)
        attenuation.__dict__ = vec3(1.0, 1.0, 1.0).__dict__
        refracted = vec3()
        if (vec3.dot(r_in.getDirection(), rec.normal) > 0):
            outward_normal = -rec.normal
            ni_over_nt = self.ref_idx
            cosine = self.ref_idx * vec3.dot(r_in.getDirection(), rec.normal) * 1.0 / r_in.getDirection().length()
        else:
            outward_normal = rec.normal
            ni_over_nt = 1.0 / self.ref_idx
            cosine = -vec3.dot(r_in.getDirection(), rec.normal) * 1.0 / r_in.getDirection().length()
        if (refract(r_in.getDirection(), outward_normal, ni_over_nt, refracted)):
            reflected_prob = schlick(cosine, self.ref_idx)
        else:
            scattered.__dict__ = ray(rec.point, reflected, r_in.getTime()).__dict__
            reflected_prob = 1.0
        if (random.uniform(0 , 1) < reflected_prob):
            scattered.__dict__ = ray(rec.point, reflected, r_in.getTime()).__dict__
        else:
            scattered.__dict__ = ray(rec.point, refracted, r_in.getTime()).__dict__
        return True
