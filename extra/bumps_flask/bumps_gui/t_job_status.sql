DROP TABLE IF EXISTS t_jobs_status;

CREATE TABLE t_jobs_status (
	job_id		INTEGER,
	status_time	DATETIME,
	status_name	TEXT,
	FOREIGN KEY (job_id) REFERENCES t_bumps_jobs (job_id) ON UPDATE CASCADE ON DELETE CASCADE
);
