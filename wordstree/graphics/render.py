import math
import random
from typing import List

import cairo

from wordstree.graphics import *
from wordstree.graphics.util import Vec, radians, Rect, rectangle_intersect
from wordstree.graphics.branch import Branch

BRANCH_LENGTH_SHRINK_FACTOR = 0.97
BRANCH_WIDTH_SHRINK_FACTOR = 0.8
BRANCH_LENGTH_DELTA = 0.01
BRANCH_ANGLE_DELTA = radians(10)
BRANCH_ANGLES = (radians(20), radians(-20))
MAX_BRANCH_LENGTH = 0.04


def generate_root() -> Branch:
    return Branch(
        Vec(0.5, 0.99),
        **{
            'length': 0.3,
            'width': 0.01
        }
    )


def generate_branches(parent: Branch, layer: int) -> List[Branch]:
    if layer == 0:
        return [generate_root()]

    if layer > 10:
        num_branches = math.floor(max(0, random.gauss(0.5 - 0.5 * layer, 0.5)) + 0.5)
    else:
        num_branches = Renderer.MAX_CHILDREN

    nangles = len(BRANCH_ANGLES)
    branches = []

    ppos, plength, pwidth, pangle = parent.pos, parent.length, parent.width, parent.angle

    base_length = min(plength, MAX_BRANCH_LENGTH) * BRANCH_LENGTH_SHRINK_FACTOR

    for i in range(num_branches):
        width = pwidth * BRANCH_WIDTH_SHRINK_FACTOR
        length = max(base_length + random.gauss(0, BRANCH_LENGTH_DELTA) / (layer + 1), 0)
        angle = pangle + BRANCH_ANGLES[i % nangles] + random.gauss(0, BRANCH_ANGLE_DELTA)

        x = ppos.x + math.cos(pangle) * plength
        y = ppos.y + math.sin(pangle) * plength

        branch = Branch(
            Vec(x, y),
            **{
                'length': length,
                'angle': angle,
                'parent': parent,
                'width': width,
                'depth': layer
            }
        )
        branches.append(branch)

    return branches


class Renderer:
    WIDTH = 1024
    HEIGHT = 1024
    MAX_CHILDREN = 2

    def __init__(self, max_layers=5):
        self.surface = cairo.SVGSurface('tree.svg', Renderer.WIDTH, Renderer.HEIGHT)

        self.layers = []
        self.max_layers = max_layers

        self.__branches = [None for i in range(2 ** max_layers + 1)]
        self.__num_branches = 0

        #self.zoom_levels = [i for i in range(0, max_layers)]
        self.zoom_levels = [5, 6, 7, 8, 9, 10, 11]
        self.grid_levels = [8, 16, 24, 40, 60]

        self.create_branches()

    def create_branches(self):
        begin, end, layer = -1, 0, 0
        max_length = len(self.branches)

        # create root branch
        self.branches[end] = generate_root()
        begin += 1
        end += 1
        layer += 1

        while layer < self.max_layers:
            self.layers.append(begin)

            layer_end = end
            while begin < layer_end:
                parent = self.branches[begin]
                sub_branches = generate_branches(parent, layer)

                i, size = 0, len(sub_branches)
                while i < size and end < max_length:
                    self.branches[end] = sub_branches[i]
                    i += 1
                    end += 1
                begin += 1

            if begin == end:
                # no new branches were added
                break

            layer += 1

        self.__num_branches = end

    def setup_canvas(self, ctx):
        ctx.scale(Renderer.WIDTH, Renderer.HEIGHT)

        # draw white background
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, 1, 1)
        ctx.fill()

        ctx.set_source_rgb(1, 0, 0)
        ctx.rectangle(0, 0, 0.01, 0.1)
        ctx.fill()
        ctx.set_source_rgb(0, 1, 0)
        ctx.rectangle(0, 0, 0.1, 0.01)
        ctx.fill()

        ctx.set_source_rgb(1, 0, 1)
        ctx.rectangle(0, 0, 1, 1)
        ctx.set_line_width(0.01)
        ctx.stroke()

        ratio = 0.9
        ctx.translate(0.5, 1)
        ctx.scale(ratio, ratio)
        ctx.translate(-0.5, -1)

        # draw boundary
        ctx.set_source_rgb(0, 0, 0)
        ctx.rectangle(0, 0, 1, 1)
        ctx.set_line_width(0.01)
        ctx.stroke()

    def get_opacity(self, zoom: int, layer: int) -> float:
        diff = layer - zoom
        if diff <= 0:
            return 1.0
        elif diff == 1:
            return 0.5
        elif diff == 2:
            return 0.15
        elif diff == 3:
            return 0.05
        else:
            return 0

    def render_tree(self, zoom=0):
        ctx = cairo.Context(self.surface)
        self.setup_canvas(ctx)

        i, layeri = self.tree_size - 1, len(self.layers) - 1
        next_layer = self.layers[layeri]

        while i >= 0:
            opacity = self.get_opacity(zoom, layeri)
            if opacity > 0.0:
                self.branches[i].draw(ctx, opacity=opacity)

            i -= 1
            if i == next_layer:
                print('finished drawing layer {:d}...'.format(layeri))
                layeri -= 1
                next_layer = self.layers[layeri]

        self.surface.write_to_png('tree.png')

    @property
    def branches(self) -> List[Branch]:
        return self.__branches

    @property
    def tree_size(self) -> int:
        return self.__num_branches


if __name__ == "__main__":
    renderer = Renderer(max_layers=16)
    renderer.render_tree(zoom=7)

