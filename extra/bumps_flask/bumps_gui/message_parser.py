from enum import Enum
from MessageCommand import MessageCommand
import os, json
try:
    from .oe_debug import print_debug
    from .misc import get_results_dir
except:
    from oe_debug import print_debug
    from misc import get_results_dir
#------------------------------------------------------------------------------
MessageTag         = 'tag'
MessageTime        = 'message_time'
MessageProblemFile = 'problem_file'
MessageCode        = 'command'
MessageFitProblem  = 'fit_problem'
MessageParams      = 'params'
MessageClientID    = 'local_id'
MessageMultiProc   = 'multi_processing'
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
    elif message_command == 'GetDbStatus':
        command = MessageCommand.GetDbStatus
    elif message_command == 'get_tags':
        command = MessageCommand.GetTags
    else:
        print(f'\nMessage command: "{message_command}\n\n')
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
    bumps_params = None
    multi_proc   = None
    local_id     = None
    fitter       = 'bumps'
#------------------------------------------------------------------------------
    def parse_message(self, host_ip, message, results_dir):
        try:
            parse = False
            header = message['header']
            if header ==  'bumps client':
                self.host_ip      = host_ip
                self.message      = message
                self.tag          = getMessageField (message, MessageTag)
                self.message_time = getMessageField (message,  MessageTime)
                self.problem_file_name = getMessageField (message, MessageProblemFile)
                self.key          = generate_key(self.host_ip, self.message_time)
                self.command      = parse_command (getMessageField (message, MessageCode))
                self.problem_text = getMessageField (message, MessageFitProblem)
                self.params       = getMessageField (message, MessageParams)
                self.local_id     = getMessageField (message, MessageClientID)
                self.multi_proc   = getMessageField (message, MessageMultiProc)
                self.job_dir      = self.compose_job_directory_name (results_dir) # just get the name, does not create directory
                if 'fitter' in message.keys():
                    self.fitter = message['fitter']
                print(f'parse_message: Fitter: {self.fitter}')
                parse = True
        except Exception as e:
            print('message_parser.py, parse_message: {e}')
            parse = False
        return parse
#------------------------------------------------------------------------------
    def compose_job_directory_name (self, results_dir=None):
        try:
            if results_dir == None:
                results_dir = f'.{os.sep}bumps_fit'
            base_results_dir = results_dir
            tmp_dir = results_dir = base_results_dir + self.host_ip + "/" + self.tag
        except Exception as e:
            print(f'message_parser.py, parse_message: {e}')
            tmp_dir = results_dir = base_results_dir + '/results'
            print(f'using temporary directory: {tmp_dir}')
        n = 1
        while os.path.exists(results_dir):
            results_dir = tmp_dir + '_' + str(n)
            n = n + 1
        return results_dir
#------------------------------------------------------------------------------
    def create_results_dir (self, server_params):
        if len(self.job_dir) == 0:
            self.job_dir = self.compose_job_directory_name (server_params.results_dir)
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
    def prepare_bumps_params(self):
        self.bumps_params = []
        try:
            self.bumps_params.append('bumps')
            self.bumps_params.append(self.problem_file_name)
            self.bumps_params.append('--batch')
            for k in self.params.keys():
                if k == 'algorithm':
                    self.bumps_params.append(f'--fit={self.params[k]}')
                elif k == 'burns':
                    self.bumps_params.append(f'--burn={self.get_burn()}')
                elif k == 'steps':
                    self.bumps_params.append(f'--steps={self.get_steps()}')
            self.bumps_params.append(f'--store={self.results_dir}')
        except Exception as e:
            print(f'"ClientMessage.prepare_params", runtime error: {e}')
        return self.bumps_params
#------------------------------------------------------------------------------
    def adjust_job_directory(self):
        base_dir = job_dir = self.job_dir
        n = 1
        while (os.path.exists(job_dir)):
            job_dir = f'{base_dir}_{n}'
            n += 1
        os.makedirs(job_dir)
        os.chmod(job_dir, 0o7777)
        self.job_dir = job_dir
        return job_dir
#------------------------------------------------------------------------------
    def set_job_directory(self, work_dir):
        try:
            os.makedirs(work_dir)
            os.chmod(work_dir, 0o7777)
            self.job_dir = work_dir
        except Exception as e:
            print(f'"set_job_directory" runtime error: {e}')
            self.job_dir = '.'
        try:
            res = 'results'
            n = 1
            base_dir = results_dir = f'{self.job_dir}{os.sep}{res}'
            fExists = os.path.exists(results_dir)
            if fExists:
                results_dir = f'{results_dir}_{n}'
                fExists = os.path.exists(results_dir)
                n += 1
            self.results_dir = results_dir
        except Exception as e:
            print(f'Could not create esults directory: {e}')
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
    def print_message(self):
        print(f'host_ip: {self.host_ip}')
        print(f'key: {self.key}')
        print(f'message: {self.message}')
        print(f'tag: {self.tag}')
        print(f'message_time: {self.message_time}')
        print(f'command: {self.command}')
        print(f'job_dir: {self.job_dir}')
        print(f'results_dir: {self.results_dir}')
        print(f'problem_text: {self.problem_text}')
        print(f'problem_file_name: {self.problem_file_name}')
        print(f'params: {self.params}')
        print(f'bumps_params: {self.bumps_params}')
        print(f'multi_proc: {self.multi_proc}')
        print(f'local_id: {self.local_id}')
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def get_message_datetime_string (message_time):
    try:
        strDate = f'{message_time["year"]}-{message_time["month"]}-{message_time["date"]}'
        strTime = f'{message_time["hour"]}:{message_time["minutes"]}:{message_time["seconds"]}.{message_time["milliseconds"]}'
        strDateTime = f'{strDate} {strTime}'
    except Exception as e:
        print(f'"get_message_datetime_string" runtime error: {e}')
        strDateTime= ''
    return strDateTime
#------------------------------------------------------------------------------
