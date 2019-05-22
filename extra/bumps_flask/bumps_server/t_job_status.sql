DROP TABLE IF EXISTS t_job_status;

CREATE TABLE t_job_status (
	job_id INTEGER,
	status_date	DATETIME,
	job_status	TEXT,
	FOREIGN KEY (job_id) REFERENCES t_bumps_jobs (job_id) ON UPDATE CASCADE ON DELETE CASCADE
);
