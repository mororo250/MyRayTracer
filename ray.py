from vector import *

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
