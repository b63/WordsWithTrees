from typing import Tuple
from wordstree.graphics import *


def degrees(rad: float) -> float:
    """Convert radians to degrees.

    :param rad: floating point value representing angle in radians
    :return: ``rad`` in degrees
    """
    return rad * DEG_RAD


def radians(deg: float) -> float:
    """Convert degrees to radians.
    :param deg:  angle in degrees
    :return: angle in radians
    """
    return deg / DEG_RAD


class Vec:
    """Represents vector in 2D. Offers overloaded `__str__` method for easier printing.
    """

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


class Rect(object):
    """Represents a rectangle in a plane in any orientation.
    """

    def __init__(self, pos: Vec, dx: float, dy: float, angle: float = 0):
        """
        Create rectangle with with its top-left corner at `pos`, dimension of `dx` along the x-axis,
        `dy` along y-axis, and oriented at an angle of `angle` radians from the positive x-axis CCW.
        :param pos: position of 'top-left' corner of rectangle
        :param dx: dimension along x-axis
        :param dy: dimension along y-axis
        :param angle: angle in radians from positive x-axis CCW
        """
        self.__pos = pos
        self.__dx = dx
        self.__dy = dy
        self.__angle = angle

    @property
    def points(self) -> Tuple[Vec, Vec, Vec, Vec]:
        """
        Returns a list of points representing the vertices of the rectangle.
        :return: list of `Vec` objects [top-left, top-right, bottom-right, bottom-left] representing
         the vertices of the rectangle
        """
        x, y, dx, dy = self.pos.x, self.pos.y, self.dx, self.dy
        return self.pos, Vec(x + dx, y), Vec(x + dx, y + dy), Vec(x, y + dy)

    @property
    def angle(self) -> float:
        return self.__angle

    @property
    def pos(self) -> Vec:
        return self.__pos

    @property
    def dx(self):
        return self.__dx

    @property
    def dy(self):
        return self.__dy


def project_point(angle: float, point: Vec):
    """Returns projection of point onto a line that makes the specified angle with the x-axis.

    :param angle: angle of the line on which to project the point
    :param point: `Vec` instance representing the point to project
    :return: projection of the point onto the line of specified angle
    """
    x, y = point.x, point.y
    cos_theta, sin_theta = math.cos(angle), math.sin(angle)

    nx = x * cos_theta + y * sin_theta
    # ny = -x * sin_theta + y * cos_theta
    return nx


def project_rectangle(angle: float, rect: Rect):
    """
    Returns the left and right endpoints of the projection of `rect` onto a line at an angle of `angle` radians
    with the x-axis.
    :param angle: angle in radians of the line onto which to project the rectangle
    :param rect: `Rect` object representing the rectangle to project
    :return: tuple of (left, right) endpoints of the projection of the rectangle onto the line
    """
    points = rect.points
    left = project_point(angle, points[0])
    right = left

    for i in range(1, len(points)):
        p = project_point(angle, points[i])

        if p < left:
            left = p
        if p > right:
            right = p
    return left, right


def rectangle_intersect(rect1: Rect, rect2: Rect):
    """
    Check whether the two rectangles intersect or not using Seprating axis theorem. If the projection of both
    the rectangles onto every edge of the both of the rectangles has some overlap, then the rectangles intersect.
    :param rect1: `Rect` object representing one of the rectangles
    :param rect2:`Rect` object representing one of the rectangles
    :return: whether the two rectangles intersect or not
    """
    def check_projection_overlap(angle: float, rect1: Rect, rect2: Rect) -> bool:
        left1, right1 = project_rectangle(angle, rect1)
        left2, right2 = project_rectangle(angle, rect2)

        # no overlap
        if not (left1 <= left2 <= right1 or left1 <= right2 <= right1):
            return False
        return True

    # check for overlap in projection onto x-axis of rect1
    overlap = check_projection_overlap(rect1.angle, rect1, rect2)
    if not overlap:
        return False

    # check for overlap in projection onto y-axis of rect1
    overlap = check_projection_overlap(rect1.angle - HALF_PI, rect1, rect2)
    if not overlap:
        return False

    # check for overlap in projection onto x-axis of rect2
    overlap = check_projection_overlap(rect2.angle, rect1, rect2)
    if not overlap:
        return False

    # check for overlap in projection onto y-axis of rect2
    overlap = check_projection_overlap(rect2.angle - HALF_PI, rect1, rect2)
    if not overlap:
        return False

    # rectangles intersect
    return True

