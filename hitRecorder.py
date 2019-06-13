from vector import *
from material import *

class hitRecorder:
    
    def __init__(self):
        self.t = 0.0
        self.point = vec3(0.0, 0.0, 0.0)
        self.normal = vec3(0.0, 0.0, 0.0)
        self.material = Lambertian()
