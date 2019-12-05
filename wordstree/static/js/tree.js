const tree = {};

(function(global){
    global.tile_info_cache = {};

    function request_zoom_info(tree_id, zoom_level) {
        let params = new URLSearchParams();
        params.append('q', `${zoom_level},${tree_id}`);

        return fetch('/api/zoom?' + params.toString(), {
            method: 'GET'
        }).then(function(response){
            if(!response.ok || response.status !== 200)
                throw new Error(response.statusText);
            return response.json()
        })
    }

    function request_tile(row, col, zoom, tree_id, type) {
        let params = new URLSearchParams();
        params.append('zoom', zoom);
        params.append('tree-id', tree_id);
        params.append('row', row);
        params.append('col', col);
        params.append('type', type || 'json');

        return fetch('/api/tile?' + params.toString(), {
            method: 'GET'
        });
    }

    class Tree extends createjs.Container {
        constructor(tree_id, zoom_level) {
            super();
            this.id = tree_id;
            this.zoom = zoom_level;

            this.grid = null;
            this._pivot_row = 0;
            this._pivot_col = 0;
            this.tile_origin_row = 0;
            this.tile_origin_col = 0;

            // for animating
            this.pan = {x: 0, y: 0, dx: 0, dy: 0, mousex: 0, mousey: 0, panning: false};
        }

        init_grid() {
            const canvas = this.stage.canvas;
            const id = this.id, zoom = this.zoom;
            const _this = this;

            return request_zoom_info(id, zoom).then(function(response){
                const height = canvas.height, width = canvas.width;
                const tile_info = response[0];
                if(!global.tile_info_cache[id])
                {
                    const obj = {};
                    obj[zoom] = tile_info;
                    global.tile_info_cache[id] = obj;
                }
                else
                {
                    global.tile_info_cache[id][zoom] = tile_info;
                }


                const cols = Math.min(Math.floor(width/tile_info['image_width']) + 2, tile_info.grid);
                const rows = Math.min(Math.floor(height/tile_info['image_height']) + 2, tile_info.grid);
                const grid = new Array(rows);

                for(let i = 0; i < rows; ++i) {

                    grid[i] = new Array(cols);
                    for(let j = 0; j < cols; ++j) {
                        // to avoid creating new Tile object every time
                        const tile = new Tile(null, null, null, null)
                        grid[i][j] = tile;
                        _this.addChild(tile);
                    }
                }

                _this.grid = grid;
            });
        }

        load_tiles(x_norm, y_norm) {
            const canvas = this.stage.canvas;
            const id = this.id, zoom = this.zoom;
            const _this = this;

            const tile_info = global.tile_info_cache[id][zoom];
            const image_width = tile_info['image_width'], image_height = tile_info['image_height'];
            const grid = this.grid;
            const rows = grid.length, cols = grid[0].length;

            // find the row,col of the tile that contains the point (x_norm, y_norm)
            // it will be placed on the top left, if possible
            x_norm = Math.max(x_norm, 0);
            y_norm = Math.max(y_norm, 0);
            const origin_col = Math.min(Math.floor(x_norm*tile_info.grid), tile_info.grid - cols);
            const origin_row = Math.min(Math.floor(y_norm*tile_info.grid), tile_info.grid - rows);
            console.log('origin:', origin_row, origin_col);

            // find new pivot in the grid
            let grid_row = ((origin_row - this.tile_origin_row ) % rows) + this._pivot_row;
            let grid_col = ((origin_col - this.tile_origin_col ) % cols) + this._pivot_col;
            if (grid_row < 0) { grid_row += rows; }
            if (grid_col < 0) { grid_col += cols; }
            console.log('pivot:', grid_row, grid_col);

            // update tile origin position
            this.tile_origin_row = origin_row;
            this.tile_origin_col = origin_col;
            this._pivot_row = grid_row;
            this._pivot_col = grid_col;

            const inner = function inner(resolve, reject)
            {
                let total = 0, requests_done = false;
                let finished = 0;
                for (let i = 0; i < rows; ++i)
                {
                    const tile_row = i + origin_row;
                    const _grid_row = (i + grid_row) % rows;
                    const row_arr = grid[_grid_row];
                    for (let j = 0; j < cols; ++j)
                    {
                        const tile_col = j + origin_col;
                        const _grid_col = (j + grid_col) % cols;
                        let tile = row_arr[_grid_col];

                        if (tile_row === tile.tile_row && tile_col === tile.tile_col) {
                            // same tile, no need to request the same tile
                            tile.x = j * image_width;
                            tile.y = i * image_height;
                            _this.stage.update();
                            continue;
                        }

                        // not same, need to request tile
                        total += 1;
                        let image = null;
                        let branches = null;
                        request_tile(tile_row, tile_col, zoom, id, 'img')
                            .then(response => response.blob())
                            .then(createImageBitmap)
                            .then(
                                function (bitmap) {
                                    image = bitmap;
                                    return request_tile(tile_row, tile_col, zoom, id, 'json');
                                }
                            )
                            .then(response => response.json())
                            .then(
                                function (json) {
                                    if(_this.tile_origin_row !== origin_row && _this.tile_origin_col !== origin_col)
                                        reject();
                                    branches = json[0] || [];
                                    tile.set_tile(image, branches, tile_row, tile_col);
                                    tile.x = j * image_width;
                                    tile.y = i * image_height;
                                    _this.stage.update();

                                    finished += 1;
                                    if (requests_done && finished >= total) {
                                        resolve(finished);
                                    }
                                }
                            )
                            .catch(function(reason){
                                console.error(reason.toString());
                            });
                    }
                }
                requests_done = true;
                if(finished >= total) {
                    resolve(finished);
                }
            }; // end of inner function body

            return new Promise(inner);
        } // end of init_tiles body

        animate_pan() {
            const drag = 0.2;
            const accel = 0.99;
            const _this = this;
            const min_delta = 1;

            this.pan.x = this.pan.mousex;
            this.pan.y = this.pan.mousey;
            this.pan.dx = 0;
            this.pan.dy = 0;

            function inner(resolve, reject){
                const pan = _this.pan;
                const diffx = (pan.mousex - pan.x);
                const diffy = (pan.mousey - pan.y);

                pan.dx += diffx * accel;
                pan.dy += diffy * accel;

                pan.dx *= drag;
                pan.dy *= drag;

                let abs_dx = Math.abs(diffx);
                let abs_dy = Math.abs(diffx);

                //if (abs_dx < min_delta) { pan.dx = diffx; }
                //if (abs_dy < min_delta) { pan.dy = diffy; }

                pan.x += pan.dx;
                pan.y += pan.dy;

                let nx = _this.x + pan.dx;
                let ny = _this.y + pan.dy;

                _this.x = nx;
                _this.y = ny;
                _this.stage.update();

                if ( pan.panning || abs_dx > min_delta || abs_dy > min_delta) {
                    requestAnimationFrame(() => inner(resolve, reject));
                } else {
                    const tile_info = global.tile_info_cache[_this.id][_this.zoom];
                    const tile_dx = tile_info['tile_width'], tile_dy = tile_info['tile_height'];
                    const origin_col = _this.tile_origin_col, origin_row = _this.tile_origin_row;
                    const grid_size = tile_info['grid'];

                    let x_norm = -_this.x/grid_size/tile_dx + _this.tile_origin_col/grid_size  ;
                    let y_norm = -_this.y/grid_size/tile_dy + _this.tile_origin_row/grid_size;

                    _this.load_tiles(x_norm, y_norm).then(function(finished){
                        const dcol = _this.tile_origin_col - origin_col;
                        const drow = _this.tile_origin_row - origin_row;
                        console.log(dcol, drow);

                        _this.x += dcol * tile_dx - Math.abs(_this.x % tile_dx);
                        _this.y += drow * tile_dy - Math.abs(_this.y % tile_dy);
                        _this.stage.update();
                    });

                    resolve();
                }
            }

            return new Promise(inner);
        } // end of animate_pan
    } // end of Tree class body



    global.Tree = Tree;

})(tree);
