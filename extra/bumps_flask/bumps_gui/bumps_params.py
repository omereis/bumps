import readchar
import sys
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
class BumpsParams:
    server = 'localhost'
    port   = 5000
    mp_port = 4567
    is_help = False
    verify = False
#------------------------------------------------------------------------------
    def print_params(self):
        print (f'server  = {self.server}')
        print (f'port    = {self.port}')
        print (f'mp_port = {self.mp_port}')
#------------------------------------------------------------------------------
    def verify_params(self):
        self.print_params()
        print('Are you ok with the parameters ([y]/n)?', end=' ')
        sys.stdout.flush()
        return read_y_n()
    #------------------------------------------------------------------------------
#------------------------------------------------------------------------------
