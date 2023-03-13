\connect HADES_db;
CREATE TABLE processors (id integer, area bytea, spawn bytea);
CREATE TABLE drones (processor_id integer, drone_id integer, drone_loc bytea, drone_goal bytea);
