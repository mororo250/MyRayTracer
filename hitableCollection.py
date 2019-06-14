import copy

from vector import *
from ray import *
from hitRecorder import *

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
          