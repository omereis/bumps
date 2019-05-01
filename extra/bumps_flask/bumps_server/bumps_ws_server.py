import asyncio
import websockets
import getopt, sys
from time import sleep
import datetime
from get_host_port import get_host_port
import mysql.connector
import json, os
from mysql.connector import Error
#------------------------------------------------------------------------------
#host = 'localhost'
host = 'NCNR-R9nano.campus.nist.gov'
port = 8765
base_results_dir = '/tmp/bumps_results/'
host, port = get_host_port (def_host='NCNR-R9nano.campus.nist.gov', def_port=8765)
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
def create_results_dir (key, host_ip, message):
    tag = message['tag']
    tmp_dir = results_dir = base_results_dir + host_ip + "/" + tag
    dir_len = len(results_dir)
    n = 1
    while os.path.exists(results_dir):
        results_dir = tmp_dir + '_' + str(n)
        n = n + 1
    os.makedirs (results_dir, 0o7777)
    os.chmod(results_dir, 0o7777)
    return results_dir
#------------------------------------------------------------------------------
def extract_file_name(filename):
    name = filename
    if (name.find('\\') >= 0):
        inv = name[::-1]
        p = inv.find('\\')
        inv = inv[0:p]
        name = p[::-1]
    return name
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
def StartFit (key, host_ip, message):
    results_dir = create_results_dir (key, host_ip, message)
    problem_file_name = save_problem_file (results_dir, message)
    print ("Results directory: {}".format(results_dir))
    print ("Results file: {}".format(problem_file_name))
#------------------------------------------------------------------------------
def handle_incoming_message (key, host_ip, message):
    connect = connect_to_db ()
    if message['command'] == 'StartFit':
        StartFit (key, host_ip, message)
#    print('Database connected')
    connect.close()
#    print('Database connection closed')
    return (0)
#------------------------------------------------------------------------------
async def bumps_server(websocket, path):
    message = await websocket.recv()
    strTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print ("Message Time: {}".format(strTime))
    save_message(strTime + ':\n'+ message)
    key = generate_key (websocket.remote_address[0])
    id = handle_incoming_message (key, websocket.remote_address[0], json.loads(message))
    print ('Key: {}'.format(key))
#    save_message(message)
    source = "{}:{}".format(websocket.host, websocket.port)
    print ("Just got a message from...")
    try:
        remote_client = websocket.remote_address[0]
        print ("    client in {}".format(source))
    except Exception as e:
        print('Oops: {}'.format(e))
    greeting = 'your ip: {}'.format(remote_client)
    sleep(1)
    await websocket.send(greeting)
#------------------------------------------------------------------------------
print('Welcome to bumps WebSocket server')
print('Host: {}'.format(host))
print('Port: {}'.format(port))
start_server = websockets.serve(bumps_server, host, port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()



