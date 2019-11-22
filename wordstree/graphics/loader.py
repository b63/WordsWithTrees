from typing import Iterable, List
import random
import json

import click

from wordstree.graphics import *
from wordstree.graphics.util import Vec, radians, JSONifiable, create_file, open_file
from wordstree.graphics.branch import Branch

BRANCH_LENGTH_SHRINK_FACTOR = 0.97
BRANCH_WIDTH_SHRINK_FACTOR = 0.8
BRANCH_LENGTH_DELTA = 0.01
BRANCH_ANGLE_DELTA = radians(10)
BRANCH_ANGLES = (radians(20), radians(-20))
MAX_BRANCH_LENGTH = 0.04
MAX_CHILDREN = 2

CACHE_DIR = 'wordstree/cache'


def generate_root() -> Branch:
    return Branch(
        0,
        Vec(0.5, 0.99),
        **{
            'length': 0.3,
            'width': 0.01
        }
    )


def generate_branches(parent: Branch, index: int, layer: int) -> List[Branch]:
    if layer == 0:
        return [generate_root()]

    if layer > 10:
        num_branches = math.floor(max(0, random.gauss(0.5 - 0.5 * layer, 0.5)) + 0.5)
    else:
        num_branches = MAX_CHILDREN

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
            index + i,
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


def create_branches(branches: List, max_layers=13):
    begin, end, layer = -1, 0, 0
    max_length = len(branches)

    if max_length < 1:
        return 0

    # create root branch
    branches[end] = generate_root()
    begin += 1
    end += 1
    layer += 1

    layers = []
    while layer < max_layers:
        layers.append(begin)

        layer_end = end
        while begin < layer_end:
            parent = branches[begin]
            sub_branches = generate_branches(parent, end, layer)

            i, size = 0, len(sub_branches)
            while i < size and end < max_length:
                branches[end] = sub_branches[i]
                i += 1
                end += 1
            begin += 1

        if begin == end:
            # no new branches were added
            break

        layer += 1

    # return number of branches created
    return layers, end


class Loader:
    def load_branches(self, **kwargs):
        pass

    def save_branches(self, **kwargs):
        pass

    def _branches(self) -> List[Branch]:
        pass

    def _num_branches(self) -> int:
        pass

    def _layers(self) -> List[int]:
        pass

    @property
    def branches(self) -> List[Branch]:
        return self._branches()

    @property
    def num_branches(self) -> int:
        return self._num_branches()

    @property
    def layers(self) -> List[int]:
        return self._layers()


class BranchJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, JSONifiable):
            return o.json_obj()
        return json.JSONEncoder.default(self, o)


def _as_obj_hook(dic):
    for key in Branch.JSON_KEYS:
        if key not in dic:
            return dic

    pos_dict = dic['pos']
    pos = Vec(pos_dict['x'], pos_dict['y'])
    branch = Branch(dic['index'], pos,
                    depth=dic['depth'],
                    length=dic['length'],
                    width=dic['width'],
                    angle=dic['angle']
                    )
    return branch


class FileLoader(Loader):
    def __init__(self):
        self.__branches = None
        self.__layers = None
        self.__num_branches = 0

    def load_branches(self, **kwargs):
        file = kwargs.get('file', None)
        new_tree = file is None

        if new_tree:
            max_depth = kwargs.get('max_depth', 10)

            click.echo('Generating new tree max_depth={} ...'.format(max_depth))

            self.__branches = [None for i in range(2 ** max_depth + 1)]
            layers, length = create_branches(self.__branches, max_layers=max_depth)

            print(layers)
            self.__layers = layers
            self.__num_branches = length
        else:
            self.read_branches(file)

    def save_branches(self, **kwargs):
        fname = kwargs.get('file', 'tree')
        branches = self.branches if self.branches else []

        stream = create_file(fname, relative=CACHE_DIR)

        with stream as file:
            click.echo('Saving branches to {} ...'.format(file.name))
            json.dump(branches[:self.num_branches], file, cls=BranchJSONEncoder)

    def read_branches(self, fpath):
        stream = open_file(fpath, relative=CACHE_DIR)

        with stream as file:
            click.echo('Reading branches from {} ...'.format(file.name))
            branches = json.load(file, object_hook=_as_obj_hook)

        self.__branches = branches
        self.__num_branches = len(branches)

        layers = []
        prev, size = -1, self.__num_branches
        for i in range(size):
            branch = branches[i]
            if prev < branch.depth:
                layers.append(i)
                prev = branch.depth
            elif prev > branch.depth:
                raise Exception('branches not in order')
        self.__layers = layers

        click.echo('Read tree with {:d} branches, {:d} layers :\n   {} ...'.format(size, len(layers), str(layers)))

        return branches

    def _branches(self):
        branches = self.__branches
        return branches if branches else []

    def _layers(self):
        layers = self.__layers
        return layers if layers else []

    def _num_branches(self) -> int:
        return self.__num_branches
