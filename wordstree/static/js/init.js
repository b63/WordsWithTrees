function create_stage(canvas) {
    const stage = new createjs.Stage(canvas);
    stage.mouseChildren = false;

    const hit = new createjs.Shape();
    const SPACING = 150;
    const draw_stage = function(width, height){
        const g = hit.graphics;
        g.clear();
        const SPACING = Math.floor(Math.min(width, height) / 6) + 1;

        // background
        g.beginFill('#817e7e').drawRect(0, 0, canvas.width, canvas.height);

        // vertical lines
        g.beginStroke('#000');
        g.setStrokeStyle(0.5);
        let pos = 0;
        while(pos <= width) {
            g.moveTo(pos, 0);
            g.lineTo(pos, height);
            pos += SPACING;
        }

        // horizontal lines
        pos = 0;
        while(pos <= height) {
            g.moveTo(0, pos);
            g.lineTo(width, pos);
            pos += SPACING;
        }

        stage.update();
        hit.cache(0, 0, width, height);
    };

    stage.hitArea = hit;
    stage.addChild(hit);

    canvas.draw_stage = draw_stage;
    return stage;
}

function init(e) {
    const canvas = document.getElementById('tree_canvas');
    const stage  = create_stage(canvas);

    const wrapper = document.getElementById('canvas-wrapper');
    const resize_canvas = function(){
        const rect = wrapper.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;
        canvas.draw_stage(canvas.width, rect.height);

    };

    resize_canvas();
    const sensor = new ResizeSensor(wrapper, resize_canvas);

    //const frac_tree = create_tree(stage);
    const t = new tree.Tree(3, 1, stage);
    stage.addChild(t);

    t.init_tree_info();
    t.init_grid().then(value => t.load_tiles(0.5, 0.5)).then(
        function(value){
            console.log(value);
            console.log(t.children);
            stage.update();
        }
    );

    let mousepos = {x: 0, y: 0};
    document.addEventListener('keypress', function(event){
        const rect = canvas.getBoundingClientRect();
        const x = mousepos.x - rect.x;
        const y = mousepos.y - rect.y;

        if (event.key === 'i') {
            t.change_zoom(x, y, 1);
        } else if (event.key === 'o') {
            t.change_zoom(x, y, -1);
        }
    });

    let mousedown = false;
    canvas.addEventListener('mousedown', function(event){
        mousedown = true;
        const rect = canvas.getBoundingClientRect();
        t.pan.x = event.clientX - rect.x;
        t.pan.y = event.clientY - rect.y;
        console.log('mousedown: ', t.pan.x, t.pan.y)
    });

    document.addEventListener('mouseup', function(event){
        mousedown = false;
        t.pan.panning = false;
    });

    document.addEventListener('mousemove', function (event) {
        mousepos.x = event.clientX;
        mousepos.y = event.clientY;

        if(!mousedown) {
            return;
        }

        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.x;
        const y = event.clientY - rect.y;
        if (x < 0 || x > rect.width || y < 0 || y > rect.height) {
            mousedown = false;
            t.pan.panning = false;
            console.log('out of bounds');
            return;
        }

        t.pan.mousex = x;
        t.pan.mousey = y;
        if(!t.pan.panning) {
            t.pan.panning = true;
            console.log('started');
            t.animate_pan().then(function(value){
                console.log('ended');
            });
        }
    });

    console.log('Tree instance:', t);
}

document.addEventListener('DOMContentLoaded', init);
