import asyncio
import websockets
import sys, getopt
import readchar
from random_word import RandomWords
import datetime
from MessageCommand import MessageCommand
#------------------------------------------------------------------------------
def name_of_algorithm(algorithm):
    if algorithm:
        loalg = algorithm.lower()
    else:
        loalg = ""
    if loalg == "lm":
        alg_name = "Levenberg Marquardt"
    elif loalg == "newton":
        alg_name = "Quasi-Newton BFGS"
    elif loalg == "de":
        alg_name = "Differential Evolution"
    elif loalg == "dream":
        alg_name = "DREAM"
    elif loalg == "amoeba":
        alg_name = "Nelder-Mead Simplex"
    elif loalg == "pt":
        alg_name = "Parallel Tempering"
    elif loalg == "ps":
        alg_name = "Particle Swarm"
    elif loalg == "rl":
        alg_name = "Random Lines"
    else:
        alg_name = "unknown"
    return alg_name
#------------------------------------------------------------------------------
def read_y_n():
    byte = readchar.readchar()
    if (type(byte) is str) == False:
        c = byte.decode('utf-8')
    else:
        c = byte
    ret = not (c == 'n')
    return ret
#------------------------------------------------------------------------------
class MessageParams:
    server      = 'localhost'
    port        = 5678
    algorithm   = 'lm'
    steps       = 100
    burn        = 100
    tag         = None
    files_names = []
    problem     = None
    check_params = True
    is_help      = False
#------------------------------------------------------------------------------
    def __init__(self):
        r = RandomWords()
        self.tag = r.get_random_word()
#------------------------------------------------------------------------------
    def set_algorithm (self, alg_abrv):
        allowed_abvr = ["lm", "newton", "de", "dream", "amoeba", "pt", "ps", "rl"]
        if alg_abrv.lower() in allowed_abvr:
            self.algorithm = alg_abrv
        else:
            raise Exception (f'unknown algorithm abbreviation {alg_abrv}')
#------------------------------------------------------------------------------
    def print_params(self):
        print(f'server: {self.server}')
        print(f'port: {self.port}')
        print(f'algorithm: {name_of_algorithm(self.algorithm)}')
        print(f'steps: {self.steps}')
        print(f'burn: {self.burn}')
        print(f'tag: {self.tag}')
        print(f'file_name: {self.files_names}')
        print(f'problem: {self.problem}')
        print(f'Check parameters: {self.check_params}')
#------------------------------------------------------------------------------
    def add_files(self, new_files):
        self.files_names += new_files
#------------------------------------------------------------------------------
    def params_ok(self):
        self.print_params()
        print('Are you ok with the parameters ([y]/n)?', end=' ')
        sys.stdout.flush()
        return read_y_n()
#------------------------------------------------------------------------------
    def read_problem_file(self):
        problem = ''
        f = None
        try:
            f = open(self.files_names[0], 'r')
            problem = f.read()
        except Exception as e:
            print(f'Error reading problem file: "{e}"')
        finally:
            if f:
                f.close()
        return problem
#------------------------------------------------------------------------------
    def compose_params(self):
        params = {}
        try:
            params['algorithm'] = self.algorithm
            params['steps']     = self.steps
            params['burn']      = self.burn
        except Exception as e:
            print(f'Error in compose_params: "{e}"')
        return params
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class BumpsMessage:
    header = 'bumps client'
    params = None
#------------------------------------------------------------------------------
    def __init__(self):
        params = MessageParams()
#------------------------------------------------------------------------------
    def compose_message(self, message_params):
        message = {}
        message['header'] = self.header
        message['tag']    = message_params.tag
        return message
#------------------------------------------------------------------------------
async def test():
   async with websockets.connect('ws://0.0.0.0:5678') as websocket:
        await websocket.send("hello")
        response = await websocket.recv()
        print(response)
#------------------------------------------------------------------------------
async def send_fit_command(message, message_params):
    try:
        remote_address = f'ws://{message_params.server}:{message_params:port}'
        print(f'sending to address "{remote_address}"')
        async with websockets.connect(remote_address) as websocket:
    #async with websockets.connect('ws://0.0.0.0:5678') as websocket:
        await websocket.send("hello")
        response = await websocket.recv()
        print(response)
    except Exception as e:
        print(f'"Error in send_fit_command": {e}')
#------------------------------------------------------------------------------
def get_cli_name():
    file_name = None
    try:
        options, remainder = getopt.getopt(sys.argv[1:],
            'f:',
            ['file='])
    except getopt.GetoptError as err:
        print(err) 
        #exit(1)
    for opt, arg in options:
        if opt in ('-f', '--file'):
            file_name = arg.strip();
    return file_name
#------------------------------------------------------------------------------
def read_file(file_name):
    content = None
    try:
        f = open(file_name, "r")
        content = f.read()
        f.close()
    except Exception as e:
        print('Error in "read_file": "{e}"')
    return content
#------------------------------------------------------------------------------
def is_help_params(sys_argv):
    is_help = False
    try:
            options, remainder = getopt.getopt(sys.argv[1:],
                's:p:a:t:yh',
                ['server=',
                 'port=',
                 'tag=',
                 'steps=',
                 'burn=',
                 'help',
                 'algorithm='])
#        options = getopt.getopt(sys_argv,
#            'h?',
#            ['help'])
    except getopt.GetoptError as err:
        print(err) 
        exit(1)
    for opt, arg in options:
        if opt in ('-h', '?', '--help'):
            is_help = True
    return is_help
#------------------------------------------------------------------------------
def print_usage():
    src_filename = __file__
    src_filename.replace('.','')
    src_filename.replace('/','')
    src_filename.replace('\\','')
    print(f'file: {__file__}, source file: {src_filename}')
    print('Usage\n\
        python send_job.py [options] problem_file1(s)\n\
        Note: problem files may include wild card, e.g. "curv_fit*.py"\n\
        \n\
        options:\n\
        --server    Server name or server IP address.\n\
          Default   localhost\n\
        ------------\n\
        --port      Server port used for websockets.\n\
          default   4567\n\
        ------------\n\
        --algorithm Optimization algorithm. Possible options include:\n\
            "lm"     (Levenberg Marquardt)\n\
            newton"  (Quasi-Newton BFGS)\n\
            "de"     (Differential Evolution)\n\
            "dream"  (DREAM)\n\
            "amoeba" (Nelder-Mead Simplex)\n\
            "pt"     (Parallel Tempering)\n\
            "ps"     (Particle Swarm)\n\
            "rl"     (Random Lines)\n\
        ------------\n\
        --steps      Maximum number of iterative steps\n\
        ------------\n\
        --burn       number of burn-in iterations before accumulating stats\n\
        ')
#------------------------------------------------------------------------------
def params_from_command_line():
    message_params = MessageParams()
    try:
        options, remainder = getopt.getopt(sys.argv[1:],
            's:p:a:t:yh?',
            ['server=',
                'port=',
                'tag=',
                'steps=',
                'burn=',
                'help',
                'algorithm='])
    except getopt.GetoptError as err:
        print(err) 
        exit(1)
    for opt, arg in options:
        if opt in ('-s', '--server'):
            message_params.server = arg.strip()
        elif opt in ('-p', '--port'):
            message_params.port = int(arg.strip())
        elif opt in ('-a', '--algorithm'):
            message_params.set_algorithm (arg.strip())
        elif opt in ('--steps'):
            message_params.step = int(arg.strip())
        elif opt in ('--burn'):
            message_params.burn = int(arg.strip())
        elif opt in ('-t','--tag'):
            message_params.tag = arg.strip()
        elif opt in ('-y'):
            message_params.check_params = False
        elif opt in ('-h', '--help'):
            message_params.is_help = True
    message_params.add_files(remainder)
    return message_params
#------------------------------------------------------------------------------
import datetime
def get_message_time():
    try:
        now = datetime.datetime.utcnow()
        message_time = {}
        message_time['year'] =        now.strftime('%Y')
        message_time['month']        = now.strftime('%m')
        message_time['date']         = now.strftime('%d')
        message_time['hour']         = now.strftime('%H')
        message_time['minutes']      = now.strftime('%M')
        message_time['seconds']      = now.strftime('%S')
        message_time['milliseconds'] = now.strftime('%f')
    except Exception as e:
        print(f'Error in get_message_time: {e}')
        message_time = {}
    return message_time
#------------------------------------------------------------------------------
def compose_fit_message(message_params):
    message = {}
    message['header'] = 'bumps client'
    message['tag']    = message_params.tag
    message['message_time'] = get_message_time()
    message['command'] = str(MessageCommand.StartFit)
    message['fit_problem'] = message_params.read_problem_file()
    message['problem_file'] = message_params.files_names[0]
    message['params'] = message_params.compose_params()
    return message
#------------------------------------------------------------------------------
def main():
    message_params = params_from_command_line()
    if message_params.is_help:
        print_usage()
        exit(0)
    if message_params.check_params:
        if not message_params.params_ok():
            print('Problem with parameters. Aborting')
            exit(0)
    print('\nsending fit job')
    sys.stdout.flush()
    message = compose_fit_message(message_params)
    print(f'Message:\n{message}')
    asyncio.run(send_fit_command(message, message_params))

    exit(0)
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
    file_name = get_cli_name()
    if file_name:
        message = read_file(file_name)
        if message:
            print(f'Message read from file:\n==========\n{message}\n==========\n')
            f = open('outmsg.txt', 'w+')
            f.write(message)
            f.close()


    print(f'File name: "{file_name}"')
#asyncio.get_event_loop().run_until_complete(test())