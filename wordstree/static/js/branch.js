class Tile extends createjs.Container {
    constructor(img, branches, tile_row, tile_col) {
        super();
        this.bitmap = this.create_bitmap(img);
        this.branches = branches;
        this.tile_row = tile_row;
        this.tile_col = tile_col;


        this.addChild(this.bitmap);
    }

    set_tile(img, branches, grid_x, grid_y) {
        if (img) {
            img.naturalWidth = img.width;
            img.naturalHeight = img.height;
        }
        this.bitmap.image = img;
        this.branches = branches;
        this.tile_row = grid_x;
        this.tile_col = grid_y;
    }

    create_bitmap(img){
        let bitmap = new createjs.Bitmap(img);
        if (img) {
            // Bitmap.isVisible checks for naturalWidth, returns false otherwise
            img.naturalWidth = img.width;
            img.naturalHeight = img.height;
        }
        return bitmap;
    }
}

