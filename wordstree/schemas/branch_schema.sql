drop table if exists branches;

create table branches (
    "index" integer primary key check ("index" >= 0),
    "depth" integer not null,
    "length" real not null,
    "angle" real not null,
    "pos_x" real not null,
    "pos_y" real not null
);