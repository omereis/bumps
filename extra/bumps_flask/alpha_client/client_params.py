from random_word import RandomWords
import sys, readchar, sqlite3
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
    print('')
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
    command      = 'send'
    valid_commands = ('send','local', 'status','data', 'server', 'tags', 'delete', 'help')
#------------------------------------------------------------------------------
#    def __init__(self):
#        try:
#            r = RandomWords()
#            self.tag = r.get_random_word()
#        except Exception as e:
#            print(f'MessageParams constructor runtime error: {e}')
#        finally:
#            if self.tag == None:
#                self.tag = 'default_tag'
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
        print(f'Command: {self.command}')
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
    def read_problem_file(self, idx=0):
        problem = ''
        f = None
        try:
            f = open(self.files_names[idx], 'r')
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
    def set_command (self, command):
        if command in self.valid_commands:
            self.command = command
            command_valid = True
        else:
            command_valid = False
        return command_valid
#------------------------------------------------------------------------------
    def is_send_command(self):
        return self.command.lower() == 'send'
#------------------------------------------------------------------------------
    def is_local_command(self):
        return self.command.lower() == 'local'
#------------------------------------------------------------------------------
    def is_status_command(self):
        return self.command.lower() == 'status'
#------------------------------------------------------------------------------
    def is_server_command(self):
        return self.command.lower() == 'server'
#------------------------------------------------------------------------------
    def is_data_command(self):
        return self.command.lower() == 'data'
#------------------------------------------------------------------------------
    def is_tag_command(self):
        return self.command.lower() == 'tags'
#------------------------------------------------------------------------------
    def is_delete_command(self):
        return self.command.lower() == 'delete'
#------------------------------------------------------------------------------
    def get_new_tag(self):
        if self.tag == None:
            try:
                r = RandomWords()
                self.tag = r.get_random_word()
            except Exception as e:
                print(f'MessageParams constructor runtime error: {e}')
            finally:
                if self.tag == None:
                    self.tag = 'default_tag'
        return self.tag
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
