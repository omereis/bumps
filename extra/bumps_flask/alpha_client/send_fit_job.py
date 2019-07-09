import asyncio, websockets, json
import os, sys, getopt
import readchar, sqlite3
#from random_word import RandomWords
from client_params import MessageParams
import datetime
from MessageCommand import MessageCommand
#------------------------------------------------------------------------------
tbl_sent_jobs   = 't_sent_jobs'
fld_id      = 'local_id'
fld_server  = 'server_id'
fld_problem = 'problem_file'
fld_tag     = 'tag'
fld_sent    = 'sent_time'
fld_status  = 'status'
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
            local_id        some client generated id that uniqueuely identifies the job for the client.\n\
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
        python send_fit_job.py [options] problem_file1(s)\n\
        Note: problem files may include wild card, e.g. "curv_fit*.py"\n\
        \n\
        options:\n\
        --server    Server name or server IP address.\n\
          Default   localhost\n\
        ------------\n\
        --port      Server port used for websockets.\n\
          default   4567\n\
        ------------\n\
        --command   The command to be sent to the Fit Server. it can be only one of the following:\n\
                    send   - Send fit job(s) with the specified parameters and problem files. \n\
                    local   - List all local jobs and their status. The list is taken from the local database\n\
                              rather then the server.\n\
                              For update from the Fit Server use "status" command.\n\
                    status - Find jobs status on the Fit Server memory, for a given tag. If no tag is giver,\n\
                             then all tags from the local database are queried\n\
                    server - Display jobs from the server database for given tags.\n\
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
                's:p:a:t:c:yh?',
                ['server=',
                    'host=',
                    'port=',
                    'tag=',
                    'steps=',
                    'burn=',
                    'command=',
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
            elif opt in ('-c','--command'):
                if not message_params.set_command (arg.strip()):
                    print(f'Unknown command: {arg.strip()}.\nAborting')
                    exit(1)
                #message_params.command = arg.strip()
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
    global tbl_sent_jobs, fld_id, fld_problem, fld_tag, fld_sent, fld_status

    try:
        sql = f'create table if not exists {tbl_sent_jobs} (\
            {fld_id}        integer,\
            {fld_server}    integer,\
            {fld_problem}    varchar(100),\
            {fld_tag}       varchar(100),\
            {fld_status}    varchar(25),\
            {fld_sent}       datetime);'
        sql = sql.replace('  ', ' ')
        conn.execute(sql)
    except Exception as e:
        print(f'"assert_jobs_table" runtime error: {e}')
        exit(1)
#------------------------------------------------------------------------------
def open_local_db():
    conn = sqlite3.connect('sent_jobs.db')
    assert_jobs_table(conn)
    return conn
#------------------------------------------------------------------------------
def get_next_local_id():
    global tbl_sent_jobs, fld_id, fld_server, fld_problem, fld_sent

    try:
        conn = open_local_db()#sqlite3.connect('sent_jobs.db')
        #assert_jobs_table(conn)
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
def update_server_id (tag, local_id, server_id):
    global tbl_sent_jobs, fld_id, fld_server, fld_tag, fld_problem, fld_sent

    try:
        conn = open_local_db()
        sql = f'update {tbl_sent_jobs} set {fld_server}={server_id} where {fld_id}={local_id} and {fld_tag}="{tag}";'
        conn.execute(sql)
        conn.commit()
    except Exception as e:
        print(f'"update_server_id" runtime error: {e}')
    finally:
        conn.close()
#------------------------------------------------------------------------------
def update_sent_jobs_db(tag, local_id, results):
    results_str = results.replace("'",'"')
    json_results = json.loads(results_str)
    print(f'json_results: {json_results}')
    server_id = json_results['params'][local_id]
    print(f'json_results: {json_results}')
    update_server_id (tag, local_id, server_id)
#------------------------------------------------------------------------------
def save_local_message(message):
    global tbl_sent_jobs, fld_id, fld_server, fld_tag, fld_problem, fld_sent

    try:
        conn = open_local_db()
#        msg_keys = list(message.keys())
        file_name = get_dict_value (message, 'problem_file', '')
        local_id  = get_dict_value (message, 'local_id')
        tag       = get_dict_value (message, 'tag')
        #sql = f'insert into {tbl_sent_jobs} ({fld_id}) values(1);'
        sql = f'insert into {tbl_sent_jobs} ({fld_id}, {fld_problem}, {fld_tag}, {fld_sent})\
                values \
            ({local_id}, "{file_name}", "{tag}", "{str(datetime.datetime.now())}");'
        conn.execute(sql)
        conn.commit()
    except Exception as e:
        print(f'"save_local_message" runtime error: {e}')
    finally:
        conn.close()
#------------------------------------------------------------------------------
def create_message_header(message_params):
    message = {}
    message['header'] = 'bumps client'
    #message['tag']    = message_params.tag
    message['message_time'] = get_message_time()
    return message
#------------------------------------------------------------------------------
def compose_fit_message(message_params, idx=0):
    message = create_message_header(message_params)
    message['tag']    = message_params.get_new_tag()
    message['command'] = 'StartFit'
    message['fit_problem'] = message_params.read_problem_file(idx)
    message['problem_file'] = message_params.files_names[idx]
    message['params'] = message_params.compose_params()
    message['multi_processing'] = 'none'
    message['local_id'] = get_next_local_id()
    return message
import websocket
#------------------------------------------------------------------------------
def send_fit_job (message_params):
    remote_address = message_params.get_remote_address()
    try:
        for n in range(len(message_params.files_names)):
            ws = websocket.create_connection(remote_address)
            message = compose_fit_message(message_params, n)
            save_local_message(message)
            ws.send(str(message))
            print('\nmessage sent')
            local_id = str(message["local_id"])
            tag      = message["tag"]
            results = ws.recv()
            print(f'\nreply recieved: {results}')
            update_sent_jobs_db(tag, local_id, results)
            ws.close()
    except Exception as e:
        print(f'"main" runtime error: {e}')
#------------------------------------------------------------------------------
def show_local_jobs():
    print('local command')
#------------------------------------------------------------------------------
def load_tags_from_db ():
    global tbl_sent_jobs, fld_tag

    tags = []
    try:
        conn = open_local_db()
        sql = f'select distinct {fld_tag} from {tbl_sent_jobs};'
        records = conn.execute(sql)
        for rec in records:
            tags.append(rec[0])
    except Exception as e:
        print(f'"load_tags_from_db" runtime error: {e}')
    finally:
        conn.close()
    return tags
#------------------------------------------------------------------------------
def update_jobs_server_status (params):
    global tbl_sent_jobs, fld_id, fld_problem, fld_tag, fld_sent, fld_status, fld_server

    conn = open_local_db()
    for x in params:
        server_id     = x['job_id']
        server_status = x['job_status']
        sql = f'update {tbl_sent_jobs} set {fld_status}="{server_status}" where {fld_server}={server_id};'
        conn.execute(sql)
    conn.commit()
    conn.close()
#------------------------------------------------------------------------------
def create_query_server_message(message_params):
    message = create_message_header(message_params)
    message['command'] = 'GetDbStatus'
    message['tag'] = message_params.tag
    return message
#------------------------------------------------------------------------------
def show_jobs_on_server(message_params):
    message = create_query_server_message(message_params)
    print(f'"show_jobs_on_server", message:\n{message}')
    readchar.readchar()
    remote_address = message_params.get_remote_address()
    ws = websocket.create_connection(remote_address)
    ws.send(str(message))
    results = ws.recv()
    print(f'server jobs:\n{results}')
#------------------------------------------------------------------------------
def compose_status_message(message_params):
    message = create_message_header(message_params)
    message['command'] = 'GetStatus'
    return message
#------------------------------------------------------------------------------
def show_jobs_status(message_params):
    try:
        tags=[]
        server_job_status = []
        remote_address = message_params.get_remote_address()
        message = compose_status_message(message_params)
        if message_params.tag:
            tags.append(message_params.tag)
        else:
            tags = load_tags_from_db ()
        for tag in tags:
            ws = websocket.create_connection(remote_address)
            message['tag'] = tag
            ws.send(str(message))
            results = ws.recv()
            print(f'reply received: {results}')
            ws.close()
            reply_msg = json.loads(results.replace("'",'"'))
            params = reply_msg['params']
            for p in params:
                server_job_status.append(p)
            print('connection closed')
    except Exception as e:
        print(f'"show_jobs_status", runtime error: {e}')
    finally:
        if 'params' in locals():
            update_jobs_server_status (params)
        else:
            print('no status retrieved')
        for x in server_job_status:
            print(f"{x['job_id']}: {x['job_status']}")
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
    sys.stdout.flush()
    if message_params.is_send_command():
        print(f'message command: {message_params.command}')
        send_fit_job (message_params)
    elif message_params.is_local_command():
        show_local_jobs()
    elif message_params.is_status_command():
        show_jobs_status(message_params)
    elif message_params.is_server_command():
        show_jobs_on_server(message_params)
    exit(0)
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
