DROP TABLE IF EXISTS t_bumps_users;
CREATE TABLE t_bumps_users (
	username VARCHAR(25) NOT NULL UNIQUE,
	PASSWORD VARCHAR(50)
);