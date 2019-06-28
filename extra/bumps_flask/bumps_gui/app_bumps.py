from flask import Flask, render_template, request
from bumps_params import BumpsParams
import json, sys, getopt, os, multiprocessing
from bumps_ws_server import ws_server_main
from bumps_params import read_y_n
#------------------------------------------------------------------------------
# Source:
# https://stackoverflow.com/questions/40963401/flask-dynamic-data-update-without-reload-page
app = Flask(__name__)
#------------------------------------------------------------------------------
@app.route('/onsendfitjob')
def on_send_fit_job():
    res = {}
    try:
        res = request.args['message']
#        print(f'res:\n---------------\n{res}\n-------------------\n')
#        print(f'type(res): {type(res)}')
        cm = json.loads(res)
#        print(f'cm = {cm}')
#        print(f'type(cm): {type(cm)}')
#        for key in cm.keys():
#            print(f'\t{key}:\t{cm[key]}')
    except Exception as e:
        print (f'run time error in on_send_fit_job: {e}')
    return json.dumps(res)
#------------------------------------------------------------------------------
@app.route('/')
def index():
        return render_template('bumps_mp_gui.html')
#------------------------------------------------------------------------------
def get_cli_params():
    bumps_params = BumpsParams()
    try:
        options, remainder = getopt.getopt(sys.argv[1:],
            's:p:m:hv',
            [
            'server=',
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
        if opt in ('-s', '--server'):
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
                            default: localhost\n\
            -p, --port    - flask server port\n\
                            default: 5000\n\
            -m, --mp_port - multiprocessing port (multiprocessing server is the same is flask server)\n\
                            defaults: 4567\n\
            -h, --help    - print this list\n\
            -v, --verify  - verify bumps parameters\
        ')
#------------------------------------------------------------------------------
def main():
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
    flask_dir = os.getcwd() + '/static/'
    pServer = multiprocessing.Process(name='bumps websockets server', target=ws_server_main, args=(bumps_params.server, bumps_params.mp_port,flask_dir))
    pServer.start()
    app.run(debug=False, host=bumps_params.server, port=bumps_params.port)
    print('server started')
    read_y_n()
    pServer.terminate()
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
    exit(0)
