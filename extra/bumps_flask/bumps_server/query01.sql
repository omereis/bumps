
SELECT * FROM t_bumps_jobs;
  
SELECT * FROM t_bumps_jobs ORDER BY job_id DESC;
SELECT MAX(job_id) FROM t_bumps_jobs;

DELETE FROM t_jobs_status WHERE job_id=282;

INSERT INTO t_jobs_status (job_id, status_time, status_name) VALUES (292, '2019-06-03 15:29:39.743360', 'StandBy');



SELECT * FROM t_jobs_status ORDER BY status_time DESC;
DELETE FROM t_bumps_jobs WHERE job_id=310;