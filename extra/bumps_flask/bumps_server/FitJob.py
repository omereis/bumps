from enum import Enum
from bumps_constants import *
from db_misc import get_next_job_id
from message_parser import get_message_datetime_string
#------------------------------------------------------------------------------
class MessageStatus (Enum):
    NoData    = 1
    Parsed    = 2
    StandBy   = 3
    Running   = 4
    Completed = 5
    Error     = 6
#------------------------------------------------------------------------------
class FitJob:
    client_message = None
    message_time   = None
    status         = MessageStatus.NoData
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
    def set_standby(self):
        self.status = MessageStatus.StandBy

