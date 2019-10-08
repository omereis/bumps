from enum import Enum
import asyncio, sys, multiprocessing, datetime, os, glob
from bumps import cli
from shutil import rmtree
try:
    from .bumps_constants import *
    from .db_misc import get_next_job_id, results_dir_for_job, get_problem_file_name
    from .message_parser import get_message_datetime_string
    from .oe_debug import print_debug, print_stack
except:
    from bumps_constants import *
    from db_misc import get_next_job_id, results_dir_for_job, get_problem_file_name
    from message_parser import get_message_datetime_string
    from oe_debug import print_debug, print_stack
#------------------------------------------------------------------------------
def get_job_index(listJobs, celery_fit_job):
    n=0
    nFound = -1
    while (n < len(listJobs)) and (nFound < 0):
        job = listJobs[n]
        if job.job_id == celery_fit_job.job_id:
            nFound = n
    return nFound
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
    elif status == JobStatus.Celery:
        strName= 'Celery'
    elif status == JobStatus.Celery:
        strName= 'Celery'
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
    chi_square     = None
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
            sql = f'insert into {tbl_bumps_jobs} ({fld_JobID}, {fld_SentIP}, {fld_SentTime}, {fld_Tag},{fld_Fitter},{fld_ResultsDir},{fld_ProblemFile}) \
                        values \
                        ({job_id}, "{cm.host_ip}", "{message_date_time}", "{cm.tag}","{cm.fitter}","{cm.results_dir}", "{cm.problem_file_name}");'
            res = connection.execute(sql)
            try:
                bmsg = str(cm.message).encode('utf-8').hex()
                sql = f'update {tbl_bumps_jobs} set {fld_blob_message}="{bmsg}" where {fld_JobID}={job_id};'
                res = connection.execute(sql)
            except Exception as e:
                print(f'blob error: {e}')
            self.job_id = job_id
        except Exception as e:
            print ('bumps_ws_server, save_message_to_db, bug: {}'.format(e))
        return job_id
#------------------------------------------------------------------------------
    def prepare_params(self):
        if self.client_message.is_bumps_fitter():
            self.params = self.client_message.prepare_bumps_params()
        elif self.client_message.is_refl1d_fitter():
            self.params = self.client_message.prepare_refl1d_params()
        return self.params
#------------------------------------------------------------------------------
    def run_bumps_fit(self, db_connection):
        sys.argv = []
        sys.argv.append('bumps')
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
    def set_celery(self, db_connection):
        self.status = JobStatus.Celery
        self.update_status_in_db(db_connection)
#------------------------------------------------------------------------------
    def set_completed(self, db_connection):
        self.status = JobStatus.Completed
        print(f'set_completed, fitter is {self.client_message.fitter}')
        if (self.client_message.fitter == 'refl1d'):
            base_name = get_refl1d_base_name_from_data(self.client_message.results_dir, self.client_message.problem_file_name)
            self.chi_square = read_chi_square(f'{base_name}.err')
            if os.path.exists(self.client_message.results_dir):
                json_name = glob.glob(f'{self.client_message.results_dir}{os.sep}*json')
                if (len(json_name)):
                    fjson = open(json_name[0], 'r')
                    strJson = fjson.read()
                    fjson.close()
                else:
                    strJson = None
            print(f'set_completed, results directory:\n{self.client_message.results_dir}\n')
        self.update_status_in_db(db_connection, save_chi=True, jsonResults=strJson)
#------------------------------------------------------------------------------
    def update_status_in_db(self, connection, save_chi = False, jsonResults=None):
        sqlInsert = f'insert into {tbl_job_status} {fld_JobID,fld_StatusTime,fld_StatusName}'.replace("'","")
        strSql = f'{sqlInsert} values {self.job_id, str(datetime.datetime.now()), name_of_status(self.status)};'
        try:
            connection.execute(strSql)
        except Exception as e:
            print (f'FitJob.py, update_status_in_db: bug ; {e}\nSQL: "{strSql}"')
        if (save_chi) and (self.chi_square != None):
            strSql = f'update {tbl_bumps_jobs} set {fld_chi_sqaue}={self.chi_square} where {fld_JobID}={self.job_id};'
            try:
                connection.execute(strSql)
            except Exception as e:
                print (f'FitJob.py, update_status_in_db: bug ; {e}\nSQL: "{strSql}"')
        if (jsonResults):
            jsonResults = jsonResults.replace('"','""')
            strSql = f'update {tbl_bumps_jobs} set {fld_json_results}="{jsonResults}" where  {fld_JobID}={self.job_id};'
            try:
                connection.execute(strSql)
            except Exception as e:
                print (f'FitJob.py, update_status_in_db: bug ; {e}\nSQL: "{strSql}"')
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
    def is_bumps(self):
        return self.client_message.is_bumps_fitter()
#------------------------------------------------------------------------------
    def is_refl1d(self):
        return self.client_message.is_refl1d_fitter()
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
    listCeleryJobs  = None

    db_connection   = None
    database_engine = None
    results_dir     = None
    flask_dir       = None

    celery_count = 0
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
    def append_celery_job (self, celery_fit_job):
        self.listCeleryJobs.append(celery_fit_job)
#------------------------------------------------------------------------------
    def get_celery_process(self, job_id):
        proc_found = None
        for process in self.listCeleryJobs:
            if hasattr(process, 'job_id'):
                if process.job_id == job_id:
                    proc_found = process
            if proc_found:
                break
        return proc_found

#------------------------------------------------------------------------------
    def kill_celery_process(self, job_id):
        return 17
        celery_process = self.get_celery_process(job_id)
        if celery_process:
            try:
                celery_process.join()
                celery_process.kill()
                self.listCeleryJobs.remove(celery_process)
            except Exception as e:
                print(f'kill_celery_process runtime error: {e}')
#------------------------------------------------------------------------------
    def delete_celery_job (self, celery_fit_job):
        idx = get_job_index(self.listCeleryJobs, celery_fit_job)
        if idx >= 0:
            del self.listCeleryJobs[idx]
#------------------------------------------------------------------------------
    def print_celery_jobs(self,title=None):
        if title:
            print(f'-----{title}-----')
        else:
            print('------------------------')
        for process in self.listCeleryJobs:
            if not hasattr (process, 'job_id'):
                process.job_id = '-1'
            print(f'process {process.pid} has job id of {process.job_id}')
        print('------------------------')
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def read_chi_square(err_name):
    try:
        chi_square = 'undefined'
        f = open (err_name, 'r')
        err_data = f.read()
        f.close()
        strChi = 'chisq='
        iChi = err_data.index(strChi)
        iNLLF = err_data.index(', nllf')
        if (iChi > 0) and (iNLLF > 0):
            strTmp = err_data[iChi + len(strChi) : iNLLF]
            iPar = strTmp.index('(')
            if iPar > 0:
                chi_square = strTmp[0:iPar]
            else:
                chi_square = strTmp
    except Exception as e:
        print(f'read_chi_square runtime error: {e}')
        chi_square = f'{e}'
    return chi_square
#------------------------------------------------------------------------------
def get_refl1d_base_name_from_data(results_dir, file_path):
    try:
        f_split = file_path.split(os.sep)
        fname = f_split[len(f_split) - 1]
        if fname.index('.') > 0:
            fname = fname.split('.')[0]
        if results_dir[len(results_dir) - 1] != os.sep:
            results_dir += os.sep
        base_name = results_dir + fname
    except:
        print(f'get_refl1d_base_name runtime error: {e}')
        base_name = None
    return base_name
#------------------------------------------------------------------------------
def get_refl1d_base_name(cm, server_params):
    try:
        results_dir = results_dir_for_job (server_params.database_engine, cm.params)
        file_path = get_problem_file_name (server_params.database_engine, cm.params)
        base_name = get_refl1d_base_name_from_data(results_dir, file_path)
    except Exception as e:
        print(f'get_refl1d_base_name runtime error: {e}')
        base_name = None
    return base_name
#------------------------------------------------------------------------------
