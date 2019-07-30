
SELECT * FROM t_bumps_jobs;
SELECT * FROM t_jobs_status;
  
SELECT tag,COUNT(job_id) FROM t_bumps_jobs GROUP BY job_id;
SELECT tag,COUNT(job_id) AS 'tag_count' FROM t_bumps_jobs GROUP BY tag ORDER BY tag;


DELETE FROM t_bumps_jobs;

SELECT * FROM t_jobs_status WHERE job_id = 44;

SELECT t_bumps_jobs.* FROM SELECT t_bumps_jobs INNER JOIN
	(SELECT job_id,MAX(status_time) AS 'status_time' FROM t_jobs_status GROUP BY job_id AS t);
	
SELECT job_id,status_time,status_name FROM t_jobs_status,
	(SELECT job_id,MAX(status_time) AS 'status_time' FROM t_jobs_status GROUP BY job_id AS t)
	WHERE 
	t_jobs_status.job_id=t.job_id AND t_jobs_status.status_time=t.status_time;

SELECT job_id,status_time,status_name FROM t_jobs_status,
	(SELECT job_id AS 'id',MAX(status_time) AS 'latest_status_time' FROM t_jobs_status GROUP BY id) AS t
	WHERE
		job_id = id
		AND
		status_time = latest_status_time
		AND
		job_id IN (SELECT job_id FROM t_bumps_jobs WHERE tag='stems');
SELECT job_id FROM t_bumps_jobs WHERE tag='stems';

SELECT DISTINCT tag FROM t_bumps_jobs;

SELECT job_id,status_time,status_name FROM t_jobs_status,
	(SELECT job_id AS "id",MAX(status_time) AS "latest_status_time" FROM t_jobs_status GROUP BY id) AS t
	WHERE (job_id = id) AND (status_time = latest_status_time)
	AND job_id IN (SELECT job_id FROM t_bumps_jobs WHERE tag='stems');