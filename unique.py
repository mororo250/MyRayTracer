import argparse
import copy
import math
import multiprocessing
import random
import time

from functools import partial


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

class ray:
    
    def __init__(self, origin: vec3, direction: vec3, t = 0.0):
        self.__origin = origin
        self.__direction = direction
        self.__time = t
    
    def getOrigin(self):
        return self.__origin

    def setOrigin(self, origin):
        self.__origin = origin

    def getDirection(self):
        return self.__direction

    def setDirection(self, direction):
        self.__direction = direction

    def getTime(self):
        return self.__time

    def pointAt(self, const):
        return self.__origin + self.__direction * const 

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

class hitRecorder:
     
    def __init__(self):
        self.t = 0.0
        self.point = vec3(0.0, 0.0, 0.0)
        self.normal = vec3(0.0, 0.0, 0.0)
        self.material = Lambertian()       

class hitableCollection:
    def __init__(self):
        self.__list = []

    def insert(self, hitable):
        self.__list.append(hitable)

    def hit(self, r, t_min, t_max, rec):
        temp_rec = hitRecorder()
        hit_anything = False
        closest_so_far = t_max
        for i in range(0 , len(self.__list)):
            if (self.__list[i].hit(r, t_min, closest_so_far, temp_rec)):
                hit_anything = True
                closest_so_far = temp_rec.t
                rec.__dict__ = temp_rec.__dict__.copy()
        return hit_anything

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

def randomInUnitDisk():
    p = vec3(random.uniform(0, 1), random.uniform(0, 1), 0) * 2.0 - vec3(1, 1, 0)
    while (vec3.dot(p, p) >= 1.0):
        p = vec3(random.uniform(0, 1), random.uniform(0, 1), 0) * 2.0 - vec3(1, 1, 0)
    return p

class Camera:
    
    def __init__(self, aspect, fov, up, position, look_at, aperture = 0.1, focus_dist = 1.0, time0 = 0.0, time1 = 0.0):
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
        self.__time0 = time0
        self.__time1 = time1

    def getRay(self, u, v):
        rd = randomInUnitDisk() * self.__lens_radius
        offset = u * rd[0] + v * rd[1]
        position = vec3(self.__position[0] + offset, self.__position[1] + offset, self.__position[2] + offset)
        time = self.__time0 + random.uniform(0, 1) * (self.__time0 - self.__time1)
        return ray(position, self.__lower_left + self.__horizontal*u + self.__vertical*v - position, time)

MAX_DISTANCE = 100000

def basicScene():
    world = hitableCollection()
    world.insert(sphere(Lambertian(vec3(0.5, 0.5, 0.5)), vec3(0.0, -1000.0, 0.0), 1000))
    world.insert(sphere(Dieletric(1.5), vec3(0.0, 1.0, 0.0), 1.0))
    world.insert(sphere(Lambertian(vec3(0.4, 0.2, 0.1)), vec3(-4.0, 1.0, 0.0), 1.0))
    world.insert(sphere(Metal(vec3(0.7, 0.6, 0.5)), vec3(4.0, 1.0, 0.0), 1.0))
    return world

def randomScene():
    world = hitableCollection()
    world.insert(sphere(Lambertian(vec3(0.5, 0.5, 0.5)), vec3(0.0, -1000.0, 0.0), 1000))
    for a in range(-7, 7):
        for b in range(-7, 7):
            choose_mat = random.uniform(0.0, 1.0)
            center = vec3(a + 0.9 * random.uniform(0.0, 1.0), 0.2, b + 0.9 * random.uniform(0.0, 1.0))
            if (center - vec3(4.0, 0.2, 0.0)).length() > 0.9:
                if choose_mat < 0.8:
                    world.insert(sphere(Lambertian(vec3(random.uniform(0.0, 1.0) * random.uniform(0.0, 1.0), random.uniform(0.0, 1.0) * random.uniform(0.0, 1.0), random.uniform(0.0, 1.0) * random.uniform(0.0, 1.0))), center, 0.2))
                elif choose_mat < 0.95:
                    world.insert(sphere(Metal(vec3(0.5 * (1 + random.uniform(0.0, 1.0)), 0.5 * (1 + random.uniform(0.0, 1.0)), 0.5 * (1 + random.uniform(0.0, 1.0))), 0.5 * random.uniform(0.0, 1.0)), center, 0.2))
                else:
                    world.insert(sphere(Dieletric(1.5), center, 0.2))
    world.insert(sphere(Dieletric(1.5), vec3(0.0, 1.0, 0.0), 1.0))
    world.insert(sphere(Lambertian(vec3(0.4, 0.2, 0.1)), vec3(-4.0, 1.0, 0.0), 1.0))
    world.insert(sphere(Metal(vec3(0.7, 0.6, 0.5)), vec3(4.0, 1.0, 0.0), 1.0))
    return world

def motionScene():
    world = hitableCollection()
    world.insert(sphere(Lambertian(vec3(0.5, 0.5, 0.5)), vec3(0.0, -1000.0, 0.0), 1000))
    for a in range(-4, 4):
        for b in range(-4, 4):
            choose_mat = random.uniform(0.0, 1.0)
            center = vec3(a + 0.9 * random.uniform(0.0, 1.0), 0.2, b + 0.9 * random.uniform(0.0, 1.0))
            if (center - vec3(4.0, 0.2, 0.0)).length() > 0.9:
                if choose_mat < 0.8:
                    world.insert(movingSphere(Lambertian(vec3(random.uniform(0.0, 1.0) * random.uniform(0.0, 1.0), random.uniform(0.0, 1.0) * random.uniform(0.0, 1.0), random.uniform(0.0, 1.0) * random.uniform(0.0, 1.0))), center, 0.2, center + vec3(0, 0.5 * random.uniform(0.0, 1.0), 0), 0.0, 1.0))
                elif choose_mat < 0.95:
                    world.insert(movingSphere(Metal(vec3(0.5 * (1 + random.uniform(0.0, 1.0)), 0.5 * (1 + random.uniform(0.0, 1.0)), 0.5 * (1 + random.uniform(0.0, 1.0))), 0.5 * random.uniform(0.0, 1.0)), center, 0.2, center + vec3(0, 0.5 * random.uniform(0.0, 1.0), 0), 0.0, 1.0))
                else:
                    world.insert(movingSphere(Dieletric(1.5), center, 0.2, center + vec3(0, 0.5 * random.uniform(0.0, 1.0), 0), 0.0, 1.0))
    return world

def cubeScene():
    world = hitableCollection()
    world.insert(xz_rect(Lambertian(vec3(0.5, 0.5, 0.5)), -500, 500, -500, 500, 0))
    world.insert(cube(Metal(vec3(0.7, 0.6, 0.5), 0.5), vec3(-1.5, 0, -1.0), vec3(0.5, 2.0, 1.0)))
    world.insert(cube(Lambertian(vec3(0.4, 0.2, 0.1)), vec3(3.0, 0.0, -1.0), vec3(5.0, 2.0, 1.0)))
    return world

def doWork(line, cam, world, spp, NX, NY):
    results = ""
    for j in range(0, NX):
        color = vec3(0.0, 0.0, 0.0)
        for z in range (0, spp):
            u = float(j + random.uniform(0, 1)) / NX
            v = float(line + random.uniform(0, 1)) / NY
            r = cam.getRay(u, v)
            color += tempColor(r, world, 0)
        color *= (1.0 / spp)
        color = vec3(math.sqrt(color[0]), math.sqrt(color[1]), math.sqrt(color[2]))
        ir = int(255.99 * color[0])
        ig = int(255.99 * color[1])
        ib = int(255.99 * color[2])
        if j < (NX -1):
            results += str("%d\t%d\t%d\t\t" % (ir, ig, ib))
        else:
            results += str("%d %d %d\n" % (ir, ig, ib))
    return results

def tempColor(r, world, depth):
    rec = hitRecorder()
    if world.hit(r, 0.0001, MAX_DISTANCE, rec):
        scattered = ray(vec3(), vec3())
        attenuation = vec3()
        if depth < 50 and rec.material.scatter(r, rec, attenuation, scattered):
            return vec3.multiply(attenuation, tempColor(scattered, world, depth + 1))
        else:
            return vec3()
    else:
        direction = r.getDirection().getNorm()
        t = 0.5 * (direction[1] + 1.0)
        return vec3(1.0, 1.0, 1.0) * (1.0 - t) + vec3(0.5, 0.7, 1.0) * t

def main():
    parser = argparse.ArgumentParser(description = "Renderer based on the book Ray Tracing in One Weekend by Peter Shirley")
    parser.add_argument("-r", "--resolution", type = int, nargs = 2, metavar = ("x", "y"), default = (340, 480), help = "Resolution of the final image. Ex: 1920 1080")
    parser.add_argument("-spp", nargs = '?', type = int, default = 64, help = "Samples per pixel")
    parser.add_argument("-scene", nargs = '?', type = str, default = "basic", choices = ["basic", "random", "motion", "cube"], help = "Scene to be render")
    parser.add_argument("-i", "--image", nargs = '?', type = str, default = "results/image.ppm", help = "Image relative path")
    parser.add_argument("-t", "--threads", nargs = '?', type = int, default = multiprocessing.cpu_count(), help = "Number of processes to be create")
    args = parser.parse_args()

    # Print configuration
    print("Rendenring %s scene" % args.scene)
    print("write in %s" % args.image)
    print("Resolution: %d x %d" % (args.resolution[0], args.resolution[1]))
    print("Samples per pixel: %d" % args.spp)
    print("Number of process: %d" % args.threads)

    if args.scene == "basic":
        world = basicScene()
    elif args.scene == "random":
        world = randomScene()
    elif args.scene == "motion":
        world = motionScene()
    elif args.scene == "cube":
        world = cubeScene()

    camera_pos = vec3(13, 2, 3)
    look_at = vec3(0, 0, 0)
    dist_to_focus = 10.0
    aperture = 0.1
    cam = Camera(args.resolution[0] / args.resolution[1], 20, vec3(0.0, 1.0, 0.0), camera_pos, look_at,  aperture, dist_to_focus, 0.0, 1.0)

    # Open and clean file
    f = open(args.image, "w+")
    f.truncate(0)
    
    # Heap
    f.write("P3\n")
    f.write("%d  %d\n" % (args.resolution[0], args.resolution[1]))
    f.write("255\n")
    f.write("#")
    for i in range(0, args.resolution[0]):
        f.write("%d\t\t\t\t" % (i + 1)),
    f.write("\n")
    
    # MultiThreading
    pool = multiprocessing.Pool(processes = args.threads)
    results = pool.imap(partial(doWork, cam = cam, world = world, spp = args.spp, NX = args.resolution[0], NY = args.resolution[1]), reversed(range(0, args.resolution[1])))
    pool.close
    jobs_completed = 0
    timer = time.time()
    while (True):
        current_time = (time.time() - timer)
        if jobs_completed == args.resolution[1]:
            print("Rendering completed in %ds" % current_time)
            break
        if jobs_completed < results._index:
            jobs_completed = results._index # __index increment with everey task completion.
            progress = jobs_completed / args.resolution[1] * 100.0
            print("Progress: %d%%" % progress)
            print("Remaining time: %ds" % ((current_time * 100 / progress) - current_time))
        time.sleep(2.0)

    for x in results:
        f.write(x)

if __name__ == '__main__': main()
