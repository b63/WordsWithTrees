from typing import List
import os
import json
import math

import cairo
import click
from flask import current_app

from wordstree.graphics.branch import Branch
from wordstree.graphics.util import Vec, radians, create_dir, Rect, rectangle_intersect, path_from
from wordstree.graphics.loader import Loader, FileLoader, BranchJSONEncoder


def create_surface(zoom=0):
    surface = cairo.RecordingSurface(
        cairo.Content.COLOR_ALPHA,
        cairo.Rectangle(0, 0, Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT)
    )
    return surface


def create_cache_file(name, path='', binary=False):
    dir = os.path.join(current_app.config['CACHE_DIR'], path)
    create_dir(dir)

    pfile = os.path.join(dir, name)
    if binary:
        file = open(pfile, mode='wb')
    else:
        file = open(pfile, mode='w')
    return file, pfile


def __draw_point(ctx, x, y):
    # utility function for drawing a point, helpful for debugging
    ctx.arc(x, y, 0.0001, 0, 2 * math.pi)
    ctx.fill()


class Renderer:
    """
    Instances of this class are responsible for rendering the branches/tiles and saving them to disk
    """

    BASE_WIDTH = 1024
    BASE_HEIGHT = 1024
    # ZOOM_LEVELS = [3, 4, 5, 6, 9, 10, 11]
    # GRID_LEVELS = [4, 12, 21, 30, 40, 60, 80]
    ZOOM_LEVELS = [2, 3, 4, 5]
    GRID_LEVELS = [4, 12, 21, 30]

    def __init__(self, zoom_levels=None, grid_levels=None):
        # self.zoom_levels = [i for i in range(0, max_layers)]
        if not zoom_levels:
            # list containing of maximum depth of visible branches at a particular zoom_level
            # ex. if zoom_level=[2, 5]; then at zoom=1, branches at depth > 5 are not visible
            self.zoom_levels = Renderer.ZOOM_LEVELS

        if not grid_levels:
            # list containing size of grid at each zoom_level
            self.grid_levels = Renderer.GRID_LEVELS

        if len(self.zoom_levels) != len(self.grid_levels):
            raise Exception('not enough zoom_levels of grid_levels provided')

        self.__map = {}

    def __setup_canvas(self, ctx):
        ctx.scale(Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT)

        # draw white background
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, 1, 1)
        ctx.fill()

    def get_opacity(self, zoom: int, layer: int) -> float:
        diff = layer - self.zoom_levels[zoom]
        if diff < 0:
            return 1.0
        elif diff == 0:
            return 0.5
        elif diff == 1:
            return 0.15
        elif diff == 2:
            return 0.05
        elif diff == 3:
            return 0.01
        else:
            return 0

    def render_tree(self, loader: Loader, zoom=0):
        """
        Renders the branches contained in `loader.branches` as well as the tiles at zoom level `zoom`.

        :param loader: `Loader` instance containing the list of `Branch` objects representing the tree to be rendered
        :param zoom: zoom level of render the tree and generate the tiles at, see `zoom_levels` and `grid_levels`
        """
        layers = loader.layers
        branches = loader.branches
        num_branches = loader.num_branches

        surface = create_surface(zoom=zoom)

        ctx = cairo.Context(surface)
        self.__setup_canvas(ctx)

        print('  Rendering branches ...')
        num_layers = len(layers)
        if num_layers < 1:
            print('    no branches to render\r')
        else:
            depth = 0
            i = layers[depth]
            next_layer = layers[depth + 1] if depth+1 < num_layers else num_branches

            while i < num_branches:
                opacity = self.get_opacity(zoom, depth)
                if opacity > 0.0:
                    branches[i].draw(ctx, opacity=opacity)

                print('    layer {}, branch {:d} of {}, {:.0f}% \r'.format(
                    depth, i, num_branches, (i/num_branches)*100
                ), end='')
                i += 1
                if i == next_layer:
                    depth += 1
                    next_layer = layers[depth] if depth < num_layers else num_branches

        print()

        self.__map[zoom] = (surface, loader)

    def save_full_tree(self, zoom: int, saver: Loader):
        """
        Saves graphics of a tree previously rendered with :meth:`render_tree` as  a SVG file to disk under the name
        `tree_z<zoom>.svg`. If tree has not been rendered at zoom level `zoom`, an exception will be raised.
        :param zoom: zoom level of the tree, used for naming the file
        :param saver: :class:`Loader` instance containing information about where to save the image
        """
        rv = self.__map.get(zoom, None)
        if not rv:
            raise Exception('tree at zoom level {} must be rendered first'.format(zoom))

        surface, loader = rv
        if not saver:
            saver = loader

        svg_file, svg_file_path = create_cache_file(
            'tree_z{}.svg'.format(zoom), path='{}/images/svg'.format(saver.output_tree('tree_name')), binary=True
        )

        print('  Saving svg of tree to {} ...'.format(path_from(svg_file_path, 4)))
        pat = cairo.SurfacePattern(surface)
        img = cairo.SVGSurface(svg_file, Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT)

        ctx = cairo.Context(img)
        ctx.set_source(pat)
        ctx.paint()

        # font options
        ctx.set_font_size(0.001)

        # draw grid
        ctx.scale(Renderer.BASE_WIDTH, Renderer.BASE_HEIGHT)
        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(0.0001)

        grid = self.grid_levels[zoom]
        dx = 1 / grid
        draw_label = grid <= 40
        for i in range(grid + 1):
            x = i * dx
            # horizontal line
            ctx.new_path()
            ctx.move_to(0, x)
            ctx.line_to(1, x)
            ctx.stroke()

            # vertical line
            ctx.new_path()
            ctx.move_to(x, 0)
            ctx.line_to(x, 1)
            ctx.stroke()

            if not draw_label:
                continue

            for j in range(grid + 1):
                # draw label
                y = j * dx + dx
                ctx.save()
                ctx.translate(x + 0.003, y - 0.003)
                ctx.show_text('({}, {}):({:.2f}, {:.2f})'.format(i, j, x, y))
                ctx.stroke()
                ctx.restore()

    def cache_tiles(self, zoom: int, saver: Loader, saver_args: dict = None):
        """
        Render the tiles at zoom level :param:`zoom` and save the images and JSON file containing list of branches
        visible in them to the cache directory(`app.config['CACHE_DIR']`). If `loader` is not `None`, then zoom level
        information and tile information is also saved using `save_tile_info` and `save_zoom_info` methods in `loader`.

        If the loader instance requires additional argument(s), they are can be provided using `saver_args`, which will
        be passed as kwargs to all invocations of :meth:`Loader.save_tile` and :meth:`Loader.save_zoom_level`.

        :param zoom: zoom level to render tiles at, must be less than length of `self.zoom_levels`.
        :param saver: :class:`Loader` instance to call for saving information about tile and zoom level
        :param saver_args: additional arguments to pass to every call to `save_tile_info` and `save_zoom_info`
            methods of `loader`
        """
        surface, loader = self.__map.get(zoom, None)

        if surface is None:
            raise Exception('branches must be rendered at zoom level {} before tiles can be rendered'.format(zoom))

        pat = cairo.SurfacePattern(surface)
        grid = self.grid_levels[zoom]

        # dimension of each tile
        dimx, dimy = Renderer.BASE_WIDTH//4, Renderer.BASE_HEIGHT//4
        # dimension of each tile in the original image
        grid_dx = Renderer.BASE_WIDTH / grid
        grid_dy = Renderer.BASE_HEIGHT / grid
        # dimension of each tile in the original image
        norm_grid_dx = 1 / grid
        norm_grid_dy = 1 / grid

        scale = grid_dx / dimx

        if saver:
            tree_name = saver.output_tree('tree_name')
        else:
            tree_name = loader.output_tree('tree_name')
        imgdir = '{}/images/png/zoom_{}'.format(tree_name, zoom)
        jsondir = '{}/json/zoom_{}'.format(tree_name, zoom)

        # save information about current zoom level
        cache_info = saver is not None
        if cache_info:
            saver.save_zoom_info(
                zoom_level=zoom,
                grid=grid,
                tile_size=(grid_dx, grid_dy),
                img_size=(dimx, dimy),
                img_dir=imgdir,
                json_dir=jsondir,
                **saver_args
            )

        tile_index, num_tiles = 0, grid*grid
        print('  Rendering {}x{} grid...'.format(grid, grid))
        for i in range(grid):
            x = i * grid_dx
            x_norm = i * norm_grid_dx
            for j in range(grid):
                tile = cairo.ImageSurface(cairo.Format.RGB24, dimx, dimy)
                ctx = cairo.Context(tile)

                y = j * grid_dy
                y_norm = j * norm_grid_dy
                mat = cairo.Matrix(xx=scale, yy=scale, x0=x, y0=y)

                pat.set_matrix(mat)
                ctx.set_source(pat)
                ctx.paint()

                rect = Rect(Vec(x_norm, y_norm), norm_grid_dx, norm_grid_dy)
                contained_branches = self._get_contained_branches(loader.branches, loader.num_branches, rect, zoom)

                file_name = 'z{}_{:.0f}x{:.0f}@{}_{}'.format(zoom, grid_dx, grid_dy, i, j)

                branch_file, branch_filepath = create_cache_file(file_name + '.json', path=jsondir)
                json.dump(contained_branches, branch_file, cls=BranchJSONEncoder)

                img_file, img_filepath = create_cache_file(file_name + '.png', path=imgdir, binary=True)
                tile.write_to_png(img_file)

                if cache_info:
                    saver.save_tile_info(
                        zoom_level=zoom, img_path=img_filepath, json_path=branch_filepath,
                        # note: (j, i) = (ROW, COLUMN) is what method expects
                        grid_location=(j, i), tile_position=(x_norm, y_norm), tile_index=tile_index,
                        **saver_args
                    )

                tile_index += 1
                print('    tile {} out of {}, {:.1f}%\r'.format(
                    tile_index, num_tiles, tile_index / num_tiles * 100), end=''
                )
        print()

    def _get_contained_branches(self, branches: List[Branch], num_branches: int, rect: Rect, zoom: int):
        # returns list of branches contained in the rectangular region described by `rect`
        # the `zoom` parameter determines the maximum depth of the branch considered
        # if a branch is deeper than `self.zoom_levels[zoom]`, then it is not considered

        hits = []
        visible = self.zoom_levels[zoom]
        for i in range(num_branches):
            branch = branches[i]
            if branch.depth > visible:
                continue

            if rectangle_intersect(rect, branch.rect):
                hits.append(branch)
        return hits

    @property
    def max_zoom_level(self):
        return len(self.zoom_levels) - 1


if __name__ == "__main__":
    renderer = Renderer()
    renderer.render_tree(zoom=7)

