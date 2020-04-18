from flask import Flask, render_template, request
from bumps_params import BumpsParams
import json, sys, getopt, os, multiprocessing
import websocket, redis
from bumps_ws_server import ws_server_main
from bumps_params import read_y_n
from bumps_celery import bumps_celery_setup, celery
from oe_debug import print_debug

#------------------------------------------------------------------------------
# Source:
# https://stackoverflow.com/questions/40963401/flask-dynamic-data-update-without-reload-page
# websocket source:
# https://github.com/websocket-client/websocket-client/blob/master/examples/echo_client.py
#------------------------------------------------------------------------------
servers_file_name = 'bumps_celery/bumps_celery_servers.json'
dct_servers_default = {'broker': {'type': 'rabbit', 'address': 'bumps:bumps@ncnr-r9nano.campus.nist.gov'}, 'backend': {'type': 'redis', 'address': 'ncnr-r9nano.campus.nist.gov'}}
#------------------------------------------------------------------------------
app = Flask(__name__)
#------------------------------------------------------------------------------
@app.route('/onsendfitjob')
def on_send_fit_job():
    global bumps_params
    res = {}
    try:
        res = request.args['message']
        cm = json.loads(res)
        msg = json.dumps(cm)
        ws = websocket.create_connection(f'ws://{bumps_params.server}:{bumps_params.mp_port}')
        ws.send(msg)
        ret = ws.recv()
        ws.close()
    except Exception as e:
        print (f'run time error in on_send_fit_job: {e}')
    return ret
#------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('bumps_mp_gui.html')
#------------------------------------------------------------------------------
import pika
#------------------------------------------------------------------------------
def test_rabbit(strRabbit, lstResult):
    print(f'test_rabbit, rabbit stri`ng: {strRabbit}')
    fRabbit = False
    sResult = ''
    try:
        con = pika.BlockingConnection(pika.ConnectionParameters(strRabbit))
        con.close()
        fRabbit = True
        sResult = 'RabbitMQ OK'
    except Exception as e:
        sErr = f'{e.args[0].exception.args[1]}'.replace('"',"'")
        sResult = f"test_rabbit, connection error.\nConnection String: {strRabbit}\nError: {sErr}"
        fRabbit = False
    lstResult[0] = sResult
    return (fRabbit)
#------------------------------------------------------------------------------
def test_redis(strRedis, lstResult):
    try:
        rdb = redis.StrictRedis(host=strRedis)
        rdb.mset({'bumps' : 'test'})
        rdb.delete ('bumps')
        sResult = f'Redis OK'
        print(sResult)
        rdb.close()
        fRedis = True
    except Exception as e:
        sResult = f"test_redis runtime error:\n{e}"
        print(sResult)
        fRedis = False
    lstResult[0] = sResult
    return (fRedis)
#------------------------------------------------------------------------------
def test_server_setup(dictSetup):
    dictResults = {}
    try:
        strBroker = dictSetup[bumps_celery_setup.ADDRESS]
        lstResult = ['0']
        if dictSetup[bumps_celery_setup.TYPE] == bumps_celery_setup.RABBIT:
            if test_rabbit(strBroker, lstResult):
                fTest = 1
            else:
                fTest = 0
            sResult = lstResult[0]
        elif dictSetup[bumps_celery_setup.TYPE] == bumps_celery_setup.REDIS:
            if test_redis(dictSetup[bumps_celery_setup.ADDRESS], lstResult):
                fTest = 1
            else:
                fTest = 0
            sResult = lstResult[0]
        else:
            fTest = 0
            sResult = f'Type "{dictSetup[bumps_celery_setup.TYPE]}" not supported'
    except Exception as e:
        print(f'Test Broker Setup runtime error:\n{e}')
        fTest = 0
        strErr = f'e'.replace('"',"'")
        sResult = f'Broker Setup runtime error:\n{strErr}'
    finally:
        dictResults['result'] = fTest
        dictResults['message'] = sResult
    return dictResults
#------------------------------------------------------------------------------
@app.route('/test_server')
def test_server():
    dctResults = {}
    try:
        client_args = request.args.to_dict()['jsdata']
        jsonSetup = json.loads(client_args)
        dctResults[bumps_celery_setup.BROKER] = test_server_setup(jsonSetup[bumps_celery_setup.BROKER])
        dctResults[bumps_celery_setup.BACKEND] = test_server_setup(jsonSetup[bumps_celery_setup.BACKEND])
    except Exception as e:
        print (f'Broker testing run time error:\n{e}')
        dctResults['results'] = "0"
        dctResults['message'] = f'{e}'
    return str(dctResults)
#------------------------------------------------------------------------------
@app.route('/test_celery')
def test_celery():
    jsonServers = bumps_celery_setup.get_servers_string()
    appTest = celery.appTest(jsonServers)
    #appTest.start()
    return jsonServers
#------------------------------------------------------------------------------
@app.route('/save_server_setup')
def save_server_setup():
    f = None
    try:
        client_args = request.args.to_dict()['jsdata']
        f = open (servers_file_name, 'w+')
        f.write(client_args)
        f.close()
        servers = str(read_servers()).lower()
    except Exception as e:
        servers = f'Error:\nCould not save servers parameters:\n{e}'
    finally:
        if f:
            f.close()
    return servers
#------------------------------------------------------------------------------
@app.route('/get_servers_default')
def get_servers_default():
    dct = add_connection_strings(dct_servers_default)
    #return str(dct_servers_default)
    return dct
#------------------------------------------------------------------------------
def read_servers():
    dct = {}
    f = None
    try:
        f = open (servers_file_name, 'r')
        s = f.read()
        dct = json.loads(s.lower().replace("'",'"'))
        dct = add_connection_strings(dct)
        #dctStrings = bumps_celery_setup.get_servers_string_from_dict(dct)
        #dct[bumps_celery_setup.BROKER][bumps_celery_setup.STRING] = dctStrings[bumps_celery_setup.BROKER]
        #dct[bumps_celery_setup.BACKEND][bumps_celery_setup.STRING] = dctStrings[bumps_celery_setup.BACKEND]
    except Exception as e:
        dir = f'{e}'
    finally:
        if f:
            f.close()
    return dct
#------------------------------------------------------------------------------
def add_connection_strings(dct):
    try:
        dctStrings = bumps_celery_setup.get_servers_string_from_dict(dct)
        dct[bumps_celery_setup.BROKER][bumps_celery_setup.STRING] = dctStrings[bumps_celery_setup.BROKER]
        dct[bumps_celery_setup.BACKEND][bumps_celery_setup.STRING] = dctStrings[bumps_celery_setup.BACKEND]
    except Exception as e:
        print(f'add_connection_strings runtime error:\n{e}')
    return dct
#------------------------------------------------------------------------------
@app.route('/celery_params')
def show_celery_params():
    dct_servers = read_servers()
    #dctStrings = bumps_celery_setup.get_servers_string_from_dict(dct_servers)
    #dct_servers[bumps_celery_setup.BROKER][bumps_celery_setup.STRING] = dctStrings[bumps_celery_setup.BROKER]
    #dct_servers[bumps_celery_setup.BACKEND][bumps_celery_setup.STRING] = dctStrings[bumps_celery_setup.BACKEND]
    return render_template('bumps_celery_setup.html', servers=dct_servers)
#------------------------------------------------------------------------------
@app.route('/read_celery_params')
def read_celery_params():
    strServers = str(read_servers()).lower()
    return strServers
#------------------------------------------------------------------------------
def get_cli_params():
    bumps_params = BumpsParams()
    try:
        options, remainder = getopt.getopt(sys.argv[1:],
            's:p:m:hv',
            [
            'server=',
            'host=',
            'port=',
			'mp_port=',
			'help',
            'view'
            ])
    except Exception as e:#getopt.GetoptError as err:
        #print(err)
        print(f'runtime error: {e}')
        exit(1) 
    for opt, arg in options:
        #if opt in ('-h', '--host'):
        if opt in ('-s', '--server', '--host'):
            bumps_params.server = arg.strip();
        elif opt in ('-p', '--port'):
            bumps_params.port = int (arg.strip())
        elif opt in ('-m', '--mp_port'):
            bumps_params.mp_port = int (arg.strip())
        elif opt in ('-h', '--help'):
            bumps_params.is_help = True
        elif opt in ('-v', '--view'):
            bumps_params.verify = True
    return bumps_params
#------------------------------------------------------------------------------
def print_usage():
    print(f'Usage:\n\
        python {__file__} [options]\n\
        options:\n\
            -s, --server  - flask server name or ip address\n\
                --host      default: localhost\n\
            -p, --port    - flask server port\n\
                            default: 5000\n\
            -m, --mp_port - multiprocessing port (multiprocessing server is the same is flask server)\n\
                            defaults: 4567\n\
            -h, --help    - print this list\n\
            -v, --verify  - verify bumps parameters\
        ')
#------------------------------------------------------------------------------
def main():
    global bumps_params
    bumps_params = get_cli_params()        
    if bumps_params.is_help:
        print_usage()
        exit(0)
    elif bumps_params.verify:
        if not bumps_params.verify_params():
            print('No!\nincorrect parameters. quitting')
            exit(0)
        else:
            print('\n')
    pServer = multiprocessing.Process(name='bumps websockets server', target=ws_server_main, args=(bumps_params.server, bumps_params.mp_port, os.getcwd()))
    pServer.start()
    print('server started')
    #app.run(debug=False, host=bumps_params.server, port=bumps_params.port)
    app.run(debug=True, host=bumps_params.server, port=bumps_params.port)
    pServer.terminate()
    print('server terminated')
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
    exit(0)
