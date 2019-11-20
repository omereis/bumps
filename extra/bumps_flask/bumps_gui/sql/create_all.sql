CREATE DATABASE if not exists bumps_db;
/*---------------------------------------------------------------------------*/
CREATE USER 'bumps'@'%' IDENTIFIED BY 'bumps_dba';
GRANT ALL PRIVILEGES ON bumps_db.* TO 'bumps'@'%';
/*---------------------------------------------------------------------------*/
CREATE TABLE bumps_db.t_bumps_jobs (
  job_id INTEGER NOT NULL PRIMARY KEY,
  sent_ip TEXT,
  sent_time DATETIME,
  tag TEXT,
  message TEXT,
  fitter TEXT,
  results_dir TEXT,
  problem_file TEXT,
  job_status INTEGER,
  end_time DATETIME,
  chi_square DOUBLE,
  blob_message BLOB,
  json_results TEXT,
  blob_refl1d_data BLOB
);
/*---------------------------------------------------------------------------*/
CREATE TABLE bumps_db.t_jobs_status (
	job_id		INTEGER,
	status_time	DATETIME,
	status_name	TEXT,
	FOREIGN KEY (job_id) REFERENCES bumps_db.t_bumps_jobs (job_id) ON UPDATE CASCADE ON DELETE CASCADE
);
/*---------------------------------------------------------------------------*/
CREATE VIEW bumps_db.v_bumps_jobs_status (
	job_id,
	sent_ip,
	sent_time,
	message,
	results_dir,
	job_status,
	end_time,
	problem_file,
	status_time,
	status_name ,
	tag,
	chi_square
)
AS
	SELECT bumps_db.t_bumps_jobs.job_id AS 'job_id',sent_ip,sent_time,message,results_dir,job_status,end_time,problem_file,status_time,
			status_name,tag,chi_square
	FROM bumps_db.t_bumps_jobs,bumps_db.t_jobs_status WHERE bumps_db.t_bumps_jobs.job_id=bumps_db.t_jobs_status.job_id;
/*---------------------------------------------------------------------------*/
