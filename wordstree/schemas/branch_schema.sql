drop table if exists branches;

create table branches (
    "id" integer primary key autoincrement,
    "index" integer check ("index" >= 0),
    "depth" integer not null,
    "length" real not null,
    "width" real not null,
    "angle" real not null,
    "pos_x" real not null,
    "pos_y" real not null,
    "tree_id" integer not null references tree(tree_id) on delete cascade,
    unique ("index", "tree_id")
);