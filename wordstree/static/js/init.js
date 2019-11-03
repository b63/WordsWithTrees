function create_stage(canvas) {
    const stage = new createjs.Stage(canvas);
    let hit = new createjs.Shape();
    hit.graphics.beginFill('#fff').drawRect(0, 0, canvas.width, canvas.height);
    stage.hitArea = hit;
    stage.addChild(hit);
    stage.mouseChildren = false;

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
    };

    resize_canvas();
    const sensor = new ResizeSensor(wrapper, resize_canvas);

    const frac_tree = create_tree(stage);
}

document.addEventListener('DOMContentLoaded', init);
