try:
    from .bumps_constants import *
except:
    from bumps_constants import *
##------------------------------------------------------------------------------
def get_next_job_id(connection):
    job_id = 0
    try:
        sql = 'select max({}) from {};'.format(fld_JobID, tbl_bumps_jobs)
        res = connection.execute(sql)
        for row in res:
            db_job_id = row.values()[0]
        if db_job_id:
            job_id = db_job_id
    except Exception as e:
        print(f"Error in get_next_job_id: {e}")
        job_id = 0
    job_id += 1
    return job_id
#------------------------------------------------------------------------------
def results_dir_for_job (database_engine, job_id):
    try:
        connection = database_engine.connect()
        strSql = f'select {fld_ResultsDir} from {tbl_bumps_jobs} where {fld_JobID}={job_id};'
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
def get_problem_file_name (database_engine, job_id):
    try:
        connection = database_engine.connect()
        strSql = f'select {fld_ProblemFile} from {tbl_bumps_jobs} where {fld_JobID}={job_id};'
        res = connection.execute(strSql)
        for row in res:
            fname = f'{row[0]}'
    except Exception as e:
        print(f'Error {e}')
        fname = None
    finally:
        connection.close()
    return fname
#------------------------------------------------------------------------------
def get_env_value(key, default_value):
    v = os.getenv(key)
    if v == None:
        v = default_value
    return v
#------------------------------------------------------------------------------
from sqlalchemy import create_engine, MetaData
#------------------------------------------------------------------------------
def read_file(file_name):
    f = open(file_name, 'r')
    content = f.read()
    f.close()
    return content
#------------------------------------------------------------------------------
def run_sql_file(sql_filename):
    try:
        if os.path.isdir('sql'):
            sql = read_file('sql/create_user.sql')
            print(f'SQL: {sql}')
            connection.execute(sql)
            exec = True
        else:
            exec = False
    except:
        exec = False
    return exec
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
