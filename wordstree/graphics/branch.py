import math
import cairo
from typing import Dict, Tuple

from wordstree.graphics.util import Vec, degrees


class Branch:
    DEFAULT_LENGTH = 0.005
    DEFAULT_WIDTH = 0.0005
    DEFAULT_ANGLE = 3 * math.pi / 2

    def __init__(self, pos: Vec = None, **props: Dict):
        self.__pos = pos if pos else Vec(0, 0)
        self.__depth = props.get('depth', 0)
        self.__length = props.get('length', Branch.DEFAULT_LENGTH)
        self.__width = props.get('width', Branch.DEFAULT_WIDTH)
        self.__angle = props.get('angle', Branch.DEFAULT_ANGLE)

    def hit_test(self, x, y):
        cos_theta = math.cos(self.angle)
        sin_theta = math.sin(self.angle)

        x -= self.pos.x
        y -= self.pos.y

        nx = x * cos_theta + y * sin_theta
        ny = -x * sin_theta + y * cos_theta

        halfw = self.width/2

        print('testing hit ({:.2f}, {:.2f})...'.format(nx, ny))
        if (0 < nx < self.length) and (-halfw < ny < halfw):
            return True
        return False

    def draw(self, ctx: cairo.Context, **kwargs):
        layer = kwargs.get('layer', 0)
        opacity = kwargs.get('opacity', 1.0)
        ctx.save()
        pos, angle, width, length = self.pos, self.angle, self.width, self.length

        ctx.translate(pos.x, pos.y)

        # draw rectangle
        ctx.rotate(angle)
        ctx.rectangle(0, -width / 2, length, width)

        r, g, b = get_branch_color(self)
        ctx.set_source_rgba(r, g, b, opacity)
        ctx.fill()

        # draw point
        # ctx.rotate(-angle)
        # ctx.arc(0, 0, 0.004, 0, 2 * math.pi)
        # ctx.set_source_rgb(0, 1, 0)
        # ctx.fill()

        ctx.restore()

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

    def __str__(self):
        return 'Branch@{}[{:.2f}x{:.2f}@{:.2f}]'.format(self.pos, self.length, self.width, degrees(self.angle))

    __repr__ = __str__


def get_branch_color(branch: Branch) -> Tuple[float, float, float]:
    depth = branch.depth
    red = min(2 * depth + 50, 160)
    green = min(1.7 * depth * depth + 50, 255)
    blue = min(14 * depth + 50, 125)

    return red / 255.0, green / 255.0, blue / 255.0
