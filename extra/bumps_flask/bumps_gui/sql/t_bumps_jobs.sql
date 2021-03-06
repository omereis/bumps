CREATE TABLE t_bumps_jobs (
	job_id			INTEGER NOT NULL PRIMARY KEY,
	sent_ip			TEXT,
	sent_time		DATETIME,
	tag				TEXT,
	message			TEXT,
	fitter			TEXT,
	results_dir		TEXT,
	problem_file	TEXT,
	job_status		INTEGER,
	end_time		DATETIME,
	chi_square		DOUBLE,
	blob_message 	BLOB,
	json_results	TEXT,
	blob_refl1d_data BLOB
);

