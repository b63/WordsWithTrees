drop table if exists tiles;

create table tiles (
    "tile_id" integer primary key autoincrement,
    zoom integer not null,
    pos_x real not null,
    pos_y real not null,
    grid_width integer not null,
    grid_height integer not null,
    tree_id not null references tree(tree_id) on delete cascade,
    location text not null,
    image_size text,
)
