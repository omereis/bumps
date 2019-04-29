import sys, getopt
#------------------------------------------------------------------------------
def get_host_port (def_host='0.0.0.0', def_port=5000):
    host = def_host,
    port = def_port
    try:
        options, remainder = getopt.getopt(sys.argv[1:],
            'h:p:',
            [
            'host=',
            'port='
            ])
    except getopt.GetoptError as err:
        print(err) 
        exit(1) 
    for opt, arg in options:
        if opt in ('-h', '--host'):
            host = arg.strip();
        elif opt in ('-p', '--port'):
            port = int (arg.strip())
    return host, port
#------------------------------------------------------------------------------
