drop table if exists tree;

create table tree (
    tree_id integer primary key autoincrement,
    num_branches integer not null default 0,
    full_width integer not null,
    full_height integer not null
);

-- dummy tree
insert into tree (num_branches, full_width, full_height) values (1, 100, 100);
