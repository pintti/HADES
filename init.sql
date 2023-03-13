CREATE USER HADES_main WITH PASSWORD 'notsecret';
CREATE DATABASE HADES_db WITH OWNER HADES_main;
\c HADES_db;
CREATE TABLE processors (id integer, area integer[4][50][50], spawn integer[3]);

CREATE TABLE drones (processor_id integer, drone_id integer, drone_loc integer[3], drone_goal integer[3]);

