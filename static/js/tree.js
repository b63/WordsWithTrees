const RADIANS = Math.PI/180;

function rand(high, low) {
    high = high || 1;
    low = low || -high;

    let range = Math.abs(high - low);
    return range * (Math.random()-0.5) + (low+high)/2.0;
}

// from https://stackoverflow.com/questions/25582882/javascript-math-random-normal-distribution-gaussian-bell-curve
function randn_bm() {
    let u = 0, v = 0;
    while(u === 0) u = Math.random(); //Converting [0,1) to (0,1)
    while(v === 0) v = Math.random();
    return Math.sqrt( -2.0 * Math.log( u ) ) * Math.cos( 2.0 * Math.PI * v );
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

        let offx = (this._width/2)* Math.cos((this.rotation+90) *RADIANS);
        let offy = (this._width/2)* Math.sin((this.rotation+90) *RADIANS);
        this._endx = -this._length * Math.sin(this.rotation * RADIANS) - offx;
        this._endy = this._length * Math.cos(this.rotation * RADIANS) - offy;

        this._rect = this.create_rect();
        this._text = this.create_text();

        this.addChild(this._rect);
        //this.addChild(this._text);
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
        const rect = new createjs.Shape();
        const g = rect.graphics;
        const length = this.length, depth = this.depth, w = this.width;
        const red = Math.min(2*depth+50, 160);
        const green = Math.min(depth*depth+50, 255);
        const blue = Math.min(14*depth+50, 125);
        const color = 'rgba(' + red + ',' + green + ',' + blue +',' + 1 + ')';

        g.beginFill(color).drawRect(-w/2, 0, w/2, length);
        return rect;
    }

    create_text() {
        const length = this.length, depth = this.depth, w = this.width;
        const text = new createjs.Text(''+this._depth, (2*w)+'px Courier', '#ff0');
        text.rotation = 180;
        const b = text.getBounds();
        text.y = this._length/2;
        text.x = b.width/4;
        text.cache(0, 0, b.width, b.height+1);

        return text;
    }
}

class Tree extends createjs.Container {
    constructor(){
        super();
    }

    _getObjectsUnderPoint(x, y, mode){
        console.log('shitting fucking shit');
        return [];
    }

    _getObjectUnderPoint(x, y, mode){
        console.log('another fucking shit');
        return null;
    }
}
function init(e) {
    const canvas = document.getElementById('tree_canvas');
    const stage = new createjs.Stage(canvas);
    let hit = new createjs.Shape();
    hit.graphics.beginFill('#fff').drawRect(0, 0, canvas.width, canvas.height);
    stage.hitArea = hit;
    stage.addChild(hit);
    stage.mouseChildren = false;


    const MAX_DEPTH = 10;
    const tree_list = new Array(Math.pow(4, MAX_DEPTH));
    let begin = -1, end = 0;
    let tree = new Tree();
    tree.mouseChildren = false;

    function generate_branches(parent, depth) {
        const delta_angle = 30;

        //const num_branches = Math.min(Math.floor(Math.abs(19*randn_bm())/(depth+1)), 3);
        const num_branches = 2;
        if (num_branches === 0) {
            return [];
        }

        const branches = new Array(num_branches);
        const plength = parent.length, pangle = parent.angle, pwidth = parent.width;
        const pos_x = parent.x + parent.endx, pos_y = parent.y + parent.endy;
        const base_length = Math.min(plength, 30)/1.03;

        let props = {
            depth: depth,
            x: pos_x,
            y: pos_y,
            width: 0.80*pwidth,
        };

        const angles = [20, -20, 2.5, -2.5];
        for (let i = 0; i < branches.length; ++i) {
            props.angle = pangle + angles[i] + rand(delta_angle);
            props.length = Math.max(base_length + 5*randn_bm()/(depth + 1), 0);

            let drift = Math.abs(props.angle - 180);
            if(drift > 30) {
                //props.length -= Math.min(rand(5, 0)/(drift+10), 1.2*props.length);
            }

            branches[i] = new Branch(parent, props);
        }

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
                width: Math.max(Math.floor(Math.abs(9*randn_bm()+9)), 2),
                length: Math.floor(150 + 50*randn_bm()),
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
            //tree.cache(0, 0, canvas.width, canvas.height);
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

    createjs.Ticker.framerate = 30;
    animate_tree(0);

    let start_mpos = {x:0, y:0};
    let start_tree_pos = {x:0, y:0}, target_tree_pos = {x:0, y:0};
    let updating_pos = false;
    stage.addEventListener('mousedown', function(ev){
        start_mpos.x = ev.stageX;
        start_mpos.y = ev.stageY;
        start_tree_pos.x = tree.x;
        start_tree_pos.y = tree.y;
    });
    stage.addEventListener('pressmove', function(ev){
        let dx = ev.stageX - start_mpos.x, dy = ev.stageY - start_mpos.y;
        target_tree_pos.x = start_tree_pos.x + dx;
        target_tree_pos.y = start_tree_pos.y + dy;
        if(!updating_pos) {
            createjs.Ticker.on('tick', function(){
                tree.set(target_tree_pos);
                stage.update();
                updating_pos = false;
            }, null, true);
        }

        updating_pos = true;
    });

    let zooming = false, wheel = 0, lastest_mpos = {x: 0, y:0};
    const scroll_max = 20.0;
    canvas.addEventListener('wheel', function(ev){
        lastest_mpos.x = ev.clientX;
        lastest_mpos.y = ev.clientY;
        wheel += ev.deltaY;
        if (Math.abs(wheel) > scroll_max) {
            wheel = wheel < 0 ? scroll_max : scroll_max;
        }

        if(!zooming) {
            createjs.Ticker.on('tick', function(){
                const rect = canvas.getBoundingClientRect();
                const scale = tree.scale, offset = {
                    // coordinate of pixel under cursor relative to top left of scaled tree
                    x: (lastest_mpos.x - rect.x - tree.x),
                    y: (lastest_mpos.y - rect.y - tree.y)
                };
                const nscale = Math.min(Math.max(scale+wheel/20, 0.3), 20.0);
                wheel = 0;

                tree.scale = nscale;
                // scaling the tree shifted the tree a little bit
                // translate back so cursor remains in same place relative to tree
                tree.x -= offset.x*(nscale/scale-1);
                tree.y -= offset.y*(nscale/scale-1);

                //tree.updateCache();
                stage.update();
                zooming = false;
            }, null, true);
        }
        ev.preventDefault();
        zooming = true;
    }, {capture: true});

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
        } else if (ev.key === 'u') {
            //tree.updateCache();
            console.log('updated cache');
        }
        stage.update();
    });
}


document.addEventListener('DOMContentLoaded', init);
