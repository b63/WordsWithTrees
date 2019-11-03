class Tree extends createjs.Container {
    constructor() {
        super();
        this.mouseChildren = false;
    }

    _getObjectsUnderPoint(x, y, mode) {
        return [];
    }

    _getObjectUnderPoint(x, y, mode) {
        return null;
    }
}

class FractalTree {
    constructor(max_depth, stage) {
        this._stage = stage;
        this._tree = new Tree();
        this._max_depth = max_depth;
        this._layers = [];
        //this._branches = new Array(Math.pow(4, max_depth));

        this.init_pan();
        this.init_zoom();
        this.create_all_layers();

        stage.addChild(this._tree);
    }

    create_all_layers() {
        const max_depth = this._max_depth;
        const _this = this;
        let i = 0;

        const f = function () {
            if (i <= max_depth) {
                _this.create_layer(i++)
                    .then(function (args) {
                        const depth = args[0];
                        console.log('created layer ', args[0]);
                        window.setTimeout(f, 0);
                    })
                    .catch(console.log);
            }
        };

        window.setTimeout(f, 0);
    }

    create_layer(depth) {
        const stage = this._stage;
        const canvas = stage.canvas;
        const tree = this._tree;
        const layers = this._layers;
        const branches = tree.children;

        if (depth > this._max_depth)
        {
            console.log('reached max depth');
        }
        else if (depth === 0)
        {
            // create root of tree
            layers.push(0);
            let width = Math.max(
                Math.floor(Math.abs(9 * randn_bm() + FractalTree.ROOT_WIDTH)),
                FractalTree.ROOT_MIN_WIDTH
            );
            branches.push(new Branch(null, {
                width: width,
                length: Math.floor(FractalTree.ROOT_LENGTH + 20 * randn_bm()),
                x: canvas.width / 2,
                y: canvas.height
            }));
            return Promise.resolve([0]);
        }
        else
        {
            const len = branches.length;
            let j = layers[layers.length - 1];
            const process = function (complete, quit) {
                const lim = j + 100;
                for (; j < lim && j < len; ++j) {
                    let parent = branches[j];
                    let children = FractalTree.generate_branches(parent, depth);

                    for (const branch of children) {
                        branches.push(branch);
                    }
                }
                if (j >= len) {
                    layers.push(len);
                    complete(depth);
                }
                stage.update();
            };
            return process_sparse(process, 100);
        }
    }

    init_pan() {
        const stage = this._stage;
        const tree = this._tree;
        let start_mpos = {x: 0, y: 0};
        let start_pos = {x: 0, y: 0}, target_pos = {x: 0, y: 0};

        stage.addEventListener('mousedown', function (ev) {
            start_mpos.x = ev.stageX;
            start_mpos.y = ev.stageY;
            start_pos.x = tree.x;
            start_pos.y = tree.y;
        });

        let updating_pos = false;
        stage.addEventListener('pressmove', function (ev) {
            let dx = ev.stageX - start_mpos.x, dy = ev.stageY - start_mpos.y;
            target_pos.x = start_pos.x + dx;
            target_pos.y = start_pos.y + dy;
            if (!updating_pos) {
                createjs.Ticker.on('tick', function () {
                    tree.set(target_pos);
                    stage.update();
                    updating_pos = false;
                }, null, true);
            }

            updating_pos = true;
        });
    }

    init_zoom() {
        const stage = this._stage;
        const canvas = stage.canvas;
        const tree = this._tree;
        const scroll_max = 20.0;

        let zooming = false, wheel = 0, lastest_mpos = {x: 0, y: 0};
        canvas.addEventListener('wheel', function (ev) {
            lastest_mpos.x = ev.clientX;
            lastest_mpos.y = ev.clientY;
            wheel += ev.deltaY;
            if (Math.abs(wheel) > scroll_max) {
                wheel = wheel < 0 ? scroll_max : scroll_max;
            }

            if (!zooming) {
                createjs.Ticker.on('tick', function () {
                    const rect = canvas.getBoundingClientRect();
                    const scale = tree.scale, offset = {
                        // coordinate of pixel under cursor relative to top left of scaled tree
                        x: (lastest_mpos.x - rect.x - tree.x),
                        y: (lastest_mpos.y - rect.y - tree.y)
                    };
                    // zoom in by more if already zoomed in
                    const dir = wheel < 0 ? -1 : 1;
                    let extra = scale > 2 ? dir * scale/10 : 0;
                    const nscale = Math.min(Math.max(scale + wheel / 20 + extra, 0.3), 20.0);
                    wheel = 0;

                    tree.scale = nscale;
                    // scaling the tree shifted the tree a little bit
                    // translate back so cursor remains in same place relative to tree
                    tree.x -= offset.x * (nscale / scale - 1);
                    tree.y -= offset.y * (nscale / scale - 1);

                    //tree.updateCache();
                    stage.update();
                    zooming = false;
                }, null, true);
            }
            ev.preventDefault();
            zooming = true;
        }, {capture: true});
    }

    static generate_branches(parent, depth) {
        const delta_angle = FractalTree.ANGLE_SPREAD;

        //const num_branches = Math.min(Math.floor(Math.abs(19*randn_bm())/(depth+1)), 3);
        const num_branches = 2;
        if (num_branches === 0) {
            return [];
        }

        const branches = new Array(num_branches);
        const plength = parent.length, pangle = parent.angle, pwidth = parent.width;
        const pos_x = parent.x + parent.endx, pos_y = parent.y + parent.endy;
        const base_length = Math.min(plength, FractalTree.MAX_BRANCH_LENGTH) / 1.03;

        let props = {
            depth: depth,
            x: pos_x,
            y: pos_y,
            width: 0.80 * pwidth,
        };

        const angles = [20, -20, 2.5, -2.5];
        for (let i = 0; i < branches.length; ++i) {
            props.angle = pangle + angles[i] + rand(delta_angle);
            props.length = Math.max(base_length + 5 * randn_bm() / (depth + 1), 0);

            let drift = Math.abs(props.angle - 180);
            if (drift > 30) {
                //props.length -= Math.min(rand(5, 0)/(drift+10), 1.2*props.length);
            }

            branches[i] = new Branch(parent, props);
        }

        return branches;
    }


    static get ROOT_LENGTH() {
        return 350;
    }

    static get MAX_BRANCH_LENGTH() {
        return 40;
    }

    static get ANGLE_SPREAD() {
        return 30;
    }

    static get ROOT_MIN_WIDTH() {
        return 15;
    }

    static get ROOT_WIDTH() {
        return 10;
    }

    get tree() {
        return this._tree;
    }

    get branches() {
        return this._branches;
    }

}


function create_tree(stage) {
    const MAX_DEPTH = 11;
    const canvas = stage.canvas;

    let tree = new FractalTree(MAX_DEPTH, stage);

    createjs.Ticker.framerate = 20;
    createjs.Ticker.on('tick', function () {
        stage.update();
    }, null, false);


    document.addEventListener('keypress', function (ev) {
        const step = 10;
        if (ev.key === '+') {
            tree.scale += 0.1;
        } else if (ev.key === '-') {
            tree.scale = Math.max(tree.scale - 0.1, 0.05);
        } else if (ev.key === 'a') {
            tree.x -= step;
        } else if (ev.key === 'd') {
            tree.x += step;
        } else if (ev.key === 'w') {
            tree.y += step;
        } else if (ev.key === 's') {
            tree.y -= step;
        } else if (ev.key === 'u') {
            //tree.updateCache();
            console.log('updated cache');
        }
        stage.update();
    });
    return tree;
}