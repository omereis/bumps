DROP TABLE IF EXISTS t_bumps_jobs;
CREATE TABLE t_bumps_jobs (
	token	VARCHAR(20) NOT NULL,
	job_id	INTEGER NOT NULL,
	params	VARCHAR(1024),
	PRIMARY KEY(token,job_id)
);
