from typing import Listimport osimport jsonimport mathimport cairoimport clickfrom flask import current_appfrom wordstree.graphics.branch import Branchfrom wordstree.graphics.util import Vec, radians, create_dir, Rect, rectangle_intersectfrom wordstree.graphics.loader import Loader, FileLoader, BranchJSONEncoderdef create_surface(zoom=0):    # name = 'tree_z{}.svg'.format(zoom)    # file = create_img_file(name, path='svg/')    # click.echo('saving svg to {} ...'.format(file.name))    surface = cairo.RecordingSurface(        cairo.Content.COLOR_ALPHA,        cairo.Rectangle(0, 0, Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT)    )    return surfacedef create_img_file(name, path=''):    dir = os.path.join(current_app.config['IMAGE_DIR'], path)    create_dir(dir)    pfile = os.path.join(dir, name)    file = open(pfile, mode='wb')    return filedef create_cache_file(name, path=''):    dir = os.path.join(current_app.config['CACHE_DIR'], path)    create_dir(dir)    pfile = os.path.join(dir, name)    file = open(pfile, mode='w')    return filedef __draw_point(ctx, x, y):    # utility function for drawing a point, helpful for debugging    ctx.arc(x, y, 0.0001, 0, 2 * math.pi)    ctx.fill()class Renderer:    BASE_WIDTH = 1024    BASE_HEIGHT = 1024    def __init__(self, max_layers=5):        # self.zoom_levels = [i for i in range(0, max_layers)]        self.zoom_levels = [3, 4, 5, 6, 9, 10, 11]        self.grid_levels = [4, 12, 21, 30, 40, 60, 80]    def setup_canvas(self, ctx):        ctx.scale(Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT)        # draw white background        ctx.set_source_rgb(1, 1, 1)        ctx.rectangle(0, 0, 1, 1)        ctx.fill()    def get_opacity(self, zoom: int, layer: int) -> float:        diff = layer - self.zoom_levels[zoom]        if diff < 0:            return 1.0        elif diff == 0:            return 0.5        elif diff == 1:            return 0.15        elif diff == 2:            return 0.05        elif diff == 3:            return 0.01        else:            return 0    def render_tree(self, loader: Loader, zoom=0):        layers = loader.layers        branches = loader.branches        num_branches = loader.num_branches        surface = create_surface(zoom=zoom)        ctx = cairo.Context(surface)        self.setup_canvas(ctx)        i, layeri = num_branches - 1, len(layers) - 1        next_layer = layers[layeri]        while i >= 0:            opacity = self.get_opacity(zoom, layeri)            if opacity > 0.0:                branches[i].draw(ctx, opacity=opacity)            i -= 1            if i == next_layer:                print('finished drawing layer {:d}...'.format(layeri))                layeri -= 1                next_layer = layers[layeri]        self._save_full_tree(surface, zoom, loader)        self._cache_tiles(surface, zoom, loader)    def _save_full_tree(self, surface: cairo.Surface, zoom: int, loader):        svg_file = create_img_file('tree_z{}.svg'.format(zoom), path='svg')        head, tail = os.path.split(svg_file.name)        click.echo('Saving svg of tree to {} ...'.format(tail))        pat = cairo.SurfacePattern(surface)        img = cairo.SVGSurface(svg_file, Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT)        ctx = cairo.Context(img)        ctx.set_source(pat)        ctx.paint()        # font options        ctx.set_font_size(0.001)        # draw grid        ctx.scale(Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT)        ctx.set_source_rgb(1, 0, 0)        ctx.set_line_width(0.0001)        grid = self.grid_levels[zoom]        dx = 1 / grid        draw_label = grid <= 40        for i in range(grid + 1):            x = i * dx            # horizontal line            ctx.new_path()            ctx.move_to(0, x)            ctx.line_to(1, x)            ctx.stroke()            # vertical line            ctx.new_path()            ctx.move_to(x, 0)            ctx.line_to(x, 1)            ctx.stroke()            if not draw_label:                continue            for j in range(grid + 1):                # draw label                y = j * dx + dx                ctx.save()                ctx.translate(x + 0.003, y - 0.003)                ctx.show_text('({}, {}):({:.2f}, {:.2f})'.format(i, j, x, y))                ctx.stroke()                ctx.restore()    def _cache_tiles(self, surface: cairo.Surface, zoom: int, loader: Loader):        pat = cairo.SurfacePattern(surface)        grid = self.grid_levels[zoom]        # dimension of each tile        dimx, dimy = Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT        # dimension of each tile in the original image        grid_dx = Renderer.BASE_WIDTH / grid        grid_dy = Renderer.BASE_HEIGHT / grid        # dimension of each tile in the original image        norm_grid_dx = 1 / grid        norm_grid_dy = 1 / grid        scale = grid_dx / dimx        imgdir = 'png/zoom_{}'.format(zoom)        jsondir = 'json/zoom_{}'.format(zoom)        click.echo('Rendering {} tiles {}x{} grid...'.format(grid*grid, grid, grid))        click.echo('  row ', nl=False)        for i in range(grid):            x = i * grid_dx            click.echo('{} '.format(i), nl=False)            for j in range(grid):                tile = cairo.ImageSurface(cairo.Format.RGB24, dimx, dimy)                ctx = cairo.Context(tile)                y = j * grid_dy                mat = cairo.Matrix(xx=scale, yy=scale, x0=x, y0=y)                pat.set_matrix(mat)                ctx.set_source(pat)                ctx.paint()                rect = Rect(Vec(i * norm_grid_dx, j * norm_grid_dy), norm_grid_dx, norm_grid_dy)                contained_branches = self._get_contained_branches(loader.branches, loader.num_branches, rect, zoom)                file_name = 'z{}_{:.0f}x{:.0f}@{}_{}'.format(zoom, grid_dx, grid_dy, i, j)                branch_file = create_cache_file(file_name + '.json', path=jsondir)                json.dump(contained_branches, branch_file, cls=BranchJSONEncoder)                img_file = create_img_file(file_name + '.png', path=imgdir)                tile.write_to_png(img_file)    def _get_contained_branches(self, branches: List[Branch], num_branches: int, rect: Rect, zoom: int):        hits = []        visible = self.zoom_levels[zoom]        for i in range(num_branches):            branch = branches[i]            if branch.depth > visible:                continue            if rectangle_intersect(rect, branch.rect):                hits.append(branch)        return hits    @property    def max_zoom_level(self):        return len(self.zoom_levels) - 1if __name__ == "__main__":    renderer = Renderer(max_layers=16)    renderer.render_tree(zoom=7)