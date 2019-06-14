import random
import time
import math
import multiprocessing
import argparse
from functools import partial

from mesh import *
from vector import *
from ray import *
from hitRecorder import *
from hitableCollection import *
from camera import *
from material import *

# Scenes
def basicScene():
    world = hitableCollection()
    world.insert(sphere(Lambertian(vec3(0.5, 0.5, 0.5)), vec3(0.0, -1000.0, 0.0), 1000))
    world.insert(sphere(Dieletric(1.5), vec3(0.0, 1.0, 0.0), 1.0))
    world.insert(sphere(Lambertian(vec3(0.4, 0.2, 0.1)), vec3(-4.0, 1.0, 0.0), 1.0))
    world.insert(sphere(Metal(vec3(0.7, 0.6, 0.5)), vec3(4.0, 1.0, 0.0), 0.0))
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
    world.insert(sphere(Metal(vec3(0.7, 0.6, 0.5)), vec3(4.0, 1.0, 0.0), 0.0))
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
    world.insert(cube(Metal(vec3(0.7, 0.6, 0.5), 0.2), vec3(-1.5, 0, 0.0), vec3(0.5, 2.0, 2.0)))
    world.insert(cube(Lambertian(vec3(0.4, 0.2, 0.1)), vec3(3.0, 0.0, -1.0), vec3(5.0, 2.0, 1.0)))
    return world

# main program / renderer manager

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
    if world.hit(r, 0.0001, 10000000, rec):
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
