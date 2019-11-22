import randomfrom typing import Listimport osimport cairofrom flask import current_app, gfrom flask.cli import with_appcontextimport clickfrom wordstree.graphics import *from wordstree.graphics.util import Vec, radians, create_dirfrom wordstree.graphics.branch import Branchfrom wordstree.graphics.loader import Loader, FileLoaderfrom functools import partialIMAGE_DIR = 'wordstree/cache/images'def create_surface(zoom=0):    # name = 'tree_z{}.svg'.format(zoom)    # file = create_img_file(name, path='svg/')    # click.echo('saving svg to {} ...'.format(file.name))    surface = cairo.RecordingSurface(        cairo.Content.COLOR_ALPHA,        cairo.Rectangle(0, 0, Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT)    )    return surfacedef create_img_file(name, path=''):    dir = os.path.join(IMAGE_DIR, path)    create_dir(dir)    pfile = os.path.join(dir, name)    file = open(pfile, mode='wb')    return fileclass Renderer:    BASE_WIDTH = 1024    BASE_HEIGHT = 1024    def __init__(self, max_layers=5):        # self.zoom_levels = [i for i in range(0, max_layers)]        self.zoom_levels = [5, 6, 7, 8, 9, 10, 11]        self.grid_levels = [4, 8, 16, 24, 40, 60, 80]    def setup_canvas(self, ctx):        ctx.scale(Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT)        # draw white background        ctx.set_source_rgb(1, 1, 1)        ctx.rectangle(0, 0, 1, 1)        ctx.fill()        ctx.set_source_rgb(1, 0, 0)        ctx.rectangle(0, 0, 0.01, 0.1)        ctx.fill()        ctx.set_source_rgb(0, 1, 0)        ctx.rectangle(0, 0, 0.1, 0.01)        ctx.fill()        ctx.set_source_rgb(1, 0, 1)        ctx.rectangle(0, 0, 1, 1)        ctx.set_line_width(0.01)        ctx.stroke()        ratio = 0.9        ctx.translate(0.5, 1)        ctx.scale(ratio, ratio)        ctx.translate(-0.5, -1)        # draw boundary        ctx.set_source_rgb(0, 0, 0)        ctx.rectangle(0, 0, 1, 1)        ctx.set_line_width(0.01)        ctx.stroke()    def get_opacity(self, zoom: int, layer: int) -> float:        diff = layer - zoom        if diff <= 0:            return 1.0        elif diff == 1:            return 0.5        elif diff == 2:            return 0.15        elif diff == 3:            return 0.05        else:            return 0    def render_tree(self, loader: Loader, zoom=0):        layers = loader.layers        branches = loader.branches        num_branches = loader.num_branches        surface = create_surface(zoom=zoom)        ctx = cairo.Context(surface)        self.setup_canvas(ctx)        i, layeri = num_branches - 1, len(layers) - 1        next_layer = layers[layeri]        while i >= 0:            opacity = self.get_opacity(zoom, layeri)            if opacity > 0.0:                branches[i].draw(ctx, opacity=opacity)            i -= 1            if i == next_layer:                print('finished drawing layer {:d}...'.format(layeri))                layeri -= 1                next_layer = layers[layeri]        self.save_full_tree(surface, zoom)        self.cache_tiles(surface, zoom)    def save_full_tree(self, surface: cairo.Surface, zoom: int):        svg_file = create_img_file('tree_z{}.svg'.format(zoom), path='svg')        click.echo('Saving svg of tree to {} ...'.format(svg_file.name))        pat = cairo.SurfacePattern(surface)        img = cairo.SVGSurface(svg_file, Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT)        ctx = cairo.Context(img)        ctx.set_source(pat)        ctx.paint()    def cache_tiles(self, surface: cairo.Surface, zoom: int):        pat = cairo.SurfacePattern(surface)        grid = self.grid_levels[zoom]        # dimension of each tile        dimx, dimy = Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT        # dimension of each tile in the original image        grid_dx = Renderer.BASE_WIDTH / grid        grid_dy = Renderer.BASE_HEIGHT / grid        scale = grid_dx / dimx        dir = 'png/zoom_{}'.format(zoom)        for i in range(grid):            x = i * grid_dx            for j in range(grid):                tile = cairo.ImageSurface(cairo.Format.RGB24, dimx, dimy)                ctx = cairo.Context(tile)                y = j * grid_dy                mat = cairo.Matrix(xx=scale, yy=scale, x0=x, y0=y)                pat.set_matrix(mat)                ctx.set_source(pat)                ctx.paint()                file = create_img_file('z{}_{:.0f}x{:.0f}@{}_{}.png'.format(zoom, grid_dx, grid_dy, i, j), path=dir)                click.echo('Saving tile at ({:.2f}, {:.2f}) to {}'.format(x, y, file.name))                tile.write_to_png(file)    @property    def max_zoom_level(self):        return len(self.zoom_levels)-1def init_app(app):    app.cli.add_command(render_tiles)def parse_range_list(string: str, max: int=0, min:int = 0):    levels = set()    items = string.split(',')    if items is None:        items = [string]    for item in items:        try:            index = item.index('-')            if index >= 0:                # parse range (0-9, 1-2, etc...)                begin, end = item[:index], item[index+1:]                if not begin and not end:                    raise click.BadParameter('range \'{}\' not valid'.format(item))                begin = int(begin) if begin else min                end = int(end) if end else max                if begin < min or end > max:                    raise click.BadParameter('\'{}\' range must be in the range {}-{}'                                             .format(item, min, max))                for i in range(begin, end+1):                    levels.add(i)            else:                level = int(item)                if level < min or level > max:                    raise click.BadParameter('\'{}\' number level must be in the range {}-{}'                                             .format(item, min, max))                levels.add(level)        except ValueError:            raise click.BadParameter('bad range or number \'{}\''.format(item))    return sorted(list(levels))def validate_zoom(ctx, param, value):    parse_range_list(value, min=0, max=100)    return value# null character at the end of help messages as a temporary way to get new lines...@click.command('render-tiles')@click.option('-z', '--zoom', 'zooms', default='0',              callback=validate_zoom,              help='\b list of comma separated ranges, or integers that specify \'zoom\' level(s) to render the tree '                   'at, higher number means more layers will be visible. \n'                   'Examples:\n'                   '(1)    \'1,2-5\' zoom levels 1, and 2 through 5 will be rendered\n'                   '(2)    \'-5,6,7\' all zoom levels from 0 through 7 will be rendered.\n\0',              )@click.option('-d', '--depth', default=14,              help='If generating new tree, specifies maximum depth of the tree, otherwise ignored.\n\0',              type=int              )@click.option('-f', '--from', 'input_str', type=str, default='',              help='Specifies where to read branches from; if left empty, a new tree will be generated. '                   'Values can be (1) path to JSON file containing serialized array of branches, or (2)'                   '\'db:<table>\' where <table> is the SQLite table where branches should be read from.\n\0'              )@click.option('-o', '--out', 'output_str', type=str, default='',              help='Specifies where to save branches; if left empty (default), branches will not be stored. '                   'See help on \'--from\' for help on other possible values.\n\0'              )def render_tiles(zooms, depth, input_str, output_str):    """    Renders tree of specified max-depth and at specified zoom level to file.    """    loader = FileLoader()    input_str = input_str if input_str else None    loader.load_branches(file=input_str, max_depth=depth)    ren = Renderer(max_layers=depth)    # bound check on zoom levels    zooms = parse_range_list(zooms, max=ren.max_zoom_level, min=0)    click.echo('Rendering tree with max depth {} at zoom level(s) {} ...'.format(depth, str(zooms).strip('[]')))    for level in zooms:        click.echo('rendering at zoom level {} ...'.format(level))        ren.render_tree(loader, zoom=level)        click.echo('')    if output_str:        loader.save_branches(file=output_str)if __name__ == "__main__":    renderer = Renderer(max_layers=16)    renderer.render_tree(zoom=7)