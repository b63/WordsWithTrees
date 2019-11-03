function create_stage(canvas) {
    const stage = new createjs.Stage(canvas);
    stage.mouseChildren = false;

    const hit = new createjs.Shape();
    const draw_stage = function(){
        const g = hit.graphics;
        g.clear();
        g.beginFill('#fff').drawRect(0, 0, canvas.width, canvas.height);
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
        canvas.draw_stage();
    };

    resize_canvas();
    const sensor = new ResizeSensor(wrapper, resize_canvas);

    const frac_tree = create_tree(stage);
}

document.addEventListener('DOMContentLoaded', init);
