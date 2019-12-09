import click
from flask import current_app
from flask.cli import with_appcontext
import os

from wordstree.graphics.loader import Loader, FileLoader, DBLoader
from wordstree.graphics.render import Renderer
from .generate import generate_layer


def init_app(app):
    app.cli.add_command(render_tree)
    app.cli.add_command(add_layer)


def parse_range_list(string: str, max: int = 0, min: int = 0):
    """
    Parses list of integer ranges of the form "<range>,<range>,..." and returns a list containing those numbers
    <range> can be the following:
      1) an integer, eg. 1 or 22
      2) a closed range, eg. 1-3 or 8-10
      3) an open range, eg. -9, or 5- where the former corresponds to integers from `min` to 9 and latter
         the integers from 5 to `max`

    :param max: maximum integer in the list
    :param min: minimum integer in the list
    :return: list of integers that corresponds to the ranges in `string`
    """
    levels = set()
    items = string.split(',')
    if items is None:
        items = [string]

    for item in items:
        try:
            try:
                index = item.strip().index('-')
            except ValueError:
                index = -1

            if index >= 0:
                # parse range (0-9, 1-2, etc...)
                begin, end = item[:index], item[index + 1:]
                if not begin and not end:
                    raise click.BadParameter('range \'{}\' not valid'.format(item))

                begin = int(begin) if begin else min
                end = int(end) if end else max

                if begin < min or end > max:
                    raise click.BadParameter('\'{}\' range must be in the range {}-{}'
                                             .format(item, min, max))

                for i in range(begin, end + 1):
                    levels.add(i)
            else:
                level = int(item)
                if level < min or level > max:
                    raise click.BadParameter('\'{}\' number level must be in the range {}-{}'
                                             .format(item, min, max))
                levels.add(level)
        except ValueError:
            raise click.BadParameter('bad range or number \'{}\''.format(item))
    return sorted(list(levels))


def validate_zoom(ctx, param, value):
    parse_range_list(value, min=0, max=100)
    return value


# null character at the end of help messages as a temporary way to get new lines...
@click.command('render')
@click.option('-z', '--zoom', 'zooms', default='0',
              callback=validate_zoom,
              help='\b list of comma separated ranges, or integers that specify \'zoom\' level(s) to render the tree '
                   'at, higher number means more layers will be visible. \n'
                   'Examples:\n'
                   '(1)    \'1,2-5\' zoom levels 1, and 2 through 5 will be rendered\n'
                   '(2)    \'-5,6,7\' all zoom levels from 0 through 7 will be rendered.\n\0',
              )
@click.option('-d', '--depth', default=14,
              help='If generating new tree, specifies maximum depth of the tree, otherwise ignored.\n\0',
              type=int
              )
@click.option('-f', '--from', 'input_str', type=str, default='',
              help='Specifies where to read branches from; if left empty, a new tree will be generated. '
                   'Values can be (1) path to JSON file containing serialized array of branches, or (2)'
                   '\'db:<tree-id>\' where <tree-id> is the id of the tree where branches should be read from.\n\0'
              )
@click.option('-o', '--out', 'output_str', type=str, default='',
              help='Specifies where to save branches; if left empty (default), branches will not be stored. '
                   'See help on \'--from\' for help on other possible values.\n\0'
              )
@click.option('--cache-tiles/--no-cache-tiles', 'cache_tiles', is_flag=True, default=True,
              help='whether to render and write PNGs of tiles to disk, by default the tiles will be rendered\n\0'
              )
@click.option('--name', 'tree_name', default=None,
              help='Name of the tree; rendered images / json files will be stored in the directory of the same name '
                   'under the cache directory. If not provided, a default one will be generated if a new tree is being'
                   'generated.\n\0'
              )
@with_appcontext
def render_tree(zooms, depth, input_str: str, output_str: str, cache_tiles, tree_name):
    """
    Generates/Loads branches from database `branches` table or from local JSON file, and renders the branches
    at specified a specified 'zoom level'. The 'zoom' level restricts the highest depth of visible branch and the
    grid-size. For each square of the grid, a full-size image is saved to disk along with a JSON file containing a list
    of branches visible in the square.
    """

    print('Cache directory: {}'.format(current_app.config['CACHE_DIR']))

    input_str, output_str = input_str.strip(), output_str.strip()

    # load branches
    if input_str.startswith('db:') or input_str == 'db':
        tree_id = input_str[3:]
        loader = DBLoader(current_app)

        if tree_id:
            loader.load_branches(tree_id=int(tree_id))
        else:
            loader.load_branches(max_depth=depth, tree_name=tree_name)
    else:
        loader = FileLoader()
        input_str = input_str if input_str else None
        try:
            loader.load_branches(file=input_str, max_depth=depth, tree_name=tree_name)
        except FileNotFoundError:
            abpath = os.path.abspath(os.path.join(current_app.config['CACHE_DIR'], input_str))
            raise click.BadParameter(r"file '{}' does not exist".format(abpath))

    ren = Renderer()
    # bound check on zoom levels
    zooms = parse_range_list(zooms, max=ren.max_zoom_level, min=0)

    print('\nRendering tree with max depth {} at zoom level(s) {} ...'.format(depth, str(zooms).strip('[]')))

    num_zooms = len(zooms)
    for i in range(num_zooms):
        level = zooms[i]
        if i > 0:
            print()
        print('Zoom level: {}'.format(level))
        ren.render_tree(loader, zoom=level)

    # save branches
    save_kwargs = dict()
    if output_str.startswith('db:') or output_str == 'db':
        saver = DBLoader(current_app)
        tree_id = output_str[3:]
        tree_id = int(tree_id) if tree_id else None
        save_kwargs['tree_id'] = tree_id

        saver.save_branches(
            tree_id=tree_id,
            width=ren.BASE_WIDTH, height=ren.BASE_WIDTH,
            branches=loader.branches,
            num_branches=loader.num_branches,
            tree_name=tree_name
        )
    elif output_str:
        saver = FileLoader()
        save_kwargs['file'] = output_str

        saver.save_branches(
            file=output_str,
            branches=loader.branches,
            num_branches=loader.num_branches,
            tree_name=tree_name
        )
    else:
        saver = loader

    # render/cache tiles and save SVGs of full tree
    for i in range(num_zooms):
        if i == 0:
            print('\nRendering SVGs/tiles ...'.format())
        else:
            print()

        level = zooms[i]
        print('Zoom level: {}'.format(level))
        ren.save_full_tree(zoom=level, saver=saver)
        if cache_tiles:
            ren.cache_tiles(zoom=level, saver=saver, saver_args=save_kwargs)


# feature list:
#   add commmand - add layers to a tree
@click.command('add-layer')
@click.option('-f', '--from', 'input_str', type=str, default='',
              help='Specifies where existing branches to which to add new layers to are stored;'
                   'Values can be: \n'
                   '   \'db:<tree-id>\' where <tree-id> is the id of the tree where branches should be read from.'
                   '\n\0'
              )
@click.option('-n', '--layers', 'num_layers', type=int, default=1,
              help='Number of layers of branches to add (or remove if negative), if value is not specified defaults '
                   'to 1.\n\0'
              )
@click.option('--owner-id', 'owner_id', default=None,
              help='If not specified, no entry is added to "branches_ownership" table. If specified, adds an entry to '
                   '"branches_ownership" table for each new entry inserted to "branches" table with the given '
                   'owner-id. Other column values can be specified by with "--price", "--purchase", and "--text".\n'
                   'Note: If this option is not specified, no entry will be added to "branches_ownership" table even '
                   'if values for other columns are specified.\n\0'
              )
@click.option('--price', 'price', default=0,
              help='Value to set for "price" column of each new entry added to "branches_ownership" table for each new '
                   'entry added to "branches" table. Defaults to 0.\n\0'
              )
@click.option('--purchase', 'purchase', default=False,
              help='Value for "available_for_purchase" column for entries added to "branches_ownership" table. '
                   'Defaults to False.\n\0'
              )
@click.option('--text', 'text', default='',
              help='Value for "text" column for entries added to "branches_ownership" table. '
                   'Defaults to empty string \'\'.\n\0'
              )
@with_appcontext
def add_layer(input_str, num_layers=1, owner_id=None, price=0, purchase=False, text=''):
    """
    Add layers of branches to an existing tree in database.

    :param input_str: `db:<tree-id>` where `<tree-id>` is the id of the entry in the `tree` table
    :param num_layers: number of layers of branches to add to the `branches` table under the given tree-id
    :param owner_id: if not `None`, entries are also added to the `branches_ownership` table with the given `owner_id`
        column value. Other column values must be specified if this argument is not `None`. See :param:`price`,
        :param:`purchase`, and :param:`text`.
    :param price: value for the `price` column
    :param purchase: value for the `purchase` column
    :param text: value for the `text` column
    """
    input_str = input_str.strip()

    # load branches
    if input_str.startswith('db:'):
        tree_id = input_str[3:]
    else:
        tree_id = None

    if not tree_id:
        raise click.BadParameter('bad value \'{}\''.format(input_str))

    try:
        # load branches from database
        loader = DBLoader(current_app)
        loader.load_branches(tree_id=int(tree_id))
    except Exception as e:
        raise click.BadParameter(str(e))

    if len(loader.layers) == 0:
        depth, begin = 0, 0
    else:
        depth = len(loader.layers)
        begin = loader.layers[-1]
    # generate next layer using branches from loader.branches
    branches, num_branches = generate_layer(loader.branches, depth, begin,
                                            loader.num_branches)

    # generate the rest from the newly generated layers
    begin = 0
    for i in range(1, num_layers):
        depth += 1
        new_branches, added_branches = generate_layer(branches, depth, begin)
        begin = num_branches
        num_branches += added_branches
        branches.extend(new_branches)

    # create owner_info for each of the new branches
    owner_info = dict()
    if owner_id:
        info = {
            'owner_id': owner_id,
            'price': price,
            'available_for_purchase': purchase,
            'text': text
        }

        for i in range(num_branches):
            branch = branches[i]
            owner_info[branch.index] = info

    # update database
    loader.update_branches(tree_id, branches=branches, num_branches=len(branches), ownership_info=owner_info)
