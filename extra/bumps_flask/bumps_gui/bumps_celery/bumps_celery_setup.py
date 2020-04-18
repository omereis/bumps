import json

BROKER  = 'broker'
BACKEND = 'backend'
TYPE    = 'type'
RABBIT  = 'rabbit'
REDIS   = 'redis'
ADDRESS = 'address'
MESSAGE = 'message'
ERROR   = 'error'
STRING  = 'string'
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
        sJson = file_content[0].lower().replace("\n","").replace("'",'"')
        dctSetup = json.loads(sJson)
    else:
        dctSetup = {}
        print(f'reading fail:\n{file_content}')
    return dctSetup
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
def get_server_string(dctSrerver):
    try:
        strType = get_server_type_string(dctSrerver[TYPE])
        strServer = dctSrerver[ADDRESS]
        strBroker = f'{strType}://{strServer}'
    except Exception as e:
        strBroker = ''
        print(f'get_server_string runtime error: {e}')
    return strBroker
#------------------------------------------------------------------------------
def get_servers_string():
    dctSetup = read_setup()
    return get_servers_string_from_dict(dctSetup)
#------------------------------------------------------------------------------
def get_servers_string_from_dict(dctSetup):
    dctSetupString={}
    fServersStringOK = False
    strErr = ''

    try:
        if (BROKER in dctSetup.keys()) and (BACKEND in dctSetup.keys()):
            strBrokerServer = get_server_string(dctSetup[BROKER])
            strBackendServer = get_server_string(dctSetup[BACKEND])
            dctSetupString[BROKER]  = strBrokerServer
            dctSetupString[BACKEND] = strBackendServer
            fServersStringOK = True
        else:
            if BROKER not in dctSetup.keys():
                strErr = 'Could not find broker'
            if BACKEND not in dctSetup.keys():
                print(str(dctSetup.keys()))
                strErr = 'Could not find backend'
            fServersStringOK = False
    except Exception as e:
        fServersStringOK = False
        strErr = f'{e}'
    if not fServersStringOK:
        dctSetupString[BROKER]  = 'amqp://rabbit-server'
        dctSetupString[BACKEND] = 'redis://redis-server'
        dctSetupString[ERROR] = strErr
    return dctSetupString
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
if __name__ == '__main__':
    get_servers_string()
