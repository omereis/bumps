from enum import Enum
from bumps_constants import *
from db_misc import get_next_job_id
from message_parser import get_message_datetime_string
import datetime
#------------------------------------------------------------------------------
class JobStatus (Enum):
    NoData    = 1
    Parsed    = 2
    StandBy   = 3
    Running   = 4
    Completed = 5
    Error     = 6
    StatusErr = 7
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
        #print(f'prepare_params, client message params: {self.client_message.params}')
        #for k in self.client_message.params.keys():
            #print(f'Key: {k}')
#------------------------------------------------------------------------------
    def set_standby(self, connection):
        self.status = JobStatus.StandBy
        self.update_status_in_db(connection)
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
            print (f'FitJob.py, update_status_in_db: bug ; {e}')
