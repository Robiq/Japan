drop table if exists users;
drop table if exists pairs;

create table users (
  id INTEGER primary key not null,
  name text UNIQUE not null,
  locLon real not null,
  locLat real not null,
  pair INTEGER,
  timeDc real
);

create table pairs (
  id INTEGER primary key,
  name1 text not null,
  name2 text not null
);