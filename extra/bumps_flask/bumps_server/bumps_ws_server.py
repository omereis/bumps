import asyncio
import websockets
import getopt, sys
from time import sleep
import datetime
from get_host_port import get_host_port
import mysql.connector
from mysql.connector import Error
#------------------------------------------------------------------------------
#host = 'localhost'
host = 'NCNR-R9nano.campus.nist.gov'
port = 8765
get_host_port
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
def save_to_db (key, message):
    connect = connect_to_db ()
    print('Database connected')
    connect.close()
    print('Database connection closed')
    return (0)
#------------------------------------------------------------------------------
async def bumps_server(websocket, path):
    message = await websocket.recv()
    strTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    key = generate_key (websocket.remote_address[0])
    id = save_to_db (key, message)
    print ('Key: {}'.format(key))
    save_message(strTime + ':\n'+ message)
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



