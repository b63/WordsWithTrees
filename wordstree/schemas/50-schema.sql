drop table if exists users;

create table users (
  id integer primary key autoincrement,
  name text not null,
  username text not null,
  hash_password text not null,
  token integer default 100 check(token >= 0),
  unique(username)
);
