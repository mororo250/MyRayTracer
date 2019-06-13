import random

from ray import *
from vector import *

def randomInUnitDisk():
    p = vec3(random.uniform(0, 1), random.uniform(0, 1), 0) * 2.0 - vec3(1, 1, 0)
    while (vec3.dot(p, p) >= 1.0):
        p = vec3(random.uniform(0, 1), random.uniform(0, 1), 0) * 2.0 - vec3(1, 1, 0)
    return p

class Camera:
    
    def __init__(self, aspect, aperture = 0.1, focus_dist = 1.0, fov = 60, up = vec3(0.0, 1.0, 0.0), position = vec3(0.0, 0.0, 0.0), look_at = vec3(0.0, 0.0, -1.0)):
        theta = fov * math.pi / 180
        half_height = math.tan(theta / 2)
        half_width = aspect * half_height
        w = (position - look_at).getNorm()
        u = vec3.cross(up, w).getNorm()
        v = vec3.cross(w, u)
        self.__position = position
        self.__lower_left = position - (u * half_width + v * half_height + w) * focus_dist
        self.__horizontal = u * 2 * half_width * focus_dist
        self.__vertical = v * 2 * half_height * focus_dist
        self.__lens_radius = aperture / 2.0

    def getRay(self, u, v):
        rd = randomInUnitDisk() * self.__lens_radius
        offset = u * rd[0] + v * rd[1]
        position = vec3(self.__position[0] + offset, self.__position[1] + offset, self.__position[2] + offset)
        return ray(position, self.__lower_left + self.__horizontal*u + self.__vertical*v - position)

    