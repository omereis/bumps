import json

BROKER  = 'broker'
BACKEND = 'backend'
TYPE    = 'type'
RABBIT  = 'rabbit'
REDIS   = 'redis'
ADDRESS = 'address'
#------------------------------------------------------------------------------
def read_file_setup (file_name, content):
    file = None
    try:
        file = open(file_name, 'r')
        content.append(file.read())
        file.close()
        file_read = True
    except Exception as e:
        file_read = False
        sErr = f'{e}'
        content.append(sErr)
    finally:
        if file:
            file.close()
    return file_read
#------------------------------------------------------------------------------
def read_setup():
    file_content=[]
    if read_file_setup ('bumps_celery_servers.json', file_content):
        print(f'File content:\n{file_content[0]}')
        sJson = file_content[0].lower().replace("\n","").replace("'",'"')
        jsonSetup = json.loads(sJson)
        print(f'JSON Setup: {str(jsonSetup)}')
    else:
        jsonSetup = {}
        print(f'reading fail:\n{file_content}')
    return jsonSetup
#------------------------------------------------------------------------------
def get_server_type_string(strType):
    if strType == RABBIT:
        strType = 'amqp'
    elif strType == REDIS:
        strType = 'redis'
    else:
        strType = ''
    return strType
#------------------------------------------------------------------------------
def get_broker_server(dictBroker):
    try:
        strType = get_server_type_string(dictBroker[TYPE])
        strServer = dictBroker[ADDRESS]
        strBroker = f'{strType}://{strServer}'
    except Exception as e:
        strBroker = ''
        print(f'get_broker_server runtime error: {e}')
    return strBroker
#------------------------------------------------------------------------------
def get_servers_string():
    jsonSetup = read_setup()
    if (BROKER in jsonSetup.keys()) and (BACKEND in jsonSetup.keys()):
        strBrokerServer = get_broker_server(jsonSetup[BROKER])
    if len(strBrokerServer) > 0:
        print(f'Broker Server: {strBrokerServer}')
    else:
        print("didn't work")

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
if __name__ == '__main__':
    get_servers_string()
