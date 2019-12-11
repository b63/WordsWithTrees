import math
import cairo
from typing import Dict, Tuple, List
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
        self.__text = kwargs.get('text', '')

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
        debug = kwargs.get('debug', False)

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

        if debug:
            # draw label
            label = '{:d}'.format(self.index)
            ctx.save()
            ctx.set_source_rgba(1, 0, 0, opacity)
            ctx.set_font_size(width*0.1)
            extents = ctx.text_extents(label)

            ctx.rotate(angle)
            ctx.translate(length/2-extents.width/2, 0)
            ctx.rotate(-angle)

            ctx.show_text(label)
            ctx.restore()

        msg = '{}'.format(' '.join(self.text.upper()))
        filler = '—  '
        if msg:
            # draw message
            ctx.save()
            ctx.set_font_size(width*0.9)
            ctx.set_line_width(0.0002)
            ctx.select_font_face('Impact', cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD)

            msg_extents = ctx.text_extents(msg)
            filler_extents = ctx.text_extents(filler)
            num_fillers = math.floor((length-msg_extents.width)/filler_extents.x_advance/2)-2

            full_msg = '{}    {}    {}'.format(filler*num_fillers, msg, filler*num_fillers)
            extents = ctx.text_extents(full_msg)

            if math.pi/2 <= angle <= 3*math.pi/2:
                ctx.rotate(angle + math.pi)
                ctx.translate(-length, 0)
                ctx.scale(1, 1)
                ctx.translate(length/2-extents.width/2, extents.height/2)
            else:
                ctx.rotate(angle)
                ctx.translate(length/2-extents.width/2, extents.height/2)

            ctx.set_source_rgba(1, 1, 1, opacity)
            ctx.text_path(full_msg)
            ctx.fill()
            ctx.stroke()

            # give border
            ctx.set_source_rgba(0, 0, 0, opacity)
            ctx.text_path(full_msg)
            ctx.stroke()

            ctx.restore()

        # draw point
        # ctx.rotate(-angle)
        # ctx.arc(0, 0, 0.004, 0, 2 * math.pi)
        # ctx.set_source_rgb(0, 1, 0)
        # ctx.fill()

        # restore out of branch coordinates
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
    def text(self):
        if self.__text is None:
            return ''
        else:
            return self.__text

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


def _interpolate(start: List, end: List, r) -> List:
    dim = len(start)
    point = [start[i] for i in range(dim)]
    # camp r between 0 and 1
    r = max(0, min(r, 1))

    for i in range(dim):
        s = start[i]
        dist = end[i] - start[i]
        point[i] += dist * r

    return point


def _get_branch_color(branch: Branch) -> List[float]:
    brown = [83/255.0, 49/255.0, 24/255.0]
    green = [0, 1, 0]
    depth = branch.depth
    # stem, brown color
    if depth == 0:
        return brown

    return _interpolate(brown, green, depth/15)


