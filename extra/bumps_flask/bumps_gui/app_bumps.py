from flask import Flask, render_template, request
from bumps_params import BumpsParams
import json, sys, getopt, os, multiprocessing
from bumps_ws_server import ws_server_main
from bumps_params import read_y_n
import websocket
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
#        print(f'cm = {cm}')
#       print(f'Message:\n{msg}')
#        print('++++++++++++++++++++++++++++++++++++++++++++++')
#        print(f'bumps parameters:\n{bumps_params.to_string()}')
#        print('++++++++++++++++++++++++++++++++++++++++++++++')
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
@app.route('/test_celery')
def test_celery():
    suggestions_list = []
    suggestions_list.append('try it!')
    return 'Here are Celery results'
    #return render_template('suggestions.html', suggestions=suggestions_list)
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
