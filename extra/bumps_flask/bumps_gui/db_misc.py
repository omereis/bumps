try:
    from .bumps_constants import *
except:
    from bumps_constants import *
##------------------------------------------------------------------------------
def get_next_job_id(connection):
    job_id = 0
    try:
        sql = 'select max({}) from {};'.format(DB_Field_JobID, tbl_bumps_jobs)
        res = connection.execute(sql)
        for row in res:
            job_id = row.values()[0]
    except Exception as e:
        print("Error in get_next_job_id()")
        print("{}".format(e))
        job_id = None
    return job_id
#------------------------------------------------------------------------------
def results_dir_for_job (database_engine, job_id):
    try:
        connection = database_engine.connect()
        strSql = f'select {DB_Field_ResultsDir} from {tbl_bumps_jobs} where {DB_Field_JobID}={job_id};'
        res = connection.execute(strSql)
        for row in res:
            res_dir = f'{row[0]}'
    except Exception as e:
        print(f'Error {e}')
        res_dir = None
    finally:
        connection.close()
    return res_dir
#------------------------------------------------------------------------------
