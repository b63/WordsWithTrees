const RADIANS = Math.PI/180;

function rand(high, low) {
    high = high || 1;
    low = low || -high;

    let range = Math.abs(high - low);
    return range * (Math.random()-0.5) + (low+high)/2.0;
}

class Branch extends createjs.Container {
    constructor(parent_branch, props){
        super();
        this.mouseChildren = false;
        this._pbranch = parent_branch;

        this._length = props['length'] || 5;
        this._depth = props['depth'] || 0;
        this._width = props['width'] || 5;
        this.rotation = props['angle'] || 180;
        this.x = props['x'] || 0;
        this.y = props['y'] || 0;

        this._endx = -this._length * Math.sin(this.rotation * RADIANS);
        this._endy = this._length * Math.cos(this.rotation * RADIANS);

        this._rect = this.create_rect();
        this.addChild(this._rect);
    }

    get depth(){
        return this._depth;
    }

    get angle() {
        return this.rotation;
    }

    get length() {
        return this._length;
    }

    get width() {
        return this._width;
    }

    get endy() {
        return this._endy;
    }

    get endx() {
        return this._endx;
    }

    get end(){
        return [this._endx, this._endy];
    }

    create_rect(){
        let rect = new createjs.Shape();
        let g = rect.graphics;
        let length = this.length;
        let w = this.width;
        g.beginFill('#000').drawRect(-w/2, 0, w/2, length);

        return rect;
    }
}

function init(e) {
    const canvas = document.getElementById('tree_canvas');
    const stage = new createjs.Stage(canvas);
    let hit = new createjs.Shape();
    hit.graphics.beginFill('#000').drawRect(0, 0, canvas.width, canvas.height);
    stage.hitArea = hit;


    const MAX_DEPTH = 15;
    const tree_list = new Array(Math.pow(2, MAX_DEPTH));
    let begin = -1, end = 0;
    let tree = new createjs.Container();
    tree.mouseChildren = false;

    function generate_branches(parent, depth) {
        const delta_angle = 20;
        const branches = new Array(2);
        const plength = parent.length, pangle = parent.angle, pwidth = parent.width;
        const pos_x = parent.x + parent.endx, pos_y = parent.y + parent.endy;

        let props = {
            depth: depth,
            x: pos_x,
            y: pos_y,
            width: 0.80*pwidth,
            length: Math.min(plength, 30)/1.05,
        };

        props.angle = pangle + 10 + rand(delta_angle);
        branches[0] = new Branch(parent, props);

        props.angle = pangle - 10 + rand(delta_angle);
        branches[1] = new Branch(parent, props);

        return branches;
    }

    function create_layer(depth) {
        if (depth > MAX_DEPTH || end >= tree_list.length)
        {
            console.log('reached max depth');
            return;
        }
        else if (depth === 0)
        {
            // create root of tree
            const root = new Branch(null, {
                width: 8,
                length: 150,
                x: canvas.width / 2,
                y: canvas.height
            });

            tree_list[++begin] = root;
            ++end;
        }
        else
        {
            const num_siblings = end - begin;
            for (let j = 0; j < num_siblings; ++j) {
                let parent = tree_list[begin++];
                let children = generate_branches(parent, depth);

                for (const branch of children) {
                    tree_list[end++] = branch;
                }
            }
        }
    }

    function animate_tree(i) {
        if (i >= end) {
            console.log('done animating tree ');
            tree.cache(0, 0, canvas.width, canvas.height);
            return;
        }

        const stop = Math.min(2*i+1, end);
        console.log(i, stop);
        while(i < stop) {
            tree.addChild(tree_list[i++]);
        }
        stage.update();
        createjs.Ticker.on('tick', function(){
            animate_tree(i);
        }, null, true);
    }

    for(let i = 0; i < MAX_DEPTH; ++i) {
        create_layer(i);
    }
    console.log(tree_list);

    stage.addChild(tree);
    stage.update();

    createjs.Ticker.framerate = 10;
    animate_tree(0);

    let startx = 0, starty = 0;
    stage.mouseChildren = false;
    stage.addEventListener('mousedown', function(ev){
        startx = ev.stageX;
        starty = ev.stageY;
        console.log('mousedown, ', startx, starty)
    });
    stage.addEventListener('pressmove', function(ev){
        let dx = ev.stageX - startx, dy = ev.stageY - starty;
        console.log('pressmove, ', dx, dy)
    });

    document.addEventListener('keypress', function(ev){
        const step = 10;
        if (ev.key === '+') {
            tree.scale += 0.1;
        }  else if (ev.key === '-') {
            tree.scale = Math.max(tree.scale-0.1, 0.05);
        } else if (ev.key === 'a') {
            tree.x -= step;
        } else if (ev.key === 'd') {
            tree.x += step;
        } else if (ev.key === 'w') {
            tree.y += step;
        } else if (ev.key === 's') {
            tree.y -= step;
        }
        stage.update();
    });
}


document.addEventListener('DOMContentLoaded', init);
