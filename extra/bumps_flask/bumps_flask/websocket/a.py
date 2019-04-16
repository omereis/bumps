import asyncio
import websockets
import getopt, sys

host='localhost'
port='8765'

version = '1.0'
verbose = False
output_filename = 'default.out'

print('ARGV      :', sys.argv[1:])

try:
    options, remainder = getopt.getopt(
        sys.argv[1:],
        'h:p:o:v',
        ['output=',
         'verbose',
         'version=',
         'host=',
         'port='
         ])

except getopt.GetoptError as err:
    print(err) 
    sys.exit(1)

print('OPTIONS   :', options)
for opt, arg in options:
    if opt in ('-o', '--output'):
        output_filename = arg
    elif opt in ('-v', '--verbose'):
        verbose = True
    elif opt == '--version':
        version = arg
    elif opt in ('-h', '--host'):
        host = arg
    elif opt in ('-p', '--port'):
        port = arg
    
print('VERSION   :', version)
print('VERBOSE   :', verbose)
print('OUTPUT    :', output_filename)
print('REMAINING :', remainder)
print('HOST      :', host)
print('PORT      :', port)
