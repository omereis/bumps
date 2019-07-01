CREATE TABLE t_bumps_jobs (
	job_id		INTEGER NOT NULL PRIMARY KEY,
	sent_ip		TEXT,
	sent_time	DATETIME,
	tag			TEXT,
	message		TEXT,
	results_dir	TEXT,
	problem_file	TEXT,
	job_status	INTEGER,
	end_time	DATETIME
);
	