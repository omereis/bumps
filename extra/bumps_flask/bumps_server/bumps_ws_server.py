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
                            DB_Field_Message, DB_Field_ResultsDir,DB_Field_JobStatus, DB_Field_EndTime

#------------------------------------------------------------------------------
#host = 'localhost'
host = 'NCNR-R9nano.campus.nist.gov'
port = 8765
base_results_dir = '/tmp/bumps_results/'
host, port = get_host_port (def_host='NCNR-R9nano.campus.nist.gov', def_port=8765)
database_engine = None
connection = None

#------------------------------------------------------------------------------
def save_message (message):
    file = open ("messages.txt", "a+")
    file.write (message + "\n")
    file.close()
#------------------------------------------------------------------------------
def generate_key (client_host):
    strTime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%-S")
    key = client_host.replace('.','_')
    if (len(key) < 1):
        key='localhost'
    key += '_' + strTime
    return (key)
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
    print("Message header: {}".format(header))
    return ''
#------------------------------------------------------------------------------
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
    print ("Results file: {}".format(problem_file_name))
    file = open(problem_file_name, "w+")
    file.write(problem_text)
    file.close()
    return problem_file_name
#------------------------------------------------------------------------------
def get_next_job_id(connection):
    job_id = 0
    try:
        sql = 'select max({}) from {};'.format(DB_Field_JobID, DB_Table)
        res = connection.execute(sql)
        for row in res:
            job_id = row.values()[0]
    except Exception as e:
        print("Error in get_next_job_id()")
        print("{}".format(e))
        job_id = None
    return job_id
#------------------------------------------------------------------------------
def get_message_datetime_string (message_time):
    datetime_str = '{}-{}-{} {}:{}:{}.{}'.format(message_time['year'], message_time['month'], message_time['date'],\
                                    message_time['hour'], message_time['minutes'], message_time['seconds'], message_time['milliseconds'])
    return datetime_str
#------------------------------------------------------------------------------
def save_message_to_db (cm, connection):
    try:
        job_id = get_next_job_id(connection)
        message_date_time = get_message_datetime_string (cm.message_time)
        if job_id:
            job_id = job_id + 1
            sql = 'insert into {} ({},{},{},{},{},{}) values ({},"{}","{}","{}","{}","{}");'.format(\
                        DB_Table,
                        DB_Field_JobID, DB_Field_SentIP, DB_Field_SentTime, DB_Field_Tag, DB_Field_Message, DB_Field_ResultsDir,
                        job_id, cm.host_ip, message_date_time, cm.tag, cm.message, cm.results_dir)
            res = connection.execute(sql)
    except Exception as e:
        print ('bumps_ws_server, save_message_to_db, bug: {}'.format(e))
    return job_id
#------------------------------------------------------------------------------
def StartFit (cm):
    cm.create_results_dir()
    cm.save_problem_file()
    try:
        connection = database_engine.connect()
        print ('bumps_ws_server.py, StartFit, cm.results_dir: {}'.format(cm.results_dir))
        job_id = save_message_to_db (cm, connection)
    except:
        print ('bumps_ws_server.py, StartFit, bug: {}'.format(e))
        job_id = 0
    finally:
        if connection:
            connection.close()
    return job_id
#    problem_file_name = save_problem_file (results_dir, message)
#------------------------------------------------------------------------------
from message_parser import ClientMessage, MessageCommand
#------------------------------------------------------------------------------
def handle_incoming_message (key, websocket, host_ip, message):
    job_id = 0
    cm = ClientMessage()
    if cm.parse_message(websocket, message):
        if cm.command == MessageCommand.StartFit:
            job_id = StartFit (cm)

#    if message['command'] == 'StartFit':
#        job_id = StartFit (key, host_ip, message)
#    print('Database connected')
#    print('Database connection closed')
    return job_id
#------------------------------------------------------------------------------
async def bumps_server(websocket, path):
    message = await websocket.recv()
    try:
        jmsg = json.loads(message)
    except:
        jmsg={}
    strTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print ("Message Time: {}".format(strTime))
    save_message(strTime + ':\n'+ message)
    key = generate_key (websocket.remote_address[0])
    job_id = handle_incoming_message (key, websocket, websocket.remote_address[0], json.loads(message))
    print ('\nmessage Key: {}\n'.format(key))
    print ('\nmessage ID: {}\n'.format(job_id))
#    save_message(message)
    source = "{}:{}".format(websocket.host, websocket.port)
    print ("Just got a message from...")
    try:
        remote_client = websocket.remote_address[0]
        print ("    client in {}".format(source))
    except Exception as e:
        print('Oops: {}'.format(e))
    greeting = 'your ip: {}'.format(remote_client)
    reply_message = {}
    reply_message['command'] = jmsg['command']
    reply_message['sender_ip'] = remote_client
    reply_message['sender_id'] = jmsg['row_id']
    reply_message['db_id'] = job_id
    sleep(1)
    await websocket.send(str(reply_message))
#    await websocket.send(greeting)
#------------------------------------------------------------------------------
#class w:
#    remote_address = ['129.6.123.151','localhost']
#in_msg = {"header":"bumps client","tag":"climb","message_time":"2019_5_2_11_25_613","command":"StartFit","fit_problem":"etrhae","problem_file":"","params":{"algorithm":"rpg","steps":"100","burns":"100"},"multi_processing":"none"}
#websocket = w()
#job_id = handle_incoming_message (0, websocket, "129.6.123.151", in_msg)
#exit(0)
#------------------------------------------------------------------------------
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
start_server = websockets.serve(bumps_server, host, port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


