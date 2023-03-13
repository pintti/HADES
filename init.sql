CREATE TABLE processors (id integer, area integer[4][50][50], spawn integer[3];
GRANT ALL PRIVILEGES ON DATABASE processors TO HADES_main;
CREATE TABLE drones (processor_id integer, drone_id integer, drone_loc integer[3], drone_goal integer[3]);
GRANT ALL PRIVILEGES ON DATABASE drones TO HADES_main;
