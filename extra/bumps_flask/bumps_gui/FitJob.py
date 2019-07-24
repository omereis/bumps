from enum import Enum
import datetime
import asyncio, sys
from bumps import cli
from shutil import rmtree
import os
try:
    from .bumps_constants import *
    from .db_misc import get_next_job_id
    from .message_parser import get_message_datetime_string
    from .oe_debug import print_debug, print_stack
except:
    from bumps_constants import *
    from db_misc import get_next_job_id
    from message_parser import get_message_datetime_string
    from oe_debug import print_debug, print_stack
#------------------------------------------------------------------------------
class JobStatus (Enum):
    NoData    = 10
    Parsed    = 20
    StandBy   = 30
    Celery    = 35
    Running   = 40
    Completed = 50
    Error     = 60
    StatusErr = 70
#------------------------------------------------------------------------------
def name_of_status (status):
    strName= ''
    if status == JobStatus.NoData:
        strName= 'NoData'
    elif status == JobStatus.Parsed:
        strName= 'Parsed'
    elif status == JobStatus.StandBy:
        strName= 'StandBy'
    elif status == JobStatus.Running:
        strName= 'Running'
    elif status == JobStatus.Completed:
        strName= 'Completed'
    elif status == JobStatus.Error:
        strName= 'Error'
    else:
        strName= 'Unknown Status'
    return strName
#------------------------------------------------------------------------------
def status_by_name (strName):
    status = None
    if strName == 'NoData':
        status = JobStatus.NoData
    elif strName == 'Parsed':
        status = JobStatus.Parsed
    elif strName == 'StandBy':
        status = JobStatus.StandBy
    elif strName == 'Running':
        status = JobStatus.Running
    elif strName == 'Completed':
        status = JobStatus.Completed
    elif strName == 'Error':
        status = JobStatus.Error
    else:
        status = JobStatus.StatusErr
    return status
#------------------------------------------------------------------------------
def find_job_by_id (listJobs, job_id):
    iFound = -1
    n = 0
    while (n < len(listJobs)) & (iFound < 0):
        if listJobs[n].job_id == job_id:
            iFound = n
        n += 1
    return iFound
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class FitJob:
    client_message = None
    message_time   = None
    status         = JobStatus.NoData
    FitType        = None
    params         = None
    job_id         = None
#------------------------------------------------------------------------------
    def __init__(self, parsed_message):
        self.client_message = parsed_message
#------------------------------------------------------------------------------
    def save_message_to_db (self, cm, connection):
        try:
            job_id = get_next_job_id(connection)
            if job_id == None:
                job_id = 1
            message_date_time = get_message_datetime_string (cm.message_time)
            sql = 'insert into {} ({},{},{},{},{},{},{}) values ({},"{}","{}","{}","{}","{}","{}");'.format(\
                        tbl_bumps_jobs,
                        fld_JobID, fld_SentIP, fld_SentTime, fld_Tag, fld_Message, fld_ResultsDir,fld_ProblemFile,
                        job_id, cm.host_ip, message_date_time, cm.tag, cm.message, cm.results_dir, cm.problem_file_name)
            res = connection.execute(sql)
            self.job_id = job_id
        except Exception as e:
            print ('bumps_ws_server, save_message_to_db, bug: {}'.format(e))
        return job_id
#------------------------------------------------------------------------------
    def prepare_params(self):
        self.params = self.client_message.prepare_bumps_params()
        return self.params
#------------------------------------------------------------------------------
    def run_bumps_fit(self, db_connection):
        sys.argv = []
        sys.argv.append('bumps')
        #for p in params:
            #sys.argv.append(p)
        print(f'\n\nFitJob, run_bumps_fit\n{sys.argv}')
    #------------------------------------------------------------------------------
    def set_running(self, db_connection):
        try:
            self.status = JobStatus.Running
            self.update_status_in_db(db_connection)
        except Exception as e:
            print(f'Process {os.getpid()}, FitJob, "set_running", job #{self.job_id}, error {e}')
#------------------------------------------------------------------------------
    def set_standby(self, connection):
        self.status = JobStatus.StandBy
        self.update_status_in_db(connection)
#------------------------------------------------------------------------------
    def set_celery(db_connection):
        self.status = JobStatus.Celery
        self.update_status_in_db(connection)
#------------------------------------------------------------------------------
    def set_completed(self, db_connection):
        self.status = JobStatus.Completed
        self.update_status_in_db(db_connection)
#------------------------------------------------------------------------------
    def update_status_in_db(self, connection):
        sqlInsert = f'insert into {tbl_job_status} {fld_JobID,fld_StatusTime,fld_StatusName}'.replace("'","")
        #print_debug(f'"update_status_in_db", sqlInsert: "{sqlInsert}"')
        strSql = f'{sqlInsert} values {self.job_id, str(datetime.datetime.now()), name_of_status(self.status)};'
        #print(f'sqlInsert: "{sqlInsert}"')
        #print(f'strSql: "{strSql}"')
        #print_debug(f'"update_status_in_db", strSql: "{strSql}"')
        try:
            connection.execute(strSql)
        except Exception as e:
            print (f'FitJob.py, update_status_in_db: bug ; {e}\nSQL: "{strSql}"')
            print_stack ()
#------------------------------------------------------------------------------
    def get_tag(self):
        return self.client_message.tag
#------------------------------------------------------------------------------
    def delete_from_db(self, connection):
        strSql = f'delete from {tbl_bumps_jobs} where {fld_JobID}={self.job_id};'
        try:
            connection.execute(strSql)
        except Exception as e:
            print (f'FitJob.py, delete_from_db: bug : {e}')
#------------------------------------------------------------------------------
    def get_results_dir(self):
        return self.client_message.results_dir
#------------------------------------------------------------------------------
    def get_job_dir(self):
        return self.client_message.job_dir
#------------------------------------------------------------------------------
    def delete_job_directory(self):
        try:
            if os.path.isdir (self.get_job_dir()):
                rmtree (self.get_job_dir())
        except Exception as e:
            print (f'Could not delete directory: {e}')
#------------------------------------------------------------------------------
    def save_params(self):
        try:
            file_name = self.get_job_dir() + "/runjob.sh"
            file = open(file_name, "w+")
            params = ' '.join(self.params)
            file.write(params)
            file.flush()
        finally:
            file.close()
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class ServerParams():
    queueJobEnded   = None
    queueRunJobs    = None
    listAllJobs     = None
    db_connection   = None
    database_engine = None
    results_dir     = None
    flask_dir       = None
#------------------------------------------------------------------------------
    def __init__ (self, db_engine):
        self.database_engine = db_engine
#------------------------------------------------------------------------------
    def run_job (self, idx, db_connection):
        if (idx >= 0) & (idx < len(self.listAllJobs)):
            job = self.listAllJobs[idx]
            job.set_running(db_connection)
            self.listAllJobs[idx] = job
#------------------------------------------------------------------------------
    def get_connection(self):
        try:
            if self.database_engine:
                connection = self.database_engine.connect()
        except:
            connection = None
        finally:
            self.db_connection = connection
        return connection
#------------------------------------------------------------------------------
    def close_connection(self):
        try:
            if self.db_connection:
                self.db_connection.close()
                self.db_connection = None
        except Exception as e:
            print(f'\tFitJob, "close_connection", process {os.getpid()}, error\n{e}')
#------------------------------------------------------------------------------
    def jobs_count(self):
        return len(self.listAllJobs)
#------------------------------------------------------------------------------
    def append_job (self, fit_job):
        idx = find_job_by_id (self.listAllJobs, fit_job.job_id)
        if idx >= 0:
            self.listAllJobs[idx] = fit_job
        else:
            self.listAllJobs.append(fit_job)
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
