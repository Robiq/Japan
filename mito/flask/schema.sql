drop table if exists users;
drop table if exists loc;
drop table if exists pair;

create table users (
  id integer autoincrement,
  name text primary key,
  pair int
);

create table loc (
  id integer primary key,
  locLon real not null,
  locLat real not null
);

create table pair (
  id integer primary key,
  name1 text not null,
  name2 text not null
);