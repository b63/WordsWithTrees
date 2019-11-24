from typing import Iterable, List
import random
import json

import click
from flask import current_app, Flask
import sqlite3

from wordstree.db import get_db
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


def generate_tree(max_depth=10, cls=None) -> Tuple[List, List[int], int]:
    click.echo('Generating new tree max_depth={} ...'.format(cls, max_depth))

    branches = [None for i in range(2 ** max_depth + 1)]
    layers, length = create_branches(branches, max_layers=max_depth)

    print(layers)
    return branches, layers, length


class Loader:

    def load_branches(self, **kwargs):
        pass

    def save_branches(self, **kwargs):
        pass

    def save_branches_from_loader(self, loader):
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


class DBLoader(Loader):

    def __init__(self, app: Flask):
        self.__app = app
        self.__branches = None
        self.__layers = None
        self.__num_branches = 0

    def load_branches(self, **kwargs):
        tree_id = kwargs.get('tree_id', None)
        new_tree = tree_id is None

        if new_tree:
            max_depth = kwargs.get('max_depth', 10)
            self.__branches, self.__layers, self.__num_branches = generate_tree(max_depth=max_depth)
            print('DB Loader')
            print(self.layers)
        else:
            self.__read_all_branches(tree_id)

    def save_branches(self, **kwargs):
        tree_id = kwargs.get('tree_id', None)
        full_width = kwargs.get('width', None)
        full_height = kwargs.get('height', None)

        # use self.branches if branches kwarg not provided
        branches, num_branches = kwargs.get('branches', None), kwargs.get('num_branches', None)
        if branches is None:
            branches = self.branches
            num_branches = self.num_branches
        elif not num_branches:
            # branches kwarg provided but no num_branches provided
            raise Exception('num_branches not provided')

        with self.app.app_context():
            db = get_db()
            cur = db.cursor()

            if tree_id is not None:
                click.echo('Dropping existing tree with tree_id={} ...'.format(tree_id))
                cur.execute(r'DELETE FROM branches WHERE "tree_id"=?', [tree_id])
                cur.execute(r'DELETE FROM tree WHERE "tree_id"=?', [tree_id])

                cur.execute('INSERT INTO tree (tree_id, num_branches, full_width, full_height) VALUES (?, ?, ?, ?)',
                            [tree_id, num_branches, full_width, full_height])
            else:
                cur.execute('INSERT INTO tree (num_branches, full_width, full_height) VALUES (?, ?, ?)',
                            [num_branches, full_width, full_height])

            cur.execute('SELECT last_insert_rowid()')
            rowid = cur.fetchone()[0]
            click.echo('Created new tree with tree_id={} ...'.format(rowid))

            self.__add_all_branches(cur, rowid, branches=branches, num_branches=num_branches)
            db.commit()

    def __read_all_branches(self, tree_id: int):
        with self.app.app_context():
            db = get_db()
            cur = db.cursor()

            # cur.execute('SELECT num_branches FROM tree WHERE tree_id=?', [tree_id])
            # num_branches = cur.fetchone()['num_branches']

            click.echo('Reading branches with tree_id={} ...'.format(tree_id))

            cur.execute('SELECT * FROM branches WHERE tree_id=? ORDER BY "index" ASC', [tree_id])
            results = cur.fetchall()

        num_branches = len(results)
        branches = [None for i in range(num_branches)]

        layers, layer = [], -1
        for i in range(num_branches):
            row = results[i]
            depth, length, width = row['depth'], row['length'], row['width']
            angle = row['angle']
            posx, posy = row['pos_x'], row['pos_y']

            branches[i] = Branch(i, Vec(posx, posy), depth=depth, length=length, width=width, angle=angle)
            if depth > layer:
                layers.append(i)
                layer = depth
            elif depth < layer:
                raise Exception('branches not in order')

        click.echo('Read {} branches with tree_id={}, layers {} ...'
                   .format(num_branches, tree_id, str(layers).strip('[]'))
                   )

        self.__branches = branches
        self.__num_branches = num_branches
        self.__layers = layers

    def __add_all_branches(self, cur: sqlite3.Connection.cursor, tree_id: int, branches=None, num_branches=None):
        if branches is not None:
            size = num_branches
            if size is None:
                raise Exception('num_branches not provided')
        else:
            branches = self.branches
            size = self.num_branches

        click.echo('Adding branches to tree with tree_id={} ...'.format(tree_id))
        for i in range(size):
            branch = branches[i]
            cur.execute('INSERT INTO branches ("index", depth, length, width, angle, pos_x, pos_y, tree_id)'
                        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                        [i, branch.depth, branch.length, branch.width, branch.angle,
                         branch.pos.x, branch.pos.y, tree_id])

        click.echo('Done adding {} branches with tree_id={} ...'.format(size, tree_id))

    @property
    def app(self):
        return self.__app

    def _branches(self):
        branches = self.__branches
        return branches if branches else []

    def _layers(self):
        layers = self.__layers
        return layers if layers else []

    def _num_branches(self) -> int:
        return self.__num_branches


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
            self.__branches, self.__layers, self.__num_branches = generate_tree(max_depth=max_depth)
        else:
            self.__read_branches(file)

    def save_branches(self, **kwargs):
        fname = kwargs.get('file', 'tree')

        # use self.branches if branches kwarg not provided
        branches, num_branches = kwargs.get('branches', None), kwargs.get('num_branches', None)
        if branches is None:
            branches = self.branches
            num_branches = self.num_branches
        elif not num_branches:
            # branches kwarg provided but no num_branches provided
            raise Exception('num_branches not provided')

        stream = create_file(fname, relative=CACHE_DIR)

        with stream as file:
            click.echo('Saving branches to {} ...'.format(file.name))
            json.dump(branches[:num_branches], file, cls=BranchJSONEncoder)

    def __read_branches(self, fpath):
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
