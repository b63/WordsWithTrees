import math
import cairo
from typing import Dict, Tuple
import json

from wordstree.graphics import HALF_PI
from wordstree.graphics.util import Vec, degrees, JSONifiable, Rect, translate_point_along_line


class Branch(JSONifiable):
    DEFAULT_LENGTH = 0.005
    DEFAULT_WIDTH = 0.0005
    DEFAULT_ANGLE = 3 * math.pi / 2
    JSON_KEYS = ['index', 'pos', 'depth', 'length', 'width', 'angle']

    def __init__(self, index, pos: Vec = None, **kwargs):
        self.__index = index
        self.__pos = pos if pos else Vec(0, 0)
        self.__depth = kwargs.get('depth', 0)
        self.__length = kwargs.get('length', Branch.DEFAULT_LENGTH)
        self.__width = kwargs.get('width', Branch.DEFAULT_WIDTH)
        self.__angle = kwargs.get('angle', Branch.DEFAULT_ANGLE)

        x, y = self.__pos.x, self.__pos.y
        top_left = translate_point_along_line(x, y, -self.__width/2, self.__angle + HALF_PI)
        self.__rect = Rect(top_left, self.__length, self.__width, self.__angle)

    def hit_test(self, x, y):
        cos_theta = math.cos(self.angle)
        sin_theta = math.sin(self.angle)

        x -= self.pos.x
        y -= self.pos.y

        nx = x * cos_theta + y * sin_theta
        ny = -x * sin_theta + y * cos_theta

        halfw = self.width / 2

        print('testing hit ({:.2f}, {:.2f})...'.format(nx, ny))
        if (0 < nx < self.length) and (-halfw < ny < halfw):
            return True
        return False

    def draw(self, ctx: cairo.Context, **kwargs):
        layer = kwargs.get('layer', 0)
        opacity = kwargs.get('opacity', 1.0)
        ctx.save()
        pos, angle, width, length = self.pos, self.angle, self.width, self.length

        # move origin to position of branch
        ctx.translate(pos.x, pos.y)

        # draw rectangle
        ctx.save()
        ctx.rotate(angle)
        ctx.rectangle(0, -width / 2, length, width)

        r, g, b = _get_branch_color(self)
        ctx.set_source_rgba(r, g, b, opacity)
        ctx.fill()
        ctx.restore()

        # draw label
        label = '{:d}'.format(self.index)
        ctx.set_source_rgba(1, 0, 0, opacity)
        ctx.set_font_size(width*0.1)
        extents = ctx.text_extents(label)

        ctx.rotate(angle)
        ctx.translate(length/2-extents.width/2, 0)
        ctx.rotate(-angle)

        ctx.show_text('{:d}'.format(self.index))

        # draw point
        # ctx.rotate(-angle)
        # ctx.arc(0, 0, 0.004, 0, 2 * math.pi)
        # ctx.set_source_rgb(0, 1, 0)
        # ctx.fill()

        ctx.restore()

    @property
    def rect(self):
        return self.__rect

    @property
    def index(self):
        return self.__index

    @property
    def pos(self):
        return self.__pos

    @property
    def depth(self):
        return self.__depth

    @property
    def length(self):
        return self.__length

    @property
    def width(self):
        return self.__width

    @property
    def angle(self):
        return self.__angle

    def json_obj(self):
        dic = dict()

        for key in Branch.JSON_KEYS:
            if key == 'pos':
                dic[key] = self.pos.json_obj()
            else:
                dic[key] = self.__getattribute__(key)
        return dic

    def __str__(self):
        return 'Branch@{}[{:.2f}x{:.2f}@{:.2f}]'.format(self.pos, self.length, self.width, degrees(self.angle))

    def __repr__(self):
        dic = self.json_obj()

        return json.dumps(dic)


def _get_branch_color(branch: Branch) -> Tuple[float, float, float]:
    depth = branch.depth
    red = min(2 * depth + 50, 160)
    green = min(1.7 * depth * depth + 50, 255)
    blue = min(14 * depth + 50, 125)

    return red / 255.0, green / 255.0, blue / 255.0
