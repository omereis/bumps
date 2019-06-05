import asyncio
import websockets
import getopt, sys
from time import sleep
import datetime
from get_host_port import get_host_port
import mysql.connector
import json, os
from mysql.connector import Error
from oe_debug import print_debug
from sqlalchemy import create_engine, MetaData
from bumps_constants import DB_Table, DB_Field_JobID, DB_Field_SentIP, DB_Field_SentTime, DB_Field_Tag, \
                            DB_Field_Message, DB_Field_ResultsDir,DB_Field_JobStatus, DB_Field_EndTime, \
                            DB_Field_ProblemFile
from FitJob import FitJob, JobStatus, name_of_status
from db_misc import get_next_job_id
#from multiprocessing import Process, Queue
import multiprocessing
import nest_asyncio
#------------------------------------------------------------------------------
#from message_parser import *
from message_parser import ClientMessage, MessageCommand, generate_key
#from message_parser import ClientMessage, MessageCommand, extract_file_name, generate_key
#------------------------------------------------------------------------------
#host = 'localhost'
host = 'NCNR-R9nano.campus.nist.gov'
port = 8765
base_results_dir = '/tmp/bumps_results/'
host, port = get_host_port (def_host='NCNR-R9nano.campus.nist.gov', def_port=8765)
database_engine = None
connection = None
qJobs = multiprocessing.Queue() # reciever to manager queue 
qRunJobs = multiprocessing.Queue() # run fit job on local machine 
smprJobRun = asyncio.Semaphore()
smprJobsList = asyncio.Semaphore()
nest_asyncio.apply()
listJobs = []

#------------------------------------------------------------------------------
def save_message (message):
    file = open ("messages.txt", "a+")
    file.write (message + "\n")
    file.close()
#------------------------------------------------------------------------------
def connect_to_db ():
    connect = mysql.connector.connect(host='localhost',
                                       database='bumps_db',
                                       user='bumps',
                                       password='bumps_dba')
    return (connect)
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
"""
def get_problem_file_name (message):
    problem_file_name = ''
    tag = message['tag']
    filename_ok = True
    try:
        problem_file_name = extract_file_name(message['problem_file'])
        if len(problem_file_name.strip()) == 0:
            filename_ok = False
    except:
        filename_ok = False
    finally:
        if not(filename_ok):
            problem_file_name = tag + ".py"
    return problem_file_name
#------------------------------------------------------------------------------
def save_problem_file (results_dir, message):
    problem_file_name = results_dir + "/" + get_problem_file_name (message)
    problem_text = message['fit_problem']
    file = open(problem_file_name, "w+")
    file.write(problem_text)
    file.close()
    return problem_file_name
"""
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
        print(f'{title}: Curreent Jobs')
        print('-----------------------')
        for n in range(len(listJobs)):
            print (f'job {n}, status: {name_of_status(listJobs[n].status)}')
        print('-----------------------')
    except Exception as e:
        print(f'Error in print_job: "{e}"')
#------------------------------------------------------------------------------
def scan_jobs_list (db_connection, listJobs):
    n_running_jobs = count_running_jobs(listJobs)
    n_cpus = multiprocessing.cpu_count()
    print(f'Number of CPUs: {n_cpus}, Number of running jobs: {n_running_jobs}')
    print(f'number of jobs: {len(listJobs)}')
    print_jobs(listJobs, title='before scan')
    for n in range(len(listJobs)):
        status = listJobs[n].status
        if status == JobStatus.Parsed:
            listJobs[n].set_standby(db_connection)
        elif listJobs[n].status == JobStatus.StandBy:
            if n_running_jobs < n_cpus:
                listJobs[n].set_running(db_connection)
    print_jobs(listJobs, title='after scan')
#------------------------------------------------------------------------------
#-------- Process: Job Queue Manager ------------------------------------------
async def queue_reader(jobs_queue):
    while True:
        job = jobs_queue.get()
        job.prepare_params()
        try:
            db_connection = database_engine.connect()
            job.set_standby(db_connection)
            await smprJobsList.acquire() # acquire semaphore before accessing jobs list
            listJobs.append(job)
            scan_jobs_list (db_connection, listJobs)
            smprJobsList.release() # release semaphore at the end of work on jobs list
        finally:
            db_connection.close()
        await asyncio.sleep(5)
#------------------------------------------------------------------------------
def jobs_q_manager(jobs_queue):
    asyncio.run(queue_reader(jobs_queue))
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def StartFit (cm):
    print('StartFit')
    cm.create_results_dir()
    print('StartFit, results directory created')
    cm.save_problem_file()
    print('StartFit, problem file saved')
    fit_job = FitJob (cm)
    #fit_job.status = JobStatus.Parsed
    try:
        db_connection = database_engine.connect()
        job_id = fit_job.save_message_to_db (cm, db_connection)
        fit_job.set_standby(db_connection)
        print(f'bumps_ws_server, StartFit, fit_job.job_id={fit_job.job_id}')
        listJobs.append(fit_job)
        scan_jobs_list (db_connection, listJobs)
        #qJobs.put(fit_job)
    except:
        print ('bumps_ws_server.py, StartFit, bug: {}'.format(e))
        job_id = 0
    finally:
        if db_connection:
            db_connection.close()
    return job_id
#------------------------------------------------------------------------------
def get_orred_ids (params):
    astrWhere = []
    for id in params:
        astrWhere.append ('(' + DB_Field_JobID + '=' + str(id) + ')')
    if len(astrWhere) > 1:
        strWhere = ' or '.join(astrWhere)
    else:
        strWhere = astrWhere[0]
    return strWhere
import shutil
#------------------------------------------------------------------------------
def delete_results_dir(db_connection, sqlWhere):
    sql = 'select ' + DB_Field_ResultsDir + ' from ' +  DB_Table + ' where ' + sqlWhere + ";"
    res = db_connection.execute(sql)
    for row in res:
        try:
            shutil.rmtree(row[0])
        except Exception as e:
            print ('delete_results_dir, error: {}'.format(e))
        
#------------------------------------------------------------------------------
def HandleDelete (cm):
    return_params = cm.params
    try:
        db_connection = database_engine.connect()
        sqlBase = 'delete from ' + DB_Table + ' where '
        sqlWhere = get_orred_ids (cm.params)
        delete_results_dir(db_connection, sqlWhere)
        sql = sqlBase + sqlWhere
        db_connection.execute(sql)
    except Exception as e:
        print ('bumps_ws_server.py, HandleDelete, bug: {}'.format(e))
    finally:
        if db_connection:
            db_connection.close()
    return return_params
 #------------------------------------------------------------------------------
def HandleStatus (cm):
    return_params = []
    #await smprJobsList.acquire() # acquire semaphore before accessing jobs list
    print_jobs(listJobs, title='HandleStatus')
    print(f'HandleStatus, message tag: {cm.tag}')
    for job in listJobs:
        print(f'HandleStatus, job_id: {job.job_id}, tag: "{job.get_tag()}"')
        if job.get_tag() == cm.tag:
            if job.job_id == None:
                job_id = -1
            else:
                job_id = job.job_id
            item = {'job_id': job_id, 'job_status': name_of_status(job.status)}
            return_params.append(item)
    return return_params
 #------------------------------------------------------------------------------
def handle_incoming_message (websocket, host_ip, message, listJobs):
    #print('handle_incoming_message')
    return_params = {}
    cm = ClientMessage()
    try:
        if cm.parse_message(websocket, message):
            print('handle_incoming_message, message parsed ok')
            if cm.command == MessageCommand.StartFit:
                job_id = StartFit (cm)
                if job_id:
                    return_params[cm.row_id] = job_id # return job_id to client
            elif cm.command == MessageCommand.Delete:
                return_params = HandleDelete (cm)
            elif cm.command == MessageCommand.Status:
                return_params = HandleStatus (cm)
#        elif cm.command == MessageCommand.Status:
        else:
            print('parse_message error.')
    except Exception as e:
        print(f'handle_incomming_message, error: {e}')
    return return_params
#------------------------------------------------------------------------------
async def bumps_server(websocket, path):
    message = await websocket.recv()
    try:
        jmsg = json.loads(message)
    except:
        jmsg={}
    strTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_message(strTime + ':\n\n'+ message + '\n')
    #key = generate_key (websocket.remote_address[0], strTime)
    return_params = handle_incoming_message (websocket, websocket.remote_address[0], json.loads(message), listJobs)
    print ('\nReturn Params: {}\n'.format(return_params))

    source = "{}:{}".format(websocket.host, websocket.port)
    print ("Just got a message from...")
    try:
        remote_client = websocket.remote_address[0]
        print ("    client in {}".format(source))
    except Exception as e:
        print(f'Error in bumps_server: {e}')
    reply_message = {}
    reply_message['sender_ip'] = remote_client
    reply_message['command'] = jmsg['command']
    if not(return_params):
        return_params = "None"
    reply_message['params'] = return_params
    sleep(0.1)
    print('bumps_server, return_params: {}'.format(return_params))
    await websocket.send(str(reply_message))
#------------------------------------------------------------------------------
if __name__ == '__main__':
    print('Welcome to bumps WebSocket server')
    print('Host: {}'.format(host))
    print('Port: {}'.format(port))

    try:
        database_engine = create_engine('mysql+pymysql://bumps:bumps_dba@NCNR-R9nano.campus.nist.gov:3306/bumps_db')
        connection = database_engine.connect()
        print("Database connected")
    except Exception as e:
        print("Error while connecting to database bumps_db in NCNR-R9nano.campus.nist.gov:3306:")
        print("{}".format(e))
        exit(1)
    finally:
        if connection:
            connection.close()
            print("Database connection closed")
        else:
            print("Fatal error. Aborting :-(")
            exit(1)
    try:
        pReader = multiprocessing.Process(name='jobs_reader', target=jobs_q_manager, args=(qJobs,))
        pReader.start()

        start_server = websockets.serve(bumps_server, host, port)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    finally:
        pReader.close()



