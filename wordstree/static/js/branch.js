class Branch extends createjs.Container {
    constructor(parent_branch, props){
        super();
        this.mouseChildren = false;
        this._pbranch = parent_branch;

        this._length = props['length'] || 5;
        this._depth = props['depth'] || 0;
        this._width = props['width'] || 10;
        this.rotation = props['angle'] || 180;
        this.x = props['x'] || 0;
        this.y = props['y'] || 0;

        let offx = (this._width/2)* Math.cos((this.rotation+90) *RADIANS);
        let offy = (this._width/2)* Math.sin((this.rotation+90) *RADIANS);
        this._endx = -this._length * Math.sin(this.rotation * RADIANS) - offx;
        this._endy = this._length * Math.cos(this.rotation * RADIANS) - offy;

        this._rect = this.create_rect();
        this.draw_rect();

        //this._text = this.create_text();
        //this.draw_text();

        this.alpha_animate(0, 1, 0.05);

        this.addChild(this._rect);
        //this.addChild(this._text);
    }

    alpha_animate(start, end, step){
        step = step || 0.1;
        end = end || 1;

        const rect = this._rect;
        this._alpha = start;
        const _this = this;

        const list = function (event) {
            if(_this._alpha > end) {
                _this._alpha = end;
                rect.removeEventListener('tick', list);
                return;
            }
            _this._alpha += step;
            rect.graphics.clear();
            _this.draw_rect();
        };

        rect.addEventListener('tick', list);
    }

    draw_rect(){
        const rect = this._rect;
        const g = rect.graphics;
        const length = this.length, depth = this.depth, w = this.width;

        const red = Math.min(2*depth+50, 160);
        const green = Math.min(depth*depth+50, 255);
        const blue = Math.min(14*depth+50, 125);
        const alpha = this._alpha;

        const color = 'rgba(' + red + ',' + green + ',' + blue +',' + alpha + ')';

        g.beginFill(color).drawRect(-w/2, 0, w/2, length);
    }

    create_rect(){
        const rect = new createjs.Shape();

        return rect;
    }

    create_text() {
        const text = new createjs.Text(''+this._depth, (2*w)+'px Courier', '#ff0');
        return text;
    }

    draw_text() {
        const length = this.length, depth = this.depth, w = this.width;
        const text = this._text;
        //const text = new createjs.Text(''+this._depth, (2*w)+'px Courier', '#ff0');
        text.rotation = 180;
        const b = text.getBounds();
        text.y = this._length/2;
        text.x = b.width/4;
        text.cache(0, 0, b.width, b.height+1);

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
}
