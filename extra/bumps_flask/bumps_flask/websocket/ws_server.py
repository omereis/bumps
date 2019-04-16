import asyncio
import websockets
import getopt, sys

#------------------------------------------------------------------------------
host = 'localhost'
port = 8765
#------------------------------------------------------------------------------
try:
    if len(sys.argv) > 0:
        print('ARGV      :', sys.argv[1:])
        options, remainder = getopt.getopt(
            sys.argv[1:],
            'h:p:',
            [
            'host=',
            'port='
            ])
except getopt.GetoptError as err:
    print(err) 
    exit(1)
#------------------------------------------------------------------------------
for opt, arg in options:
    if opt in ('-h', '--host'):
        host = arg.strip();
    elif opt in ('-p', '--port'):
        port = arg.strip();
#------------------------------------------------------------------------------
async def hello(websocket, path):
    name = await websocket.recv()
    source = "{}:{}".format(websocket.host, websocket.port)
    print ("Just got a message from...")
    try:
        print ("    client in {}".format(source))
    except Exception as e:
        print('Oops: {}'.format(e.message))
    print(" {}".format(name))
    greeting = "Hello {}, from {}:{}!".format(name, host, port)
    await websocket.send(greeting)
    print(greeting)
#------------------------------------------------------------------------------
print('Host: {}'.format(host))
print('Port: {}'.format(port))
start_server = websockets.serve(hello, host, port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
