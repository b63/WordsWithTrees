drop table if exists tree;

create table tree (
    tree_id integer primary key autoincrement,
    tree_name text default 'default_tree',
    full_width integer not null,
    full_height integer not null
);

