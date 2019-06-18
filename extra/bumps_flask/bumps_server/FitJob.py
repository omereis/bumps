from enum import Enum
from .bumps_constants import *
from .db_misc import get_next_job_id
from .message_parser import get_message_datetime_string
import datetime
import asyncio, sys
from bumps import cli
from shutil import rmtree
import os
from .oe_debug import print_debug, print_stack
#------------------------------------------------------------------------------
class JobStatus (Enum):
    NoData    = 10
    Parsed    = 20
    StandBy   = 30
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
            message_date_time = get_message_datetime_string (cm.message_time)
            if job_id:
                job_id = job_id + 1
                sql = 'insert into {} ({},{},{},{},{},{},{}) values ({},"{}","{}","{}","{}","{}","{}");'.format(\
                        DB_Table,
                        DB_Field_JobID, DB_Field_SentIP, DB_Field_SentTime, DB_Field_Tag, DB_Field_Message, DB_Field_ResultsDir,DB_Field_ProblemFile,
                        job_id, cm.host_ip, message_date_time, cm.tag, cm.message, cm.results_dir, cm.problem_file_name)
                res = connection.execute(sql)
                self.job_id = job_id
        except Exception as e:
            print ('bumps_ws_server, save_message_to_db, bug: {}'.format(e))
        return job_id
#------------------------------------------------------------------------------
    def prepare_params(self):
        self.params = []
        self.params.append('bumps')
        self.params.append(self.client_message.problem_file_name)
        self.params.append('--batch')
        for k in self.client_message.params.keys():
            if k == 'algorithm':
                self.params.append(f'--fit={self.client_message.params[k]}')
            elif k == 'burns':
                self.params.append(f'--burn={self.client_message.get_burn()}')
            elif k == 'steps':
                self.params.append(f'--steps={self.client_message.get_steps()}')
        self.params.append(f'--store={self.client_message.results_dir}')
#------------------------------------------------------------------------------
    def run_bumps_fit(self, db_connection):
        sys.argv = []
        sys.argv.append('bumps')
        for p in params:
            sys.argv.append(p)
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
    def set_completed(self, db_connection):
        self.status = JobStatus.Completed
        self.update_status_in_db(db_connection)
#------------------------------------------------------------------------------
    def update_status_in_db(self, connection):
        #j = JobStatus.status_by_name.StandBy
        #print (f'StandBy status: {j}')
        sqlInsert = f'insert into {DB_StatusTable} {DB_Field_JobID,DB_Field_StatusTime,DB_Field_StatusName}'.replace("'","")
        strSql = f'{sqlInsert} values {self.job_id, str(datetime.datetime.now()), name_of_status(self.status)};'
        #strSql = f'insert into {DB_StatusTable} {DB_Field_JobID,DB_Field_StatusTime,DB_Field_StatusName} values {self.job_id, str(datetime.datetime.now()), status_by_name(self.status)};'
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
        strSql = f'delete from {DB_Table} where {DB_Field_JobID}={self.job_id};'
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
#------------------------------------------------------------------------------
class ServerParams():
    queueJobEnded = None
    queueRunJobs = None
    listAllJobs = None
    db_connection = None
    database_engine = None
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
            #print_debug(f'append_job, process {os.getpid()}, appended job {fit_job.job_id}, list contains {self.jobs_count()} jobs')
        #server_params.listAllJobs.append(fit_job)
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
