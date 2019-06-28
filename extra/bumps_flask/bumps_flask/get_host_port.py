import sys, getopt
#------------------------------------------------------------------------------
def get_host_port (def_host='1.2.4.5', def_port=5000):
    host = def_host,
    port = def_port
    try:
        # Note: arguments start after 2nd word (flask run --<parameter>)
        options, remainder = getopt.getopt(sys.argv[2:],
            'h:p:y',
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
