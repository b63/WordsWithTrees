import math
import random
from typing import List, Tuple

from .branch import Branch
from .util import Vec, radians, JSONifiable, create_file, open_file

BRANCH_LENGTH_SHRINK_FACTOR = 1 / math.sqrt(2)
# BRANCH_LENGTH_SHRINK_FACTOR = 0.97
BRANCH_WIDTH_SHRINK_FACTOR = 0.8
BRANCH_LENGTH_DELTA = 0.01
BRANCH_ANGLE_DELTA = radians(10)
# BRANCH_ANGLES = (radians(20), radians(-20))
BRANCH_ANGLES = (1, -1)
MAX_BRANCH_LENGTH = 0.2
MAX_CHILDREN = 2


def generate_root() -> Branch:
    """
    Returns the 'stem' or trunk of the tree that has its `Branch.depth` attribute set to `0`.
    :return: :class:`Branch` object representing a stem or trunk of a possible tree
    """
    return Branch(
        0,
        Vec(0.5, 0.99),
        **{
            'length': 0.4,
            'width': 0.008
        }
    )


def generate_branches(parent: Branch, index: int, layer: int) -> List[Branch]:
    """
    Generate the child branches given a parent branch.

    :param parent: the :class:`Branch` object representing the parent branch
    :param index: index of the first child branch
    :param layer: layer of the child branches that are to be generated
    :return: a list of :class:`Branch` objects that have :param:`parent` as their parent branch.
    """
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
        # length = max(base_length + random.gauss(0, BRANCH_LENGTH_DELTA) / (layer + 1), 0)
        length = base_length
        # angle = pangle + BRANCH_ANGLES[i % nangles] + random.gauss(0, BRANCH_ANGLE_DELTA)
        angle = pangle + BRANCH_ANGLES[i % nangles] * math.pi / 2

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


def _create_branches(branches: List, max_layers=13):
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


def generate_tree(max_depth=10) -> Tuple[List, List[int], int]:
    """
    Generates and returns a list of :class:`Branch` objects representing a tree.
    :param max_depth: maximum layers of branches to generate
    :return: a tuple consisting of the list of :class:`Branch` objects representing the tree, a list of indicies that
        mark the beginning of each layer, and the number of branches created
    """
    print('Generating new tree max_depth={} ...'.format(max_depth))

    branches = [None for i in range(2 ** max_depth + 1)]
    layers, length = _create_branches(branches, max_layers=max_depth)

    print('  layers: {}'.format(layers))
    print('  number of branches: {}'.format(length))
    return branches, layers, length


def generate_layer(branches: List[Branch], depth: int, begin: int, end=None) -> Tuple[List[Branch], int]:
    """
    Generates and returns another layer of branches generated from the last layer of branches in :param:`branches`.

    :param branches: list of :class:`Branch` objects containing the layer of branches from which to generate the next
        layer.
    :param depth: depth of layer to generate; this is the depth that will be passed in when constructing :class:`Branch`
        objects
    :param begin: index in :param:`branches` containing the first branch of the layer.
    :param end: index that marks the end of the layer in :param:`branches` (item at `end-1` index in :param:`branches`
        should contain the last branch in the layer, if one exists.
    :return: a tuple consisting of the list of new branches created and the number of branches created
    """
    if not end:
        end = len(branches)

    new_branches = []

    if depth == 0:
        # generate root
        new_branches.append(generate_root())
    else:
        layer_end = end
        # index of first child branch
        index = branches[begin].index + end-begin

        while begin < layer_end:
            parent = branches[begin]
            sub_branches = generate_branches(parent, index, depth)

            for j in range(len(sub_branches)):
                new_branches.append(sub_branches[j])
                index += 1
                end += 1
            begin += 1

    return new_branches, len(new_branches)
