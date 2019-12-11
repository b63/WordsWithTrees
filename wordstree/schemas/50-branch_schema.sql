drop table if exists branches;
drop table if exists branches_ownership;

create table branches (
    "id" integer primary key autoincrement,
    ind integer check (ind >= 0),
    "depth" integer not null,
    "length" real not null,
    "width" real not null,
    "angle" real not null,
    "pos_x" real not null,
    "pos_y" real not null,
    "tree_id" integer not null references tree(tree_id) on delete cascade,
    unique (ind, "tree_id")
);

create table branches_ownership (
    "id" integer primary key autoincrement,
    "branch_id" integer not null references branches("id") on delete cascade,
    "owner_id" integer default null references users("id") on delete set default,
    "text" text,
    "price" integer default 0,
    "available_for_purchase" boolean default 0 check ("available_for_purchase" in (0,1)),
    "available_for_bid" boolean default 0 check ("available_for_bid" in (0,1)),
    unique ("branch_id")
)

