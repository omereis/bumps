from oe_debug import print_debug
from enum import Enum
import os, json

base_results_dir = '/tmp/bumps_results/'
#------------------------------------------------------------------------------
class MessageCommand (Enum):
    Error    = -1
    StartFit = 1
    Status   = 2
    Delete   = 3
    GetData  = 4
    PrintStatus = 5
    GetResults  = 6
#------------------------------------------------------------------------------
MessageTag         = 'tag'
MessageTime        = 'message_time'
MessageProblemFile = 'problem_file'
MessageCode        = 'command'
MessageFitProblem  = 'fit_problem'
MessageParams      = 'params'
MessageRowID       = 'row_id'
#------------------------------------------------------------------------------
def generate_key (client_host, time_string):
    key = client_host.replace('.','_') + '_' + str(time_string)
    return key
#------------------------------------------------------------------------------
def extract_problem_file_name(filename):
    try:
        name = filename
        if (name.find('\\') >= 0):
            inv_name = name[::-1]
            p = inv_name.find('\\')
            inv_part = inv_name[0:p]
            name = inv_part[::-1]
    except Exception as e:
        print(f'Error in extract_problem_file_name: {e}')
        name = 'bumps_problem.py'
    return name
#------------------------------------------------------------------------------
def parse_command (message_command):
    if message_command == 'StartFit':
        command = MessageCommand.StartFit
    elif message_command == 'GetStatus':
        command = MessageCommand.Status
    elif message_command == 'Delete':
        command = MessageCommand.Delete
    elif message_command == 'get_data':
        command = MessageCommand.GetData
    elif message_command == 'print_status':
        command = MessageCommand.PrintStatus
    elif message_command == 'get_results':
        command = MessageCommand.GetResults
    else:
        command = MessageCommand.Error
    return command
#------------------------------------------------------------------------------
def getMessageField (message, key):
    val = None
    if key in message.keys():
        val = message[key]
    return val
#------------------------------------------------------------------------------
class ClientMessage:
    host_ip      = None
    key          = None
    message      = None
    tag          = None
    message_time = None
    command      = None
    job_dir      = None
    results_dir  = './results'
    problem_text = None
    problem_file_name = None
    params       = None
    row_id       = None
#------------------------------------------------------------------------------
    def parse_message(self, websocket, message):
        try:
            parse = False
            header = message['header']
            if header ==  'bumps client':
                self.host_ip      = websocket.remote_address[0]
                self.message      = message
                self.tag          = getMessageField (message, MessageTag)
                self.message_time = getMessageField (message,  MessageTime)
                self.problem_file_name = getMessageField (message, MessageProblemFile)
                self.key          = generate_key(self.host_ip, self.message_time)
                self.command      = parse_command (getMessageField (message, MessageCode))
                self.problem_text = getMessageField (message, MessageFitProblem)
                self.params       = getMessageField (message, MessageParams)
                self.row_id       = getMessageField (message, MessageRowID)
                self.job_dir      = self.compose_job_directory_name () # just get the name, does not create directory
                parse = True
        except Exception as e:
            print('message_parser.py, parse_message: {}'.format(e))
            parse = False
        return parse
#------------------------------------------------------------------------------
    def compose_job_directory_name (self):
        try:
            tmp_dir = results_dir = base_results_dir + self.host_ip + "/" + self.tag
        except:
            tmp_dir = results_dir = base_results_dir + '/results'
        n = 1
        while os.path.exists(results_dir):
            results_dir = tmp_dir + '_' + str(n)
            n = n + 1
        return results_dir
#------------------------------------------------------------------------------
    def create_results_dir (self):
        if len(self.job_dir) == 0:
            self.job_dir = self.compose_job_directory_name ()
        results_dir = tmp_dir = self.job_dir + '/results'
        n = 1
        while os.path.exists(results_dir):
            results_dir = tmp_dir + '_' + str(n)
            n = n + 1
        os.makedirs (results_dir, 0o7777)
        os.chmod(results_dir, 0o7777)
        self.results_dir = results_dir
        return results_dir
#------------------------------------------------------------------------------
    def create_results_dir1 (self):
        try:
            tmp_dir = results_dir = base_results_dir + self.host_ip + "/" +self.tag
            dir_len = len(results_dir)
            n = 1
            while os.path.exists(results_dir):
                results_dir = tmp_dir + '_' + str(n)
                n = n + 1
            #results_dir += '/out'
            os.makedirs (results_dir, 0o7777)
            os.chmod(results_dir, 0o7777)
            self.results_dir = results_dir
        except:
            results_dir = './results'
        return results_dir
#------------------------------------------------------------------------------
    def get_problem_file_name (self):
        problem_file_name = ''
        filename_ok = True
        try:
            problem_file_name = extract_problem_file_name(self.message['problem_file'])
            if len(problem_file_name.strip()) == 0:
                filename_ok = False
        except:
            filename_ok = False
        finally:
            if not(filename_ok):
                problem_file_name = self.tag + ".py"
        return problem_file_name
#------------------------------------------------------------------------------
    def save_problem_file (self):
        if len(self.job_dir) == 0:
            self.job_dir = self.compose_job_directory_name ()
        problem_file_name = self.job_dir + "/" + self.get_problem_file_name ()
        file = open(problem_file_name, "w+")
        file.write(self.problem_text)
        file.close()
        self.problem_file_name = problem_file_name
        return problem_file_name
#------------------------------------------------------------------------------
    def save_problem_file1 (self):
        if not(self.results_dir):
            self.results_dir = self.create_results_dir()
        problem_file_name = self.results_dir + "/" + self.get_problem_file_name ()
        print ("Results file: {}".format(problem_file_name))
        file = open(problem_file_name, "w+")
        file.write(self.problem_text)
        file.close()
        self.problem_file_name = problem_file_name
        return problem_file_name
#------------------------------------------------------------------------------
    def get_param_by_key(self, key, def_val):
        n = None
        try:
            n = int(self.params[key])
        except:
            n = def_val
            self.params[key] = n
        return n
#------------------------------------------------------------------------------
    def get_steps(self):
        return self.get_param_by_key('steps', 100)
#------------------------------------------------------------------------------
    def get_burn(self):
        return self.get_param_by_key('burns', 100)
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def get_message_datetime_string (message_time):
    datetime_str = '{}-{}-{} {}:{}:{}.{}'.format(message_time['year'], message_time['month'], message_time['date'],\
                                    message_time['hour'], message_time['minutes'], message_time['seconds'], message_time['milliseconds'])
    return datetime_str
#------------------------------------------------------------------------------
