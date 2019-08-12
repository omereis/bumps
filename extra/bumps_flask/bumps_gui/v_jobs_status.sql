DROP VIEW IF EXISTS v_bumps_jobs_status;

CREATE VIEW v_bumps_jobs_status (
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
	tag
)
AS
	SELECT t_bumps_jobs.job_id AS 'job_id',sent_ip,sent_time,message,results_dir,job_status,end_time,problem_file,status_time,status_name,tag FROM t_bumps_jobs,t_jobs_status WHERE t_bumps_jobs.job_id=t_jobs_status.job_id
;

/*
SELECT t_bumps_jobs.job_id AS 'job_id',sent_ip,sent_time,message,results_dir,job_status,end_time,problem_file,status_time,status_name FROM t_bumps_jobs,t_jobs_status WHERE t_bumps_jobs.job_id=t_jobs_status.job_id;
*/