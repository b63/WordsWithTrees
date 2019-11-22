import click

from wordstree.graphics.loader import Loader, FileLoader
from wordstree.graphics.render import Renderer


def init_app(app):
    app.cli.add_command(render_tiles)


def parse_range_list(string: str, max: int = 0, min: int = 0):
    levels = set()
    items = string.split(',')
    if items is None:
        items = [string]

    for item in items:
        try:
            try:
                index = item.index('-')
            except ValueError:
                index = -1

            if index >= 0:
                # parse range (0-9, 1-2, etc...)
                begin, end = item[:index], item[index+1:]
                if not begin and not end:
                    raise click.BadParameter('range \'{}\' not valid'.format(item))

                begin = int(begin) if begin else min
                end = int(end) if end else max

                if begin < min or end > max:
                    raise click.BadParameter('\'{}\' range must be in the range {}-{}'
                                             .format(item, min, max))

                for i in range(begin, end+1):
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
@click.command('render-tiles')
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
                   '\'db:<table>\' where <table> is the SQLite table where branches should be read from.\n\0'
              )
@click.option('-o', '--out', 'output_str', type=str, default='',
              help='Specifies where to save branches; if left empty (default), branches will not be stored. '
                   'See help on \'--from\' for help on other possible values.\n\0'
              )
def render_tiles(zooms, depth, input_str, output_str):
    """
    Renders tree of specified max-depth and at specified zoom level to file.
    """

    loader = FileLoader()
    input_str = input_str if input_str else None
    loader.load_branches(file=input_str, max_depth=depth)

    ren = Renderer(max_layers=depth)

    # bound check on zoom levels
    zooms = parse_range_list(zooms, max=ren.max_zoom_level, min=0)

    click.echo('Rendering tree with max depth {} at zoom level(s) {} ...'.format(depth, str(zooms).strip('[]')))

    for level in zooms:
        click.echo('rendering at zoom level {} ...'.format(level))
        ren.render_tree(loader, zoom=level)
        click.echo('')

    if output_str:
        loader.save_branches(file=output_str)
