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
#        print ('websocket connected')
        ws.send(msg)
        ret = ws.recv()
        ws.close()
#        print (f'websocket disconnected, return value: {ret}')
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
    print(f'test_rabbit, rabbit string: {strRabbit}')
    fRabbit = False
    sResult = ''
    try:
        #print_debug(str(dir(request)))
        con = pika.BlockingConnection(pika.ConnectionParameters(strRabbit))
        con.close()
        fRabbit = True
        sResult = 'RabbitMQ OK'
    except Exception as e:
        fRabbit = False
        print(f'"test_rabbit" runtime error:\n{e}')
        sResult = f'{e}'
    lstResult[0] = sResult
    return (fRabbit)
#------------------------------------------------------------------------------
def test_redis(strRedis):
    print(f'test_redis, redis string: {strRedis}')
    return (False)
#------------------------------------------------------------------------------
def test_broker_setup(dictSetup, dictResults):
    try:
        strBroker = dictSetup[bumps_celery_setup.ADDRESS]
        lstResult = ['0']
        if dictSetup[bumps_celery_setup.TYPE] == bumps_celery_setup.RABBIT:
            if test_rabbit(strBroker, lstResult):
                fTest = "1"
            else:
                fTest = "0"
            sResult = lstResult[0]
        elif dictSetup[bumps_celery_setup.TYPE] == bumps_celery_setup.REDIS:
            fTest = test_redis(strBroker)
            sResult = 'Redis OK'
        else:
            fTest = "0"
            sResult = f'Type "{dictSetup[bumps_celery_setup.TYPE]}" not supported'
    except Exception as e:
        print(f'Test Broker Setup runtime error:\n{e}')
        fTest = "0"
        sResult = f'Broker Setup runtime error:\n{e}'
    finally:
        dictResults['result'] = fTest
        dictResults['message'] = sResult
    return sResult
#------------------------------------------------------------------------------
@app.route('/test_broker')
def test_broker():
    dictResults = {}
    try:
        client_args = request.args.to_dict()['jsdata']
        #print_debug(f'request args:\n{str(request.args)}')
        #print_debug(f'request args content:\n{request.args[0][1]}')
        #dctArgs = request.args.to_dict()
        #print_debug(f'request dictionary:\n{str(dctArgs)}')
        print_debug(f'request jsdata:\n{client_args}')
        jsonArgs = json.parse(client_args)
        jsonSetup = bumps_celery_setup.read_setup()
        print_debug(f'jsonArgs:\n{str(jsonArgs)}')
        print_debug(f'jsonSetup:\n{str(jsonSetup)}')
        #print(f'test_broker, jsonSetup: {str(jsonSetup)}')
        #jsonServers = bumps_celery_setup.get_servers_string()
        #print(f'test_broker, jsonServers: {str(jsonServers)}')
        fBrokerTest = test_broker_setup(jsonSetup[bumps_celery_setup.BROKER], dictResults)
        #appTest = celery.appTest(jsonServers)
        #dictResults['results'] = 'OK'
        #dictResults['message'] = 'Suceess'
    except Exception as e:
        print (f'Broker testing run time error:\n{e}')
        dictResults['results'] = False
        dictResults['message'] = f'{e}'
    #appTest.start()
    return str(dictResults)
    #return jsonServers
#------------------------------------------------------------------------------
@app.route('/test_celery')
def test_celery():
    jsonServers = bumps_celery_setup.get_servers_string()
    appTest = celery.appTest(jsonServers)
    #appTest.start()
    return jsonServers
#------------------------------------------------------------------------------
def read_servers():
    dir = {}
    f = None
    try:
        f = open ('bumps_celery/bumps_celery_servers.json', 'r')
        s = f.read()
        dir = json.loads(s.replace("'",'"'))
    except Exception as e:
        dir = f'{e}'
    finally:
        if f:
            f.close()
    return dir
#------------------------------------------------------------------------------
@app.route('/celery_params')
def show_celery_params():
    dir_servers = read_servers()
    return render_template('bumps_celery_setup.html', dir=dir_servers)
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
    app.run(debug=False, host=bumps_params.server, port=bumps_params.port)
    pServer.terminate()
    print('server terminated')
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
    exit(0)
