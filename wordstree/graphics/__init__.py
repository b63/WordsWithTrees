import math

DEG_RAD = 180 / math.pi


def degrees(radians: float) -> float:
    return radians * DEG_RAD


def radians(degrees: float) -> float:
    return degrees / DEG_RAD


class Vec:
    def __init__(self, x: float, y: float):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __str__(self):
        return '({:.2f}, {:.2f})'.format(self.__x, self.__y)

    __repr__ = __str__
