drop table if exists branches;
drop table if exists users;

create table branches (
  id integer primary key autoincrement,
  "text" text not null,
  "depth" integer not null,
  "index" integer not null,
  owner_id integer not null,
  price integer not null,
  color text not null,
  sell boolean NOT NULL CHECK (sell IN (0,1))
);

create table users (
  id integer primary key autoincrement,
  name text not null,
  username text not null,
  hash_password text not null,
  unique(username)
);