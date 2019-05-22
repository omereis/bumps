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
def extract_file_name(filename):
    name = filename
    if (name.find('\\') >= 0):
        inv = name[::-1]
        p = inv.find('\\')
        inv = inv[0:p]
        name = p[::-1]
    return name
#------------------------------------------------------------------------------
def parse_command (message_command):
    if message_command == 'StartFit':
        command = MessageCommand.StartFit
    elif message_command == 'status':
        command = MessageCommand.Status
    elif message_command == 'Delete':
        command = MessageCommand.Delete
    elif message_command == 'get_data':
        command = MessageCommand.GetData
    else:
        command = MessageCommand.Error
    return command
#------------------------------------------------------------------------------
def getMessageField (message, key):
    print_debug('getMessageField, key: {}'.format(key))
    val = None
    if key in message.keys():
        val = message[key]
        print_debug('getMessageField, key: {}'.format(message[key]))
    return val
#------------------------------------------------------------------------------
class ClientMessage:
    host_ip      = None
    key          = None
    message      = None
    tag          = None
    message_time = None
    command      = None
    results_dir  = None
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
                parse = True
        except Exception as e:
            print('message_parser.py, parse_message: {}'.format(e))
            parse = False
        return parse
#------------------------------------------------------------------------------
    def create_results_dir (self):
        tmp_dir = results_dir = base_results_dir + self.host_ip + "/" +self. tag
        dir_len = len(results_dir)
        n = 1
        while os.path.exists(results_dir):
            results_dir = tmp_dir + '_' + str(n)
            n = n + 1
        os.makedirs (results_dir, 0o7777)
        os.chmod(results_dir, 0o7777)
        self.results_dir = results_dir
        return results_dir
#------------------------------------------------------------------------------
    def get_problem_file_name (self):
        problem_file_name = ''
        filename_ok = True
        try:
            problem_file_name = extract_file_name(self.message['problem_file'])
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
def get_message_datetime_string (message_time):
    datetime_str = '{}-{}-{} {}:{}:{}.{}'.format(message_time['year'], message_time['month'], message_time['date'],\
                                    message_time['hour'], message_time['minutes'], message_time['seconds'], message_time['milliseconds'])
    return datetime_str
#------------------------------------------------------------------------------
