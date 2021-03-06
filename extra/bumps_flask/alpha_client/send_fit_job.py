import asyncio, websockets, json, websocket
import os, sys, getopt, tabulate
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
                    send <file>[,<file>...]\n\
                        Send fit job(s) with the specified parameters and problem files. \n\
                    local   - List all local jobs and their status. The list is taken from the local database\n\
                              rather then the server.\n\
                              For update from the Fit Server use "status" command.\n\
                    status - Find jobs status on the Fit Server memory, for a given tag. If no tag is given,\n\
                             then all tags from the local database are queried\n\
                    server - Display jobs from the server database for given tags.\n\
                    data <tag> - Retrieve archived results for completed jobs.\n\
                    tags\n\
                        Display all distinct tags in the database\n\
                    delete <job_id>[,<job_id>,...]\n\
                        Delete jobs from the server disk, the server database and local database\n\
                            Note: local files will not be deleted\n\
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
        -------------\n\
        --multi     Multiprocessing\n\
          default   none\n\
          "celery"  Use Celery queue management\n\
        ')
#------------------------------------------------------------------------------
def params_from_command_line():
    message_params = MessageParams()
    message_params.is_help = is_help_params(sys.argv[1:])
    if not message_params.is_help:
        try:
            options, remainder = getopt.getopt(sys.argv[1:],
                's:p:a:t:m:c:yh?',
                ['server=',
                    'host=',
                    'port=',
                    'tag=',
                    'steps=',
                    'burn=',
                    'command=',
                    'multi=',
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
            elif opt in ('-m','--multi'):
                message_params.multi = arg.strip()
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
    server_id = json_results['params'][local_id]
    update_server_id (tag, local_id, server_id)
#------------------------------------------------------------------------------
def save_local_message(message):
    global tbl_sent_jobs, fld_id, fld_server, fld_tag, fld_problem, fld_sent

    try:
        conn = open_local_db()
        file_name = get_dict_value (message, 'problem_file', '')
        local_id  = get_dict_value (message, 'local_id')
        tag       = get_dict_value (message, 'tag')
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
    message['message_time'] = get_message_time()
    message['multi_processing'] = message_params.get_mp_system()
    return message
#------------------------------------------------------------------------------
def compose_fit_message(message_params, idx=0):
    message = create_message_header(message_params)
    message['tag']    = message_params.get_new_tag()
    message['command'] = 'StartFit'
    message['fit_problem'] = message_params.read_problem_file(idx)
    message['problem_file'] = message_params.files_names[idx]
    message['params'] = message_params.compose_params()
    #message['multi_processing'] = 'none'
    message['local_id'] = get_next_local_id()
    return message
#------------------------------------------------------------------------------
def show_sent_jobs(local_ids):
    global tbl_sent_jobs, fld_id, fld_problem, fld_tag, fld_sent, fld_status, fld_server

    try:
        conn = open_local_db()
        where = []
        for id in local_ids:
            where.append(f'{fld_id}={id}')
        sql_where = " or ".join(where)
        sql = f'select {fld_id}, {fld_server}, {fld_problem}, {fld_tag}, {fld_sent} \
            from {tbl_sent_jobs}  where {sql_where} order by {fld_problem};'
        sent_jobs = conn.execute(sql).fetchall()
        display_jobs = []
        for row in sent_jobs:
            display_jobs.append(list(row))
        print(tabulate.tabulate(display_jobs, headers=['Local ID', 'Server ID', 'File', 'Tag', 'Time & Date'], tablefmt='orgtbl'))
    except Exception as e:
        print(f'"show_sent_jobs" runtime error: {e}')
    finally:
        conn.close()
#------------------------------------------------------------------------------
def send_fit_job (message_params, ws, remote_address):
    local_ids = []
    try:
        for n in range(len(message_params.files_names)):
            if not ws.connected:
                ws.connect(remote_address)
            message = compose_fit_message(message_params, n)
            save_local_message(message)
            ws.send(str(message))
            local_id = str(message["local_id"])
            tag      = message["tag"]
            results = ws.recv()
            update_sent_jobs_db(tag, local_id, results)
            local_ids.append(local_id)
            ws.close()
        show_sent_jobs(local_ids)
    except Exception as e:
        print(f'"send_fit_job" runtime error: {e}')
    finally:
        if ws.connected:
            ws.close()
#------------------------------------------------------------------------------
def show_local_jobs():
    print('local command')
    global tbl_sent_jobs, fld_id, fld_server, fld_problem, fld_tag, fld_sent, fld_status

    try:
        display_jobs = []
        conn = open_local_db()
        sql = f'select {fld_tag},{fld_server},{fld_problem},{fld_tag},{fld_status},{fld_sent} from {tbl_sent_jobs} order by {fld_tag},{fld_server},{fld_status};'
        res = conn.execute(sql).fetchall()
        for row in res:
            display_jobs.append(list(row))
        print(tabulate.tabulate(display_jobs, headers=['Tag', 'Server ID', 'File', 'Tag', 'Status', 'Time & Date'], tablefmt='orgtbl'))
    except Exception as e:
        print(f'get_next_local_id, runtime error: {e}')
    finally:
        conn.close()
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
    try:
        for x in params:
            server_id     = x['job_id']
            server_status = x['job_status']
            sql = f'update {tbl_sent_jobs} set {fld_status}="{server_status}" where {fld_server}={server_id};'
            conn.execute(sql)
        conn.commit()
    except Exception as e:
        print(f'"update_jobs_server_status" runtime error: {e}')
    finally:
        conn.close()
#------------------------------------------------------------------------------
def create_query_server_message(message_params):
    message = create_message_header(message_params)
    message['command'] = 'GetDbStatus'
    message['tag'] = message_params.tag
    return message
#------------------------------------------------------------------------------
def message_reply_to_dict(message):
    try:
        reply = json.loads(message)
    except:
        message = message.replace("'",'"')
        reply = json.loads(message)
    return reply
#------------------------------------------------------------------------------
def item_from_row(row, fmt):
    item = []
    item.append(list(row.values())[0])
    src_time_str = list(row.values())[1]
    dt = datetime.datetime.strptime(src_time_str,fmt)
    time_str = dt.strftime('%H:%M:%S, %b %d, %Y')
    item.append(time_str)
    item.append(list(row.values())[2])
    return item
#------------------------------------------------------------------------------
def show_jobs_on_server(message_params, ws, remote_address):
    results = []
    try:
        message = create_query_server_message(message_params)
        remote_address = message_params.get_remote_address()
        ws = websocket.create_connection(remote_address)
        ws.send(str(message))
        server_results = message_reply_to_dict(ws.recv())
        params = server_results['params']
        for n in range(len(params)):
            if n == 0:
                fmt = list(params[0].values())[0]
            else:
                item = item_from_row(params[n], fmt)
                results.append(item)
    except Exception as e:
        print (f'"show_jobs_on_server" runtime error: {e}')
    finally:
        ws.close()
    print(tabulate.tabulate(results, headers=['Job ID', 'Time & Date', 'Status'], tablefmt='orgtbl'))
    return results
#------------------------------------------------------------------------------
def save_results(key, hex_value):
    bin_content = bytes().fromhex(hex_value)
    zip_name = f'{key}.zip'
    f = open(zip_name, 'wb')
    f.write(bin_content)
    f.close()
    return zip_name
#------------------------------------------------------------------------------
def get_jobs_server_data(message_params, ws, remote_address):
    #if message_params.tag == None:
        #print(f'Missing Tag. Required argument for this command')
        #exit(0)
    try:
        message = create_message_header(message_params)
        message['command'] = 'get_data'
        if message_params.tag:
            message['tag']    = message_params.tag
        else:
            message['tag']    = 'None'
        if not ws.connected:
            ws.connect(remote_address)
        ws.send(str(message))
        server_results = ws.recv()
        server_results = server_results.replace("'",'"')
        json_results = json.loads(server_results)
        params = json_results['params']
        if type(params) is str and params.lower() == 'none':
            print(f'No data found for tag "{message_params.tag}"')
        else:
            for n in range(len(params)):
                item = params[n]
                for key in item.keys():
                    zip_name = save_results(key, item[key])
                    print(f'results file {zip_name} written')
    except Exception as e:
        print(f'"get_jobs_server_data" runtime error: {e}')
    finally:
        if ws.connected:
            ws.close()
#------------------------------------------------------------------------------
def get_server_tags(message_params, ws, remote_address):
    try:
        message = create_message_header(message_params)
        message['command'] = 'get_tags'
        try:
            if not ws.connected:
                ws.connect(remote_address)
        except:
            print(f'Could not create connection to {message_params.get_remote_address()}')
            ws = None
        if ws:
            ws.send(str(message))
            server_results = ws.recv()
            server_results = server_results.replace("'",'"')
            json_results = json.loads(server_results)
            tags = json_results['params']
            for tag in tags:
                print(f'{tag}')
    except Exception as e:
        print(f'"get_server_tags" runtime error: {e}')
    finally:
        if ws:
            ws.close()
#------------------------------------------------------------------------------
def delete_server_jobs(message_params, ws, remote_address):
    global tbl_sent_jobs, fld_server
    try:
        message = create_message_header(message_params)
        message['command'] = 'Delete'
        message['params'] = message_params.files_names
        if not ws.connected:
            ws.connect(remote_address)
        ws.send(str(message))
        server_results = message_reply_to_dict(ws.recv())
        server_ids = server_results['params']
        where=[]
        for id in server_ids:
            where.append(f'{fld_server}={int(id)}')
        where_id = ' or '.join(where)
        conn = open_local_db()
        sql = f'delete from {tbl_sent_jobs} where {where_id};'
        conn.execute(sql)
        conn.commit()
    except Exception as e:
        print(f'"delete_server_jobs" runtime error: {e}')
    finally:
        ws.close()
#------------------------------------------------------------------------------
def compose_status_message(message_params):
    message = create_message_header(message_params)
    message['command'] = 'GetStatus'
    return message
#------------------------------------------------------------------------------
def show_jobs_status(message_params, ws, remote_address):
    try:
        tags=[]
        #ws = websocket.create_connection(remote_address)
        server_job_status = []
        remote_address = message_params.get_remote_address()
        message = compose_status_message(message_params)
        if message_params.tag:
            tags.append(message_params.tag)
        else:
            tags = load_tags_from_db ()
        for tag in tags:
            #ws = websocket.create_connection(remote_address)
            if not ws.connected:
                ws.connect(remote_address)
            message['tag'] = tag
            ws.send(str(message))
            results = ws.recv()
            #print(f'reply received: {results}')
            ws.close()
            reply_msg = json.loads(results.replace("'",'"'))
            params = reply_msg['params']
            for p in params:
                server_job_status.append(p)
            #print('connection closed')
    except Exception as e:
        print(f'"show_jobs_status", runtime error: {e}')
    finally:
        if 'params' in locals():
            update_jobs_server_status (params)
        else:
            print('no status retrieved')
        status_list = []
        for x in server_job_status:
            if type(x) is dict:
                status_list.append([x['job_id'],x['job_status'],x['job_time']])
                #print(f"{x['job_id']}: {x['job_status']}")
        print(tabulate.tabulate(status_list, headers=['Job ID', 'status','since'], tablefmt='orgtbl'))
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
    remote_address = message_params.get_remote_address()
    try:
        ws = websocket.create_connection(remote_address)
    except:
        ws = None
    if ws:
        if message_params.is_send_command():
            send_fit_job (message_params, ws, remote_address)
        elif message_params.is_local_command():
            show_local_jobs()
        elif message_params.is_status_command():
            show_jobs_status(message_params, ws, remote_address)
        elif message_params.is_server_command():
            show_jobs_on_server(message_params, ws, remote_address)
        elif message_params.is_data_command():
            get_jobs_server_data(message_params, ws, remote_address)
        elif message_params.is_tag_command():
            get_server_tags(message_params, ws, remote_address)
        elif message_params.is_delete_command():
            delete_server_jobs(message_params, ws, remote_address)
        if ws.connected:
            ws.close()
    else:
        print(f'Could not connect to {remote_address}')
    exit(0)
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
