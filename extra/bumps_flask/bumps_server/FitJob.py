from enum import Enum
from bumps_constants import DB_Table, DB_Field_JobID, DB_Field_SentIP, DB_Field_SentTime, DB_Field_Tag, \
                            DB_Field_Message, DB_Field_ResultsDir,DB_Field_JobStatus, DB_Field_EndTime, \
                            DB_Field_ProblemFile
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
    message      = None
    message_time = None
    status       = MessageStatus.NoData
    FitType      = None
    arguments    = None
#------------------------------------------------------------------------------
    def __init__(self, parsed_message):
        self.message = parsed_message
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
        except Exception as e:
            print ('bumps_ws_server, save_message_to_db, bug: {}'.format(e))
        return job_id

