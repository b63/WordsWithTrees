import os
from wordstree.graphics import *
import json

from cairo import Matrix


class JSONifiable:
    def json_obj(self):
        pass


def create_dir(path):
    """
    Create directory `path` if the path does not already exist, creating parent directories as needed
    :param path: path of directory to create
    """
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except FileNotFoundError:
            parent = os.path.split(path)[0]
            # create parent directory
            create_dir(parent)

            os.mkdir(path)
        except FileExistsError:
            return


def create_file(fpath, relative=''):
    """
    Returns a file object pointing to file located at `fpath` that is open for writing. Parent directories are
    created as needed.
    Note: Callee is responsible for closing the file.

    :param fpath: path to file
    :param relative: if `fpath` is a not an absolute path, what the path is relative to
    :return: file object open for writing
    """
    if not os.path.isabs(fpath):
        fpath = os.path.join(relative, fpath)

    if os.path.exists(fpath):
        if os.path.isdir(fpath):
            raise IsADirectoryError(r"'{}' is a directory".format(fpath.name))
        file = open(fpath, mode='w')
    else:
        dir, fname = os.path.split(fpath)
        create_dir(dir)

        file = open(fpath, mode='w')

    return file


def open_file(fpath, relative=''):
    if not os.path.isabs(fpath):
        fpath = os.path.join(relative, fpath)

    if not os.path.exists(fpath):
        raise FileNotFoundError('"{}" does not exist'.format(fpath))

    file = open(fpath, mode='r')
    return file


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


class Vec(JSONifiable):
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

    def json_obj(self):
        dic = {'x': self.x, 'y': self.y}
        return dic

    def __repr__(self):
        dic = self.json_obj()
        return json.dumps(dic)


class Rect(object):
    """
    Represents a rectangle in a plane in any orientation.
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
        self.__matrix = Matrix.init_rotate(-angle)
        self.__inv_matrix = Matrix.init_rotate(angle)

    def to_rect_basis(self, x, y):
        x1, y1 = self.__matrix.transform_point(x - self.pos.x, y - self.pos.y)
        return Vec(x1, y1)

    def from_rect_basis(self, x, y):
        x1, y1 = self.__inv_matrix.transform_point(x, y)
        return Vec(x1 + self.pos.x, y1 + self.pos.y)

    @property
    def points(self) -> Tuple[Vec, Vec, Vec, Vec]:
        """
        Returns a list of points representing the vertices of the rectangle.
        :return: list of `Vec` objects [top-left, top-right, bottom-right, bottom-left] representing
         the vertices of the rectangle
        """
        dx, dy = self.dx, self.dy

        top_left = self.pos
        top_right = self.from_rect_basis(dx, 0)
        bot_right = self.from_rect_basis(dx, dy)
        bot_left = self.from_rect_basis(0, dy)

        return top_left, top_right, bot_right, bot_left

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


def translate_point_along_line(x, y, dl, angle: float = 0):
    cos_theta, sin_theta = math.cos(angle), math.sin(angle)
    x += dl * cos_theta
    y += dl * sin_theta

    return Vec(x, y)


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
