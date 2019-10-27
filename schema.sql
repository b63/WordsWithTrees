create table branches (
  id integer primary key autoincrement,
  'text' text not null,
  depth integer not null,
  index integer not null,
  owner_id integer not null,
  price integer not null,
  color text not null,
  sell boolean NOT NULL CHECK (sell IN (0,1))
);