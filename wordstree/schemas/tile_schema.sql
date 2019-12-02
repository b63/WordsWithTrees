drop table if exists tiles;
drop table if exists zoom_info;

create table zoom_info (
    "zoom_id" integer primary key autoincrement,
    "zoom_level" integer not null,
    "tree_id" integer not null references tree(tree_id) on delete cascade,
    "grid" integer not null check (grid >= 0),
    "tile_width"  real not null check (tile_width >= 0),
    "tile_height" real not null check ( tile_height >= 0),
    "imgs_path" text not null,
    "jsons_path" text not null,
    unique (zoom_level, tree_id)
);

create table tiles (
    "tile_id" integer primary key autoincrement,
    tile_index integer not null check ( tile_index>=0 ),
    zoom_id integer not null references zoom_info(zoom_id) on delete cascade,
    img_file text not null,
    json_file text not null,
    tile_col integer not null,
    tile_row integer not null,
    tile_pos_x real not null,
    tile_pos_y real not null,
    unique (zoom_id, tile_index)
)

