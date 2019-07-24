
SELECT * FROM t_bumps_jobs;
SELECT * FROM t_jobs_status;
  
SELECT tag,COUNT(job_id) FROM t_bumps_jobs GROUP BY job_id;
SELECT tag,COUNT(job_id) AS 'tag_count' FROM t_bumps_jobs GROUP BY tag ORDER BY tag;

SELECT * FROM t_bumps_jobs;
DELETE FROM t_bumps_jobs;
