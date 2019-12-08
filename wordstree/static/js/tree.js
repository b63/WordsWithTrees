const tree = {};

(function(global){
    global.tile_info_cache = {};
    global.tree_info_cache = {};

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

    function request_tree_info(tree_id) {
        let params = new URLSearchParams();
        params.append('id', tree_id);
        params.append('q', 'max_zoom');

        return fetch('/api/tree?' + params.toString(), {
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

        init_tree_info() {
            const _this = this;
            request_tree_info(this.id).then(function(json){
                for (let i = 0; i < json.length; ++i){
                    const info = json[i];
                    global.tree_info_cache[info['tree_id']] = info;
                }
            });
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

        change_zoom(center_x, center_y, i) {
            const tile_info = global.tile_info_cache[this.id][this.zoom];
            const max_zoom = global.tree_info_cache[this.id]['max_zoom'];
            const _this = this;

            const image_width = tile_info['image_width'], image_height = tile_info['image_height'];
            const origin_col = this.tile_origin_col, origin_row = this.tile_origin_row;
            const grid_size = tile_info['grid'];

            this.zoom = Math.min(max_zoom-1, this.zoom + i);
            this.removeAllChildren();
            this.init_grid().then(() => {
                const new_tile_info = global.tile_info_cache[_this.id][_this.zoom];
                const new_grid_size = new_tile_info['grid'];
                const new_image_width = new_tile_info['image_width'];
                const new_image_height = new_tile_info['image_height'];
                const new_tile_dx = 1/new_grid_size, new_tile_dy = 1/new_grid_size;

                // distance from top corner to center point
                const dcx_norm = (center_x - _this.x)/image_width/grid_size;
                const dcy_norm = (center_y - _this.y)/image_height/grid_size;

                // find coordinates of center point
                let cx_norm =  dcx_norm + origin_col / grid_size;
                let cy_norm =  dcy_norm + origin_row / grid_size;

                // distance to top corner to center point in units of zoomed grid
                const dcx_norm_new = (center_x - _this.x)/new_image_width/new_grid_size;
                const dcy_norm_new = (center_y - _this.y)/new_image_height/new_grid_size;

                // coordinate of top corner
                let x_norm = cx_norm - dcx_norm_new;
                let y_norm = cy_norm - dcy_norm_new;

                // floor to coordinate of top of a tile
                let tile_x_norm = Math.floor(x_norm/new_tile_dx)*new_tile_dy;
                let tile_y_norm = Math.floor(y_norm/new_tile_dy)*new_tile_dy;

                _this.load_tiles(tile_x_norm, tile_y_norm).then(function(value){
                    let shift_x = (x_norm * new_grid_size - _this.tile_origin_col) * new_image_width;
                    let shift_y = (y_norm * new_grid_size - _this.tile_origin_row) * new_image_height;

                    _this.x -= shift_x;
                    _this.y -= shift_y;
                    _this.stage.update();
                });

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
                                    tile.x = (j) * image_width;
                                    tile.y = (i) * image_height;
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

                if ( pan.panning || abs_dx > min_delta || abs_dy > min_delta) {
                    _this.stage.update();
                    requestAnimationFrame(() => inner(resolve, reject));
                } else {
                    const tile_info = global.tile_info_cache[_this.id][_this.zoom];
                    const tile_dx = tile_info['tile_width'], tile_dy = tile_info['tile_height'];
                    const image_width = tile_info['image_width'], image_height = tile_info['image_height'];
                    const origin_col = _this.tile_origin_col, origin_row = _this.tile_origin_row;
                    const grid_size = tile_info['grid'];

                    let dcol = floor_ceil(_this.x/image_width);
                    let drow = floor_ceil(_this.y/image_height);
                    console.log('x,y ', _this.x,',', _this.y, '  dcol,drow ', dcol,',', drow);

                    let x_norm = -dcol/grid_size + _this.tile_origin_col/grid_size  ;
                    let y_norm = -drow/grid_size + _this.tile_origin_row/grid_size;

                    _this.load_tiles(x_norm, y_norm).then(function(finished){
                        const dcol = _this.tile_origin_col - origin_col;
                        const drow = _this.tile_origin_row - origin_row;
                        console.log(dcol, drow);

                        _this.x -= -dcol * image_width;
                        _this.y -= -drow * image_height;
                        console.log('pos ', _this.x, _this.y);
                        _this.stage.update();
                    });

                    resolve();
                }
            }

            return new Promise(inner);
        } // end of animate_pan
    } // end of Tree class body

    function floor_ceil(x) {
        if (x < 0) {
            return Math.ceil(x);
        } else {
            return Math.ceil(x);
        }
    }


    global.Tree = Tree;

})(tree);
