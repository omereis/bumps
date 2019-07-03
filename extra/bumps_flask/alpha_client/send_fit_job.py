import asyncio, websockets
import os, sys, getopt
import readchar, sqlite3
from random_word import RandomWords
import datetime
from MessageCommand import MessageCommand
#------------------------------------------------------------------------------
tbl_sent_jobs   = 'sent_jobs'
fld_id      = 'local_id'
fld_server  = 'server_id'
fld_problem = 'problem_file'
fld_tag     = 'tag'
fld_sent    = 'sent_time'

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
#            fname = os.getcwd() + "/" + self.files_names[0]
#            f = open(fname, 'r')
            f = open(self.files_names[0], 'r')
            problem = f.read()
        except Exception as e:
            print(f'Error reading problem file: "{e}"')
#            exit(1)
        finally:
            if f:
                f.close()
        if len(problem) == 0:
            print('Missing problem definition. Aborting')
            exit(1)
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
    def get_remote_address(self):
        remote_address = f'ws://{self.server}:{self.port}'
        return remote_address
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
    for v in sys.argv[1:]:
        if (v.startswith('--')) and not ('=' in v):
            if 'help' in (v):
                return True
        elif (v.startswith('-')) and not ('=' in v):
            if v == '-h':
                return True
        elif v == '?':
            return True
    return False
#------------------------------------------------------------------------------
def print_usage2():
    print(f'Usage\n\
        python {__file__} [options] --params <parameters file> problem_file[,problem_file,...]\n\
        parameters file is a JSON format, that should include the following fields.\n\
        Note that all fields must be enclose in double quotes, such as "field": "value"\n\
            server  Fitter server name or ip.\n\
                    default: localhost\n\
            port    Fitter port used for the websocket service\n\
                    default: 4567\n\
            options\n\
                -h | --help |-?     print this message\n\
                -v                  print parsed parameters, and request approval\n\
            command Fitter  case sensitive command. Can be only one of the following:\n\
                StartFit    Start fit\n\
                GetStatus   Return status for job, identified by the message tag.\n\
                Delete      Delete results a database record for jobs identified by id, in params field\n\
                get_data    Retrieve file names (URLs) for the files resulted from the fitting algorithm.\n\
                            Note that one of the files is an archive (zip) that encapsulate all the results files.\n\
                print_status    print jobs status on server console. Used mainly during development.\n\
            params:         parameters field. In case of StartFit command, this field should include the following dict:\n\
                algorithm   fitting algorithm. Possible options include:\n\
                    "lm"     (Levenberg Marquardt)\n\
                    newton"  (Quasi-Newton BFGS)\n\
                    "de"     (Differential Evolution)\n\
                    "dream"  (DREAM)\n\
                    "amoeba" (Nelder-Mead Simplex)\n\
                    "pt"     (Parallel Tempering)\n\
                    "ps"     (Particle Swarm)\n\
                    "rl"     (Random Lines)\n\
                steps       number of steps\n\
                burns       number of burns\n\
            multi_processing    may by "none", "celery" or "slurm"\n\
            row_id          some client generated id that uniqueuely identifies the job for the client.\n\
                            The server returns uniqueue database id, for each job.\n\
                            The client should bind the database id to the local id\n')
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
        --burn         number of burn-in iterations before accumulating stats\n\
        --view      display the parsed message\n\
        ')
#------------------------------------------------------------------------------
def params_from_command_line():
    message_params = MessageParams()
    message_params.is_help = is_help_params(sys.argv[1:])
    if not message_params.is_help:
        try:
            options, remainder = getopt.getopt(sys.argv[1:],
                's:p:a:t:yh?',
                ['server=',
                    'host=',
                    'port=',
                    'tag=',
                    'steps=',
                    'burn=',
                    'algorithm='])
        except getopt.GetoptError as err:
            print(err) 
            exit(1)
        for opt, arg in options:
            if opt in ('-s', '--server', '--host'):
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
def assert_jobs_table(conn):
    global tbl_sent_jobs, fld_id, fld_problem, fld_tag, fld_sent

#    sql = "select name from SQLITE_MASTER where type='table' and name = '{tbl_sent_jobs}';"
#    print(f'"assert_jobs_table", sql:\n{sql}')
#    res = conn.execute(sql).fetchall())
#    print(f'"assert_jobs_table", len(res):\n{len(res)}')
#    if len(conn.execute(sql).fetchall()) == 0:
    try:
        sql = f'create table if not exists {tbl_sent_jobs} (\
            {fld_id}        integer,\
            {fld_server}    integer,\
            {fld_problem}    varchar(100),\
            {fld_tag}       varchar(100),\
            {fld_sent}       datetime);'
        conn.execute(sql)
    except Exception as e:
        print(f'"assert_jobs_table" runtime error: {e}')
        exit(1)
#------------------------------------------------------------------------------
def open_local_db():
    return sqlite3.connect('sent_jobs.db')
#------------------------------------------------------------------------------
def get_next_local_id():
    global tbl_sent_jobs, fld_id, fld_server, fld_problem, fld_sent

    try:
        conn = open_local_db()#sqlite3.connect('sent_jobs.db')
        assert_jobs_table(conn)
        sql = f'select max ({fld_id}) from {tbl_sent_jobs};'
        mx = conn.execute(sql).fetchall()
        if mx[0][0] == None:
            db_id = 0
        else:
            db_id = int(mx[0][0])
    except Exception as e:
        print(f'get_next_local_id, runtime error: {e}')
    finally:
        conn.close()
    return db_id + 1
#------------------------------------------------------------------------------
def get_dict_value (source, key, default_value=None):
    src_keys = list(source.keys())
    if key in src_keys:
        value = source[key]
    else:
        value = default_value
    return value

#------------------------------------------------------------------------------
def save_local_message(message):
    global tbl_sent_jobs, fld_id, fld_server, fld_tag, fld_problem, fld_sent

    try:
        conn = open_local_db()
#        msg_keys = list(message.keys())
        file_name = get_dict_value (message, 'problem_file', '')
        local_id  = get_dict_value (message, 'row_id')
        tag       = get_dict_value (message, 'tag')
        sql = f'insert into {tbl_sent_jobs} ({fld_id}, {fld_problem}, {fld_tag}, {fld_sent})\
                values \
            ({local_id}, {file_name}, {tag}, {str(datetime.datetime.now())});'
        conn.execute(sql)
    except Exception as e:
        print(f'"save_local_message" runtime error: {e}')
    finally:
        conn.close()
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
    message['multi_processing'] = 'none'
    message['row_id'] = get_next_local_id()
    return message
import websocket
#------------------------------------------------------------------------------
def main():
# 1. get parameters: server, instruction, problem files
# 2.
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
    save_local_message(message)
    #print(f'Message:\n{message}')
    #websocket.enableTrace(True)
    remote_address = message_params.get_remote_address()
    #ws = websocket.create_connection("ws://echo.websocket.org/")
    #ws = websocket.create_connection(message_params.get_remote_address())
    try:
        ws = websocket.create_connection(remote_address)
        ws.send(str(message))
        print(f'message sent:\n\
            local ID: {message["row_id"]})\n\
            Tag:      {message["tag"]}')
        results = ws.recv()
        print (f'results: {results}')
    except Exception as e:
        print(f'"main" runtime error: {e}')
    finally:
        ws.close()
    exit(0)
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
#    file_name = get_cli_name()
#    if file_name:
#        message = read_file(file_name)
#        if message:
#            print(f'Message read from file:\n==========\n{message}\n==========\n')
#            f = open('outmsg.txt', 'w+')
#            f.write(message)
#            f.close()


#    print(f'File name: "{file_name}"')
#asyncio.get_event_loop().run_until_complete(test())
# 4:51 pm