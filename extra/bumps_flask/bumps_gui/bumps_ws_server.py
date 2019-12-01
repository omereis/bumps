import asyncio, websockets, getopt, sys, datetime, time
import mysql.connector, json, os, multiprocessing
import nest_asyncio, functools, shutil, glob
from pathlib import Path
from sqlalchemy import create_engine, MetaData
import bumps
from refl1d.main import cli as refl1d_cli

from oe_debug import print_debug
from bumps_constants import *
from misc import get_results_dir, get_web_results_dir, zip_directory
from FitJob import FitJob, JobStatus, name_of_status, ServerParams, find_job_by_id, get_refl1d_base_name, read_chi_square
from db_misc import results_dir_for_job, get_problem_file_name
from message_parser import ClientMessage, MessageCommand, generate_key
from get_host_port import get_host_port
from MessageCommand import MessageCommand
#------------------------------------------------------------------------------
database_engine = None
connection = None
nest_asyncio.apply()

#------------------------------------------------------------------------------
def save_message (message):
    file = open ("messages.txt", "a+")
    file.write (message + "\n")
    file.close()
#------------------------------------------------------------------------------
def check_header(json_message):
    err = ''
    try:
        header = json_message['header']
        if header != 'bumps client':
            err = 'E_INVALID_HEADER'
        else:
            err = ''
    except Exception as e:
            err = 'E_INVALID_HEADER'
    return err, header 
#------------------------------------------------------------------------------
def is_valid_message(message):
    json_message = json.loads(message)
    header,err = check_header(json_message)
    if len(err) > 0:
        return err
    return ''
#------------------------------------------------------------------------------
def count_running_jobs (listJobs):
    n_running_jobs = 0
    for job in listJobs:
        if job.status == JobStatus.Running:
            n_running_jobs += 1
    return n_running_jobs
#------------------------------------------------------------------------------
def print_jobs(listJobs, title=''):
    try: 
        print(f'{title}: Current Jobs')
        print('-----------------------')
        for n in range(len(listJobs)):
            print (f'job {n}, job_id: {listJobs[n].job_id}, status: {name_of_status(listJobs[n].status)}')
        print('-----------------------')
    except Exception as e:
        print(f'Error in print_job: "{e}"')
#------------------------------------------------------------------------------
def scan_jobs_list (server_params):
    try:
        n_cpus = multiprocessing.cpu_count()
        for n in range(len(server_params.listAllJobs)):
            n_running_jobs = count_running_jobs(server_params.listAllJobs)
            fit_job = server_params.listAllJobs[n]
            if fit_job.status == JobStatus.Parsed:
                fit_job.set_standby(server_params.db_connection)
            elif fit_job.status == JobStatus.StandBy:
                if n_running_jobs < n_cpus:
                    fit_job.prepare_params()
                    fit_job.set_running(server_params.get_connection())
                    server_params.listAllJobs[n] = fit_job
                    server_params.queueRunJobs.put(fit_job)
    except Exception as e:
        print(f'"scan_jobs_list" runtime error: {e}')
#------------------------------------------------------------------------------
#-------- Process: Job Queue Manager ------------------------------------------
def run_fit_job (fit_job, server_params):
    try:
        sys.argv = fit_job.params
        try:
            if fit_job.is_bumps():
                bumps.cli.main()
            elif fit_job.is_refl1d():
                refl1d_cli()
        finally:
            server_params.queueJobEnded.put(fit_job)
    except Exception as e:
        print (f'Error in run_fit_job: {e}')
#------------------------------------------------------------------------------
async def job_runner(server_params):
    while True:
        fit_job = server_params.queueRunJobs.get()
        try:
            run_fit_job (fit_job, server_params)
        except Exception as e:
            print(f'Error in job_runner: {e}')
#------------------------------------------------------------------------------
def jobs_runner_process(server_params):
    asyncio.run(job_runner(server_params))
#------------------------------------------------------------------------------
def get_job_dir_zip_name(results_dir):
    job_dir = os.path.abspath(os.path.join(results_dir, '..'))
    if job_dir[len(job_dir) - 1] == os.path.sep:
        job_dir = job_dir[0:len(job_dir) - 1]
    parts = job_dir.split(os.path.sep)
    zip_name = f'{parts[len(parts) - 1]}.zip'
    return job_dir, zip_name
#------------------------------------------------------------------------------
def get_job_full_zip_name(results_dir):
    job_dir, zip_name = get_job_dir_zip_name(results_dir)
    if not job_dir.endswith('/'):
        job_dir += '/'
    if not zip_name.lower().endswith('.zip'):
        zip_name += '.zip'
    return f'{job_dir}{zip_name}'
#------------------------------------------------------------------------------
def zip_job_results(job):
    job_dir, zip_name = get_job_dir_zip_name(job.client_message.results_dir)
    cur_dir = os.getcwd()
    if job_dir.find(cur_dir) == 0:
        zip_dir = '.' + job_dir[len(cur_dir):len(job_dir)]
    else:
        zip_dir = job_dir
    zip_directory (zip_name, zip_dir)
#------------------------------------------------------------------------------
async def job_finalizer(server_params):
    while True:
        fit_job = server_params.queueJobEnded.get()
        print(f'"job_finalizer", process {os.getpid()}, fit job {fit_job.job_id} ended, not completed')
        fit_job.save_params()
        sys.stdout.flush()
        if fit_job.status == JobStatus.Running:
            try:
                idx = find_job_by_id(server_params.listAllJobs, fit_job.job_id)
                if idx >= 0:
                    job = server_params.listAllJobs[idx]
                    job.set_completed(server_params.get_connection())
                    zip_job_results(job)
                    server_params.listAllJobs[idx] = job
                else:
                    print(f'job_finalizer, process {os.getpid()}, job {fit_job.job_id} not on list')
                scan_jobs_list (server_params)
            except Exception as e:
                print(f'"job_finalizer", process {os.getpid()}, error"{e}"')
            finally:
                server_params.close_connection()
                #db_connection.close()
#------------------------------------------------------------------------------
def job_ending_manager(server_params):
    asyncio.run(job_finalizer(server_params))
#------------------------------------------------------------------------------
def print_celery_jobs(server_params):
    for process in server_params.listCeleryJobs:
        print(f'{datetime.datetime.now()}: process {process.pid} job id {process.job_id}')
    time.sleep(20)
#------------------------------------------------------------------------------
from bumps_celery import tasks as celery_tasks
import zipfile
#------------------------------------------------------------------------------
def send_celery_fit (fit_job, server_params, message):
    try:
        tStart = datetime.datetime.now()
        res = celery_tasks.run_celery_fit.delay (message)
        dt = datetime.datetime.now() - tStart
        while (res.ready() == False) and (dt.seconds < 5 * 60):
            time.sleep(0.1)
            dt = datetime.datetime.now() - tStart
        if res.ready():
            fit = str(res.get())
        else:
            fit = 'no results. timeout'
        if fit:
            bin_content = bytes().fromhex(fit)
            zip_name = get_job_full_zip_name (fit_job.client_message.results_dir)
            f = open(zip_name,'wb')
            f.write(bin_content)
            f.close()
            with zipfile.ZipFile(zip_name, 'r') as zip_ref:
                zip_ref.extractall(fit_job.client_message.job_dir)
            db_connection = server_params.database_engine.connect()
            fit_job.set_completed(db_connection)
            db_connection.close()
            server_params.print_celery_jobs('send_celery_fit')
    except Exception as e:
        print(f'{__file__},send_celery_fit runtime error: {e}')
#------------------------------------------------------------------------------
def HandleFitMessage (cm, server_params, message):
    cm.create_results_dir(server_params)
    fit_job = FitJob (cm)
    try:
        db_connection = server_params.database_engine.connect()
        job_id = fit_job.save_message_to_db (cm, db_connection)
        if cm.multi_proc == 'celery':
            fit_job.set_celery(db_connection)
            pCelery = multiprocessing.Process(name='celery fit', target=send_celery_fit, args=(fit_job, server_params, message,))
            pCelery.start()
            pCelery.job_id = fit_job.job_id
            server_params.append_celery_job(pCelery)
        else:
            cm.save_problem_file()
            fit_job.set_standby(db_connection)
            server_params.append_job (fit_job)
            scan_jobs_list (server_params)
    except Exception as e:
        print (f'bumps_ws_server.py, HandleFitMessage, bug: {e}')
        job_id = 0
    finally:
        db_connection.close()
    return job_id
#------------------------------------------------------------------------------
def get_orred_ids (params, field=None, add_quotes=False):
    astrWhere = []
    if field == None:
        field = fld_JobID
    for id in params:
        if add_quotes == True:
            value = f'"{str(id)}"'
        else:
            value = str(id)
        astrWhere.append (f'({field}={value})')
    if len(astrWhere) > 1:
        strWhere = ' or '.join(astrWhere)
    else:
        strWhere = astrWhere[0]
    return strWhere
#------------------------------------------------------------------------------
def remove_from_list_by_id (listJobs, strlstIDs, db_connection):
    n = 0
    try:
        while n < len(listJobs):
            if str(listJobs[n].job_id) in strlstIDs:
                job = listJobs.pop(n)
                job.delete_from_db(db_connection)
                job.delete_job_directory()
            else:
                n += 1
    except Exception as e:
        print ('bumps_ws_server.py, remove_from_list_by_id, bug: {}'.format(e))
#------------------------------------------------------------------------------
def HandleDelete (cm, server_params):
    return_params = cm.params
    db_connection = None
    try:
        db_connection = server_params.database_engine.connect()
        IDs = get_orred_ids (cm.params)
        sql = f'select results_dir from t_bumps_jobs where {IDs};'
        res = db_connection.execute(sql)
        for row in res:
            if os.path.exists(row[0]):
                shutil.rmtree(row[0])
        sql = f'delete from t_bumps_jobs where {IDs};'
        db_connection.execute(sql)
    except Exception as e:
        print ('bumps_ws_server.py, HandleDelete, bug: {}'.format(e))
    finally:
        if db_connection:
            db_connection.close()
    return return_params
#------------------------------------------------------------------------------
def remove_double_blanks(s):
    pos = s.find('  ')
    while pos >= 0:
        s = s.replace('  ',' ')
        pos = s.find('  ')
    return s
#------------------------------------------------------------------------------
async def HandleStatus (cm, server_params):
    return_params = []
    try:
        db_connection = server_params.database_engine.connect()
        sqlSelect = f'SELECT job_id,status_time,status_name'
        if cm.params:
            sqlFrom = f'from {tbl_job_status} where {fld_JobID}={cm.params}'
        else:
            sqlFrom = f'FROM t_jobs_status, \
	        (SELECT job_id AS "id",MAX(status_time) AS "latest_status_time" FROM t_jobs_status GROUP BY id) AS t \
	        WHERE (job_id = id) AND (status_time = latest_status_time) \
	        AND job_id IN (SELECT job_id FROM {tbl_bumps_jobs} WHERE tag="{cm.tag}")'
        sql = f'{sqlSelect} {sqlFrom};'
        sql = remove_double_blanks (sql)
        res = db_connection.execute(sql)
        for row in res:
            item = {'job_id': row[0], 'job_status': row[2], 'job_time' : str(row[1])}
            return_params.append(item)
        if len(return_params) == 0:
            return_params.append('unknown')
    except Exception as e:
        print (f'bumps_ws_server.py, get_db_jobs_status, runteime error: {e}\nSQL:\n{sql}')
    finally:
        if db_connection:
            db_connection.close()
    return return_params
#------------------------------------------------------------------------------
def get_results (cm, server_params):
    try:
        results_dir = results_dir_for_job (server_params.database_engine, cm.params)
        flask_dir = server_params.flask_dir
        final_dir = results_dir[len(flask_dir) - 1 : ]
        files_list = os.listdir(results_dir)
        files = []
        for file in files_list:
            file = final_dir + '/' + file
            files.append(file)
    except Exception as e:
        print(f'Error in "get_results": {e}')
        files = {e}
    return_params = {'id': cm.params, 'files' : files}
    return return_params
#------------------------------------------------------------------------------
def read_json_data(json_name):
    try:
        f = open(json_name, 'r')
        file_data = f.read()
        f.close()
        json_data = file_data.encode('utf-8').hex()
    except Exception as e:
        print(f'json reading runtime error: {e}')
        json_data = f'{e}'
    return json_data
#------------------------------------------------------------------------------
def get_refl1d_results(cm, server_params):
    try:
        base_name = get_refl1d_base_name(cm, server_params)
        json_name = base_name + '-expt.json'
        return_params = {}
        problem_name = get_problem_name_from_blob_field(cm.params, server_params)
        return_params['json_data'] = read_json_data(json_name)
        chi_square = read_chi_square(f'{base_name}.err')
        print(f'chi square: {chi_square}')
        return_params['chi_square'] = chi_square
        return_params['job_id'] = cm.params # feedback
        return_params['problem_name'] = problem_name
    except Exception as e:
        print(f'get_refl1d_results runtime error: {e}')
        return_params = {'results_directory' : f'Runtime error" {e}'}
    return (return_params) 
#------------------------------------------------------------------------------
def get_comm_status(cm, server_params):
    try:
        return_params = cm.params
    except Exception as e:
        print(f'get_comm_status runtime error: {e}')
        return_params = {'error' : f'{e}'}
    return (return_params) 
#------------------------------------------------------------------------------
def get_tag_count(cm, server_params):
    return_params = []
    try:
        db_connection = server_params.database_engine.connect()
        sql = f'select {fld_Tag},COUNT({fld_JobID}) FROM {tbl_bumps_jobs} WHERE ({fld_Fitter}="refl1d")'
        if (cm.params != None) and (len(cm.params) > 0):
            tags = cm.params.split(',')
            astr = get_orred_ids(tags, field=fld_Tag, add_quotes=True)
            sql += f' AND ({astr})'
        sql += f' group by {fld_Tag};'
        res = db_connection.execute(sql)
        if res.rowcount > 0:
            for row in res:
                item = {'job_id' : row[0], 'count':row[1]}
                return_params.append(item)
        else:
            return_params.append({'job_id' : '', 'count':''})
    except Exception as e:
        sErr = f'bumps_ws_server.py, get_tag_count, runteime error: {e}'
        print (sErr)
        return_params = sErr
    finally:
        if db_connection:
            db_connection.close()
    return return_params
#------------------------------------------------------------------------------
def get_all_tag_count(cm, server_params):
    try:
        return_params = get_tag_count(cm, server_params)
    except Exception as e:
        sErr = f'bumps_ws_server.py, get_tag_count, runteime error: {e}'
        print (sErr)
        return_params = sErr
    return return_params
#------------------------------------------------------------------------------
def delete_by_tag(cm, server_params):
    return_params = []
    try:
        if cm.params:
            db_connection = server_params.database_engine.connect()
            tags = cm.params.split(',')
            astr = get_orred_ids(tags, field=fld_Tag, add_quotes=True)
            sql = f'delete from {tbl_bumps_jobs} WHERE {astr};'
            res = db_connection.execute(sql)
            return_params = tags
    except Exception as e:
        strErr = f'{e}'
        print(f'\ndelete_by_tag Error:\n{strErr}\n')
        s1 = strErr.replace("'",'"')
        print(f'\nError:\n{s1}\n')
        sErr = f'bumps_ws_server.py, delete_by_tag, runteime error: {e}'
        print (sErr)
        return_params = sErr
    finally:
        if db_connection:
            db_connection.close()
    return return_params
#------------------------------------------------------------------------------
def is_broken_pipe_err(e):
    strErr = f'{e}'
    return (strErr.find('32') > 0) and (strErr.find('BrokenPipeError') > 0)
#------------------------------------------------------------------------------
load_job_by_tag_counter = 0;
#------------------------------------------------------------------------------
def load_jobs_by_tags(cm, server_params):
    global load_job_by_tag_counter
    return_params = []
    try:
        if cm.params:
            if 'load_job_by_tag_counter' in locals():
                load_job_by_tag_counter += 1
            else:
                load_job_by_tag_counter = 1
            db_connection = server_params.database_engine.connect()
            tags = cm.params.split(',')
            astr = get_orred_ids(tags, field=fld_Tag, add_quotes=True)
            sql = f'select {fld_JobID}, {fld_Tag}, {fld_SentTime}, {fld_chi_sqaue}, {fld_ProblemFile} FROM {tbl_bumps_jobs} WHERE {astr} order by {fld_Tag};'
            res = db_connection.execute(sql)
            for row in res:
                d = row[2]
                strDate = f'{d.month}/{d.day}, {d.year}'
                strMin = str(d.minute).rjust(2,'0')
                strTime = f'{d.hour}:{strMin}'#{d.minute}
                if row[3] == None:
                    chi = 'none'
                else:
                    chi = row[3]
                fname = get_problem_name (row[4])
                item = {'job_id' : row[0], 'tag':row[1], 'sent_date' : strDate, 'sent_time' : strTime, 'chi_square' : chi, 'problem_name' : fname}
                return_params.append(item)
    except Exception as e:
        if (is_broken_pipe_err(e) and (load_job_by_tag_counter < 5)):
            load_job_by_tag_counter += 1
            time.sleep(0.1)
            return load_jobs_by_tags(cm, server_params)
        else:
            sErr = f'bumps_ws_server.py, load_jobs_by_tags, runteime error: {e}'
            print (sErr)
            return_params = sErr
    finally:
        if db_connection:
            db_connection.close()
    return return_params
#------------------------------------------------------------------------------
def chi_from_db(db_value):
    if db_value == None:
        chi = 'none'
    else:
        chi = db_value
    return chi
#------------------------------------------------------------------------------
def zip_file_from_results_dir(results_dir):
    zip_path = glob.glob(results_dir + os.sep + '*.zip')[0]
    return zip_path
#------------------------------------------------------------------------------
def get_refl1d_zip_name(zip_path):
    aZip = zip_path.split(os.sep)
    zip_name = aZip[len(aZip) - 1]
    return zip_name
#------------------------------------------------------------------------------
def get_refl1d_table_data(zip_path):
    head,tail = os.path.split(zip_path)
    json_name = head + os.sep + tail.split('.')[0] + '-expt.json'
    sld_table = read_json_data(json_name)
    return sld_table
#------------------------------------------------------------------------------
def read_zip_data(zip_path):
    zip_file = zipfile.ZipFile(zip_path)
    zip_names = zip_file.namelist()
    data_name = None
    data = ''
    for n in range(len(zip_names)):
        if zip_names[n].endswith('refl'):
            data_name = zip_names[n];
    if data_name:
        f = zip_file.open(data_name)
        data = f.read()
        f.close()
    return data.decode('utf8')
#------------------------------------------------------------------------------
def get_problem_name (db_name):
    basename = os.path.basename(db_name)
    name = basename.replace('.zip', '.refl')
    return name
#------------------------------------------------------------------------------
def json_from_blob(blob):
    try:
        msg_data = bytes.fromhex(blob.decode('utf-8')).decode('utf-8')
        jmsg = json.loads(msg_data.replace('"','\\\"').replace("'",'"'))
    except Exception as e:
        print(f'get_refl1d_results runtime error: {e}')
        jmsg = {}
    return jmsg
#------------------------------------------------------------------------------
def get_problem_name_from_blob_field(job_id, server_params):
    db_connection = None
    try:
        db_connection = server_params.database_engine.connect()
        sql = f'select {fld_blob_message} from {tbl_bumps_jobs} where {fld_JobID}="{job_id}";'
        res = db_connection.execute(sql)
        bufs = res.fetchone()
        buf = bufs[0]
        jmsg = json_from_blob(buf)
        problem_name = jmsg['problem_name']
    except Exception as e:
        print(f'get_refl1d_results runtime error: {e}')
        problem_name = ''
    finally:
        if db_connection:
            db_connection.close()
    return (problem_name) 
#------------------------------------------------------------------------------
def load_jobs_by_id(cm, server_params):
    return_params = []
    try:
        if cm.params:
            db_connection = server_params.database_engine.connect()
            id = cm.params
            sql = f'select {fld_Tag},{fld_chi_sqaue},{fld_ResultsDir},{fld_ProblemFile},{fld_blob_message} FROM {tbl_bumps_jobs} WHERE {fld_JobID}={id};'
            res = db_connection.execute(sql)
            res_buffer = res.fetchone()
            base_name = get_refl1d_base_name(cm, server_params)
            results_dir = str(Path(base_name).parent)
            if os.path.exists(results_dir):
                zip_path = zip_file_from_results_dir(res_buffer[2])
                zip_name = get_refl1d_zip_name(zip_path)
                zip_data = read_zip_data(zip_path)
                refl1d_table = get_refl1d_table_data(zip_path)
                jsonMsg = json_from_blob(res_buffer[4])
                problem_name = jsonMsg['problem_name']
                item = {'job_id' : id, 'tag' : res_buffer[0], 'zip_name' : zip_name, 'chi_square' : chi_from_db(res_buffer[1]), 'data' : zip_data, 'fit_table': refl1d_table, 'problem_name' : problem_name}
            else:
                get_problem_name_from_blob_field(cm.params, server_params);
                item = {'job_id' : id, 'error' : 'missing files'}
            return_params.append(item)
    except Exception as e:
        sErr = f'bumps_ws_server.py, load_jobs_by_id, runteime error: {e}'
        sErr = sErr.replace("'", '"');
        print (sErr)
        return_params = sErr
    finally:
        if db_connection:
            db_connection.close()
    return return_params
#------------------------------------------------------------------------------
def get_tag_jobs(cm, server_params):
    return_params = []
    try:
        if cm.params:
            db_connection = server_params.database_engine.connect()
            tags = cm.params.split(',')
            astr = []
            for n in range(len(tags)):
                s = f'{fld_Tag}="{tags[n]}"'
                astr.append(s)
            if len(astr) > 1:
                where_tags = ' or '.join(astr)
            else:
                where_tags = ' or '.join(astr)
            sql = f'SELECT {fld_JobID},{fld_SentTime},{fld_Tag},{fld_ResultsDir},{fld_chi_sqaue} FROM {tbl_bumps_jobs} WHERE {where_tags};'
            res = db_connection.execute(sql)
            for row in res:
                results_dir = row[3]
                fname = glob.glob(f'{results_dir}/*.zip')
                if len(fname) > 0:
                    ar = fname.split('/')
                    fname = ar[len(ar) - 1]
                    fname = fname.replace('zip','refl')
                item = {'job_id': row[0], 'sent_time': row[1], 'tag' : row[2], 'file_name': fname, 'chi_square' : row[4]}
                return_params.append(item)
    except Exception as e:
        sErr = f'bumps_ws_server.py, get_db_jobs_status, runteime error: {e}'
        print (sErr)
        return_params = sErr
    finally:
        if db_connection:
            db_connection.close()
    return return_params
#------------------------------------------------------------------------------
def get_db_status (cm, server_params):
    params = []
    fmt = '%d %m %Y %H %M %S %f'
    params.append({'datetime format': fmt})
    if cm.tag:
        sqlIn = f'select distinct {fld_JobID} from {tbl_bumps_jobs} where {fld_Tag}="{cm.tag}" order by {fld_JobID}'
        sqlSelect = f'select {fld_JobID},{fld_StatusTime},{fld_StatusName} from {tbl_job_status} where {fld_JobID} in ({sqlIn});'
        db_connection = server_params.database_engine.connect()
        results = db_connection.execute(sqlSelect)
        for row in results:
            item = {'job_id': str(row[0]), 'status time': row[1].strftime(fmt), 'status': row[2]}
            params.append(item)
    return params
#------------------------------------------------------------------------------
def get_job_data (cm, server_params):
    params = []
    if cm.tag:
        db_connection = server_params.database_engine.connect()
        sql = f'select {fld_JobID},{fld_ResultsDir} from {tbl_bumps_jobs} where {fld_Tag} = "{cm.tag}";'
        results = db_connection.execute(sql)
        for row in results:
            job_dir, zip_name = get_job_dir_zip_name(row[1])
            zip_name = f'{job_dir}{os.path.sep}{zip_name}'
            f = open (zip_name, 'rb')
            bin_content = f.read()
            f.close()
            string_content = bin_content.hex()
            item = {str(row[0]) : string_content}
            params.append(item)
    return params
#------------------------------------------------------------------------------
def get_db_tags (cm, server_params):
    params = []
    try:
        db_connection = server_params.database_engine.connect()
        sql = f'select distinct {fld_Tag} from {tbl_bumps_jobs} order by {fld_Tag};'
        results = db_connection.execute(sql)
        for row in results:
            params.append(row[0])
    except Exception as e:
        print('"get_db_tags" runtime error: {e}')
        params = [e]
    return params
#------------------------------------------------------------------------------
def handle_incoming_message (websocket, message, server_params):
    return_params = {}
    cm = ClientMessage()
    try:
        if cm.parse_message(websocket.remote_address[0], message, server_params.results_dir):
            if cm.command == MessageCommand.StartFit:
                job_id = HandleFitMessage (cm, server_params, message)
                if job_id:
                    return_params[str(cm.local_id)] = job_id
            elif cm.command == MessageCommand.Delete:
                return_params = HandleDelete (cm, server_params)
            elif cm.command == MessageCommand.Status:
                return_params = asyncio.run(HandleStatus (cm, server_params))
            elif  cm.command == MessageCommand.PrintStatus:
                print_jobs(server_params.listAllJobs, title='current_status')
                print_celery_jobs(server_params.listCeleryJobs)
            elif cm.command == MessageCommand.GetResults:
                return_params = get_results (cm, server_params)
            elif cm.command == MessageCommand.GetDbStatus:
                return_params = get_db_status (cm, server_params)
            elif cm.command == MessageCommand.GetData:
                return_params = get_job_data (cm, server_params)
            elif cm.command == MessageCommand.GetTags:
                return_params = get_db_tags (cm, server_params)
            elif cm.command == MessageCommand.GetRefl1dResults:
                return_params = get_refl1d_results(cm, server_params);
            elif cm.command == MessageCommand.CommunicationTest:
                return_params = get_comm_status(cm, server_params)
            elif cm.command == MessageCommand.get_tags_jobs:
                return_params = get_tag_jobs(cm, server_params)
            elif cm.command == MessageCommand.get_tag_count:
                return_params = get_tag_count(cm, server_params)
            elif cm.command == MessageCommand.del_by_tag:
                return_params = delete_by_tag(cm, server_params)
            elif cm.command == MessageCommand.load_by_tag:
                return_params = load_jobs_by_tags(cm, server_params)
            elif cm.command == MessageCommand.job_data_by_id:
                return_params = load_jobs_by_id(cm, server_params)
            elif cm.command == MessageCommand.get_all_tag_count:
                return_params = get_all_tag_count(cm, server_params)
            else:
                return_params = {'unknown command' : f'{cm.command}'}
        else:
            print('parse_message error.')
    except Exception as err:
        print(f'handle_incoming_message, error: {err}')
    return return_params
#------------------------------------------------------------------------------
async def bumps_server(websocket, path, server_params):
    message = await websocket.recv()
    try:
        jmsg = json.loads(message)
    except:
        msg = message.replace("'",'"')
        jmsg = json.loads(msg)
    strTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #save_message(strTime + ':\n\n'+ message + '\n')
    return_params = handle_incoming_message (websocket, jmsg, server_params)

    try:
        remote_client = websocket.remote_address[0]
    except Exception as e:
        print(f'Error in bumps_server: {e}')
    reply_message = {}
    reply_message['sender_ip'] = remote_client
    reply_message['command'] = jmsg['command']
    if not(return_params):
        return_params = "None"
    reply_message['params'] = return_params
    await websocket.send(str(reply_message))
#------------------------------------------------------------------------------
def print_intro(serverHost, serverPort):
    print('Welcome to bumps WebSocket server')
    print(f'Host: {serverHost}')
    print(f'Port: {serverPort}')
    print(f'Results directory: "{get_results_dir()}"')
    print(f'Current directory: "{os.getcwd()}"')
#------------------------------------------------------------------------------
def set_server_params(database_engine, flask_dir):
    server_params = ServerParams(database_engine)
    server_params.queueJobEnded = multiprocessing.Queue() # reciever to manager queue 
    server_params.queueRunJobs = multiprocessing.Queue() # run fit job on local machine 
    server_params.listAllJobs = multiprocessing.Manager().list()
    server_params.listCeleryJobs = []
    server_params.flask_dir = flask_dir
    server_params.results_dir = flask_dir + 'static/'

    return server_params
#------------------------------------------------------------------------------
def get_env_db_server():
    try:
        database_server = os.getenv('DATABASE_SERVER')
        if len(database_server) == 0:
            database_server = 'bumps_db'
    except Exception as e:
        database_server = 'bumps_db'
        print(f'get_env_db_server runtime error: {e}')
        print(f'Database server set to default: {database_server}')
    return database_server 
#------------------------------------------------------------------------------
def ws_server_main(serverHost='0.0.0.0', serverPort='4567', flask_dir='/home/app_user/bumps_flask/bumps_flask'):
    print_intro(serverHost, serverPort)
    try:
        connection = None
        if flask_dir[len(flask_dir) - 1] != '/':
            flask_dir += '/'
        database_server = get_env_db_server()
        database_link = f'mysql+pymysql://bumps:bumps_dba@{database_server}:3306/bumps_db'
        database_engine = create_engine(database_link)
        server_params = set_server_params(database_engine, flask_dir)
        connection = database_engine.connect()
    except Exception as e:
        print(f'ws_server_main runtime error: {e}')
        exit(1)
    finally:
        if connection:
            connection.close()
        else:
            print("Fatal error. Aborting :-(")
            exit(1)
    try:
        pRunner = multiprocessing.Process(name='jobs runner', target=jobs_runner_process, args=(server_params,))
        pRunner.start()

        pFinalizer = multiprocessing.Process(name='jobs finalizer', target=job_ending_manager, args=(server_params,))
        pFinalizer.start()

        start_server = websockets.serve(functools.partial(bumps_server, server_params=server_params), serverHost, serverPort)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print('Interrupted')
        loop = asyncio.get_event_loop()
        loop.close()
        print('loop closed')
        pRunner.terminate()
        pFinalizer.terminate()
        pCleaner.terminate()
        print('procersses terminated')
        pRunner.join()
        pFinalizer.join()
        pCleaner.join()
        print('Aborting')
        exit(0)
    except Exception as e:
        print("{}".format(e))
        exit(1)
#------------------------------------------------------------------------------
if __name__ == '__main__':
    host, port = get_host_port (def_host='NCNR-R9nano.campus.nist.gov', def_port=8765)
    ws_server_main()
