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
from bumps import cli
from bumps_constants import DB_Table, DB_Field_JobID, DB_Field_SentIP, DB_Field_SentTime, DB_Field_Tag, \
                            DB_Field_Message, DB_Field_ResultsDir,DB_Field_JobStatus, DB_Field_EndTime, \
                            DB_Field_ProblemFile
from FitJob import FitJob, JobStatus, name_of_status, ServerParams
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
nest_asyncio.apply()

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
def scan_jobs_list (db_connection, server_params):
    n_running_jobs = count_running_jobs(server_params.listAllJobs)
    n_cpus = multiprocessing.cpu_count()
    #print_jobs(server_params.listAllJobs, title='before scan')
    for n in range(len(server_params.listAllJobs)):
        if server_params.listAllJobs[n].status == JobStatus.Parsed:
            server_params.listAllJobs[n].status[n].set_standby(db_connection)
        elif server_params.listAllJobs[n].status == JobStatus.StandBy:
            if n_running_jobs < n_cpus:
                print(f'"scan_jobs_list", before putting job in "queueRunJobs", process ID {os.getpid()}')
                server_params.queueRunJobs.put(server_params.listAllJobs[n])
                #server_params.run_job (n, db_connection)
                #run_fit_job (server_params.listAllJobs[n], server_params)
    #print_jobs(server_params.listAllJobs, title='after scan')
#------------------------------------------------------------------------------
#-------- Process: Job Queue Manager ------------------------------------------
import bumps.cli
def run_fit_job (fit_job, server_params):
    try:
        sys.argv = fit_job.params
        print('Fit job started')
        try:
            bumps.cli.main()
        finally:
            print('\n\n\nFit job completed')
            server_params.queueJobEnded.put(fit_job)
    except Exception as e:
        print (f'Error in run_fit_job: {e}')
#------------------------------------------------------------------------------
async def job_runner(server_params):
#async def queue_reader(jobs_queue,queueJobEnded,listAllJobs,smprJobsList):
    while True:
        print(f'"job_runner", waiting on queueRunJobs')
        sys.stdout.flush()
        fit_job = server_params.queueRunJobs.get()
        print(f'"job_runner", new job from queueRunJobs')
        sys.stdout.flush()
        try:
            fit_job.prepare_params()
            fit_job.set_running(server_params.get_connection())
            idx = find_job_by_id (server_params.listAllJobs, fit_job.job_id)
            if idx >= 0:
                print(f'"job_runner", job {fit_job.job_id} status changed to "{name_of_status(fit_job.status)}')
                print(f'"job_runner", connection closed, {len(server_params.listAllJobs)} jobs')
                server_params.listAllJobs[idx] = fit_job
                print(f'"job_runner", job {fit_job.job_id} status changed to "{name_of_status(server_params.listAllJobs[idx].status)}')
            print (f'"job_runner", process id : {os.getpid()}, fit job params (after preparation): {fit_job.params}')
            run_fit_job (fit_job, server_params)
        except Exception as e:
            print(f'Error in job_runner: {e}')
        finally:
            server_params.close_connection()
            print(f'"job_runner", connection closed, {len(server_params.listAllJobs)} jobs')
            sys.stdout.flush()
#------------------------------------------------------------------------------
def jobs_runner_process(server_params):
    print(f'"jobs_q_manager", started process with id {os.getpid()}, number of jobs: {len(server_params.listAllJobs)}')
    asyncio.run(job_runner(server_params))
#------------------------------------------------------------------------------
def find_job_by_id (listJobs, job_id):
    iFound = -1
    n = 0
    while (n < len(listJobs)) & (iFound < 0):
        if listJobs[n].job_id == job_id:
            iFound = n
    return iFound
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
async def job_finalizer(server_params):
    while True:
        fit_job = server_params.queueJobEnded.get()
        try:
            db_connection = database_engine.connect()
            idx = find_job_by_id(server_params.listAllJobs, fit_job.job_id)
            if idx >= 0:
                job = server_params.listAllJobs[idx]
                job.set_completed(db_connection)
                server_params.listAllJobs[idx] = job
            else:
                fit_job.set_completed(db_connection)
            print(f'"job_finalizer", process {os.getpid()}, fit job {fit_job.job_id} complted')
            sys.stdout.flush()
            scan_jobs_list (db_connection, server_params)
        finally:
            db_connection.close()
#------------------------------------------------------------------------------
def job_ending_manager(server_params):
    print(f'"job_ending_manager", started process with id {os.getpid()}, length(listJobs): {len(server_params.listAllJobs)}')
    asyncio.run(job_finalizer(server_params))
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
async def add_job_to_queue (fit_job, listJobs, smprJobsList):
    await smprJobsList.acquire()
    listJobs.append(fit_job)
    smprJobsList.release()
#------------------------------------------------------------------------------
def HandleFitMessage (cm, server_params):
    cm.create_results_dir()
    cm.save_problem_file()
    fit_job = FitJob (cm)
    try:
        db_connection = database_engine.connect()
        job_id = fit_job.save_message_to_db (cm, db_connection)
        fit_job.set_standby(db_connection)
        print(f'bumps_ws_server, HandleFitMessage, fit_job.job_id={fit_job.job_id}')
        #server_params.queueRunJobs.put(fit_job)
        server_params.listAllJobs.append(fit_job)
        scan_jobs_list (db_connection, server_params)
    except:
        print ('bumps_ws_server.py, HandleFitMessage, bug: {}'.format(e))
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
async def HandleDelete (cm, server_params):
    return_params = cm.params
    db_connection = None
    try:
        db_connection = database_engine.connect()
        remove_from_list_by_id (server_params.listAllJobs, cm.params, db_connection)
    except Exception as e:
        print ('bumps_ws_server.py, HandleDelete, bug: {}'.format(e))
    finally:
        if db_connection:
            db_connection.close()
    return return_params
 #------------------------------------------------------------------------------
async def HandleStatus (cm, server_params):
    return_params = []
    for job in server_params.listAllJobs:
        if job.get_tag() == cm.tag:
            if job.job_id == None:
                job_id = -1
            else:
                job_id = job.job_id
            item = {'job_id': job_id, 'job_status': name_of_status(job.status)}
            return_params.append(item)
    return return_params
 #------------------------------------------------------------------------------
def handle_incoming_message (websocket, message, server_params):
    return_params = {}
    cm = ClientMessage()
    try:
        if cm.parse_message(websocket, message):
            if cm.command == MessageCommand.StartFit:
                print(f'"handle_incoming_message", in process {os.getpid()}, before calling StartFit')
                job_id = HandleFitMessage (cm, server_params)
                print(f'"handle_incoming_message", fit job with id of {job_id} in process {os.getpid()}')
                if job_id:
                    return_params[cm.row_id] = job_id # return job_id to client
            elif cm.command == MessageCommand.Delete:
                return_params = asyncio.run(HandleDelete (cm, server_params))
            elif cm.command == MessageCommand.Status:
                return_params = asyncio.run(HandleStatus (cm, server_params))
            elif  cm.command == MessageCommand.PrintStatus:
                print_jobs(server_params.listAllJobs, title='current_status')
        else:
            print('parse_message error.')
    except Exception as err:
        print(f'handle_incomming_message, error')
        print(f'handle_incomming_message, error: {err}')
    return return_params
#------------------------------------------------------------------------------
import functools
async def bumps_server(websocket, path, server_params):
#async def bumps_server(websocket, path, lstJobs, ):
#async def bumps_server(websocket, path):
    #print(f'type of "websocket": {type(websocket)}')
    message = await websocket.recv()
    try:
        jmsg = json.loads(message)
    except:
        jmsg={}
    strTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_message(strTime + ':\n\n'+ message + '\n')
    #return_params = handle_incoming_message (websocket, json.loads(message), lstJobs, smprJobsList)
    return_params = handle_incoming_message (websocket, json.loads(message), server_params)
    print (f'Return Params: {return_params}')

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
    #sleep(0.1)
    print(f'bumps_server, return_params: {return_params}')
    await websocket.send(str(reply_message))
#------------------------------------------------------------------------------
if __name__ == '__main__':
    print('Welcome to bumps WebSocket server')
    print('Host: {}'.format(host))
    print('Port: {}'.format(port))

    try:
        database_engine = create_engine('mysql+pymysql://bumps:bumps_dba@NCNR-R9nano.campus.nist.gov:3306/bumps_db')
        connection = database_engine.connect()

        server_params = ServerParams(database_engine)
        server_params.queueJobEnded = multiprocessing.Queue() # reciever to manager queue 
        server_params.queueRunJobs = multiprocessing.Queue() # run fit job on local machine 
        server_params.smprJobRun = asyncio.Semaphore()
        server_params.smprJobsList = asyncio.Semaphore()
        server_params.listAllJobs = multiprocessing.Manager().list()
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
        pRunner = multiprocessing.Process(name='jobs runner', target=jobs_runner_process, args=(server_params,))
        pRunner.start()

        pFinalizer = multiprocessing.Process(name='jobs finalizer', target=job_ending_manager, args=(server_params,))
#        pFinalizer = multiprocessing.Process(name='jobs finalizer', target=job_ending_manager, args=(queueJobEnded,listAllJobs,smprJobsList,))
        pFinalizer.start()

        start_server = websockets.serve(functools.partial(bumps_server, server_params=server_params), host, port)
        #start_server = websockets.serve(functools.partial(bumps_server, lstJobs=listAllJobs), host, port)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        print("{}".format(e))
        exit(1)
    finally:
        pRunner.terminate()
        pFinalizer.terminate()



