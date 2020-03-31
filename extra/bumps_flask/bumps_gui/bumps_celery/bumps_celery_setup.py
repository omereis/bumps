import json

BROKER  = 'broker'
BACKEND = 'backend'
TYPE    = 'type'
RABBIT  = 'rabbit'
REDIS   = 'redis'
ADDRESS = 'address'
MESSAGE = 'message'
ERROR   = 'error'
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
    if read_file_setup ('bumps_celery/bumps_celery_servers.json', file_content):
        #print(f'File content:\n{file_content[0]}')
        sJson = file_content[0].lower().replace("\n","").replace("'",'"')
        jsonSetup = json.loads(sJson)
        #print(f'JSON Setup: {str(jsonSetup)}')
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
def get_server_string(dictBroker):
    try:
        #print(f'get_server_string, dictBroker: {str(dictBroker)}')
        strType = get_server_type_string(dictBroker[TYPE])
        #print(f'get_server_string, strType: {strType}')
        strServer = dictBroker[ADDRESS]
        #print(f'get_server_string, strType: {strServer}')
        strBroker = f'{strType}://{strServer}'
    except Exception as e:
        strBroker = ''
        print(f'get_server_string runtime error: {e}')
    return strBroker
#------------------------------------------------------------------------------
def get_servers_string():
    jsonSetup = read_setup()
    jsonSetupString={}
    fServersStringOK = False
    strErr = ''

    try:
        if (BROKER in jsonSetup.keys()) and (BACKEND in jsonSetup.keys()):
            strBrokerServer = get_server_string(jsonSetup[BROKER])
            strBackendServer = get_server_string(jsonSetup[BACKEND])
            jsonSetupString[BROKER]  = strBrokerServer
            jsonSetupString[BACKEND] = strBackendServer
            fServersStringOK = True
        else:
            if BROKER not in jsonSetup.keys():
                strErr = 'Could not find broker'
            if BACKEND not in jsonSetup.keys():
                print(str(jsonSetup.keys()))
                strErr = 'Could not find backend'
            fServersStringOK = False
    except Exception as e:
        fServersStringOK = False
        strErr = f'{e}'
    if not fServersStringOK:
        jsonSetupString[BROKER]  = 'amqp://rabbit-server'
        jsonSetupString[BACKEND] = 'redis://redis-server'
        jsonSetupString[ERROR] = strErr
    return jsonSetupString

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
if __name__ == '__main__':
    get_servers_string()
