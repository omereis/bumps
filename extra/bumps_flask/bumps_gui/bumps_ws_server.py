import asyncio
import websockets
import getopt, sys
import datetime
import mysql.connector
import json, os
import multiprocessing
import nest_asyncio
from mysql.connector import Error
from sqlalchemy import create_engine, MetaData
from bumps import cli
from time import sleep
try:
    from .oe_debug import print_debug
    from .bumps_constants import *
    from .misc import get_results_dir, get_web_results_dir
    from .FitJob import FitJob, JobStatus, name_of_status, ServerParams, find_job_by_id
    from .db_misc import get_next_job_id, results_dir_for_job
    from .message_parser import ClientMessage, generate_key
    from .get_host_port import get_host_port
    from .MessageCommand import MessageCommand
except:
    from oe_debug import print_debug
    from bumps_constants import *
    from misc import get_results_dir, get_web_results_dir
    from FitJob import FitJob, JobStatus, name_of_status, ServerParams, find_job_by_id
    from db_misc import get_next_job_id, results_dir_for_job
    from message_parser import ClientMessage, MessageCommand, generate_key
    from get_host_port import get_host_port
    from MessageCommand import MessageCommand
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
host = 'NCNR-R9nano.campus.nist.gov'
port = 8765
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
def scan_jobs_list (server_params):
    n_cpus = multiprocessing.cpu_count()
    for n in range(len(server_params.listAllJobs)):
        n_running_jobs = count_running_jobs(server_params.listAllJobs)
        fit_job = server_params.listAllJobs[n]
        if fit_job.status == JobStatus.Parsed:
            fit_job.set_standby(server_params.db_connection)
            #print_debug(f'"scan_jobs_list", process ID {os.getpid()}, writing job {fit_job.job_id} to queueRunJobs, , list contains {server_params.jobs_count()} jobs')
        elif fit_job.status == JobStatus.StandBy:
            if n_running_jobs < n_cpus:
                #print_debug(f'"scan_jobs_list", process ID {os.getpid()}, writing job {fit_job.job_id} to queueRunJobs, , list contains {server_params.jobs_count()} jobs')
                fit_job.prepare_params()
                fit_job.set_running(server_params.get_connection())
                server_params.listAllJobs[n] = fit_job
                server_params.queueRunJobs.put(fit_job)
                #print_debug(f'"scan_jobs_list", process ID {os.getpid()}, job {fit_job.job_id} written to queueRunJobs, current status {name_of_status(fit_job.status)} list contains {server_params.jobs_count()} jobs')
                #print_jobs (server_params.listAllJobs, "scan_jobs_list")
#------------------------------------------------------------------------------
#-------- Process: Job Queue Manager ------------------------------------------
import bumps.cli
def run_fit_job (fit_job, server_params):
    try:
        sys.argv = fit_job.params
        try:
            #print_debug(f'"run_fit_job", process {os.getpid()}, fit job {fit_job.job_id} running, params: {fit_job.params}')
            #print_debug(f'"run_fit_job", process {os.getpid()}, fit job {fit_job.job_id} running')
            bumps.cli.main()
        finally:
            #rint_debug(f'"run_fit_job", process {os.getpid()}, fit job {fit_job.job_id} ended')
            server_params.queueJobEnded.put(fit_job)
            #print_debug(f'"run_fit_job", process {os.getpid()}, fit job {fit_job.job_id} added to queueJobEnded')
    except Exception as e:
        print (f'Error in run_fit_job: {e}')
#------------------------------------------------------------------------------
async def job_runner(server_params):
    while True:
        fit_job = server_params.queueRunJobs.get()
        try:
            #print_debug(f"'job_runner', job id {fit_job.job_id}, status {name_of_status(fit_job.status)}")
            #fit_job.prepare_params()
            #fit_job.set_running(server_params.get_connection())
            run_fit_job (fit_job, server_params)
        except Exception as e:
            print(f'Error in job_runner: {e}')
#------------------------------------------------------------------------------
def jobs_runner_process(server_params):
    print(f'"jobs_q_manager", started process with id {os.getpid()}, number of jobs: {len(server_params.listAllJobs)}')
    asyncio.run(job_runner(server_params))
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
async def job_finalizer(server_params):
    while True:
        #print(f'"job_finalizer", process {os.getpid()}, waiting for a fit job to end')
        fit_job = server_params.queueJobEnded.get()
        print_debug(f'"job_finalizer", process {os.getpid()}, fit job {fit_job.job_id} ended, not completed')
        print(f'"job_finalizer", process {os.getpid()}, fit job {fit_job.job_id} ended, not completed')
        fit_job.save_params()
        sys.stdout.flush()
        if fit_job.status == JobStatus.Running:
            try:
                #db_connection = database_engine.connect()
                idx = find_job_by_id(server_params.listAllJobs, fit_job.job_id)
                if idx >= 0:
                    job = server_params.listAllJobs[idx]
                    job.set_completed(server_params.get_connection())
                    server_params.listAllJobs[idx] = job
                else:
                    print(f'job_finalizer, process {os.getpid()}, job {fit_job.job_id} not on list')
                #print_debug(f'"job_finalizer", process {os.getpid()}, fit job {fit_job.job_id} ended and completed')
                #print(f'"job_finalizer", process {os.getpid()}, fit job {fit_job.job_id} ended and completed')
                #sys.stdout.flush()
                #scan_jobs_list (db_connection, server_params)
                #print_jobs(server_params.listAllJobs, "job_finalizer")
                scan_jobs_list (server_params)
            except Exception as e:
                print_debug(f'"job_finalizer", process {os.getpid()}, error"{e}"')
            finally:
                server_params.close_connection()
                #db_connection.close()
#------------------------------------------------------------------------------
def job_ending_manager(server_params):
    print(f'"job_ending_manager", started process with id {os.getpid()}, length(listJobs): {len(server_params.listAllJobs)}')
    asyncio.run(job_finalizer(server_params))
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def HandleFitMessage (cm, server_params):
    cm.create_results_dir(server_params)
    cm.save_problem_file()
    fit_job = FitJob (cm)
    try:
        db_connection = server_params.database_engine.connect()
        job_id = fit_job.save_message_to_db (cm, db_connection)
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
        db_connection = server_params.database_engine.connect()
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
import os
def get_results (cm, server_params):
    print(f'getting results for job {cm.params}')
    try:
        results_dir = results_dir_for_job (server_params.database_engine, cm.params)
        flask_dir = server_params.flask_dir
        final_dir = results_dir[len(flask_dir) - 1 : ]

#        print('-------------------------')
#        print('-------Directories-------')
#        print(f'results: "{results_dir}"')
#        print(f'web results: "{web_dir}"')
#        print(f'final dir: "{final_dir}"')
#        print(f'flask dir: "{server_params.flask_dir}"')
#        print(f'Results dir: "{server_params.results_dir}"')
        
        files_list = os.listdir(results_dir)
        files = []
        for file in files_list:
            file = final_dir + '/' + file
            files.append(file)
#        for file in files:
#            print (f'file: {file}')
    except Exception as e:
        print(f'Error in "get_results": {e}')
        files = {e}
    return_params = {'id': cm.params, 'files' : files}
    return return_params
#------------------------------------------------------------------------------
def handle_incoming_message (websocket, message, server_params):
    return_params = {}
    cm = ClientMessage()
    try:
        if cm.parse_message(websocket, message, server_params):
            print(f'Message command: {cm.command}')
            if cm.command == MessageCommand.StartFit:
                job_id = HandleFitMessage (cm, server_params)
                if job_id:
                    return_params[cm.row_id] = job_id # return job_id to client
            elif cm.command == MessageCommand.Delete:
                return_params = asyncio.run(HandleDelete (cm, server_params))
            elif cm.command == MessageCommand.Status:
                return_params = asyncio.run(HandleStatus (cm, server_params))
            elif  cm.command == MessageCommand.PrintStatus:
                print_jobs(server_params.listAllJobs, title='current_status')
            elif cm.command == MessageCommand.GetResults:
                return_params = get_results (cm, server_params)
        else:
            print('parse_message error.')
    except Exception as err:
        print(f'handle_incoming_message, error: {err}')
    return return_params
#------------------------------------------------------------------------------
import functools
async def bumps_server(websocket, path, server_params):
    message = await websocket.recv()
    try:
        jmsg = json.loads(message)
    except:
        jmsg={}
    strTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_message(strTime + ':\n\n'+ message + '\n')
    return_params = handle_incoming_message (websocket, json.loads(message), server_params)

    source = "{}:{}".format(websocket.host, websocket.port)
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
def print_intro():
    print('Welcome to bumps WebSocket server')
    print('Port: {}'.format(port))
    print(f'Results directory: "{get_results_dir()}"')
    print(f'Current directory: "{os.getcwd()}"')
#------------------------------------------------------------------------------
def set_server_params(database_engine, flask_dir):
    server_params = ServerParams(database_engine)
    server_params.queueJobEnded = multiprocessing.Queue() # reciever to manager queue 
    server_params.queueRunJobs = multiprocessing.Queue() # run fit job on local machine 
    server_params.listAllJobs = multiprocessing.Manager().list()
    server_params.flask_dir = flask_dir
    server_params.results_dir = flask_dir + 'static/'

    return server_params
#------------------------------------------------------------------------------
def ws_server_main(serverHost='0.0.0.0', serverPort='4567', flask_dir='/home/app_user/bumps_flask/bumps_flask'):
    print_intro()
    try:
        connection = None
        if flask_dir[len(flask_dir) - 1] != '/':
            flask_dir += '/'
        database_engine = create_engine('mysql+pymysql://bumps:bumps_dba@NCNR-R9nano.campus.nist.gov:3306/bumps_db')
        server_params = set_server_params(database_engine, flask_dir)
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
        print('Aborting')
        exit(0)
    except Exception as e:
        print("{}".format(e))
        exit(1)
#------------------------------------------------------------------------------
if __name__ == '__main__':
    host, port = get_host_port (def_host='NCNR-R9nano.campus.nist.gov', def_port=8765)
    ws_server_main()
