from bumps_server import get_host_port
from bumps_server import bumps_ws_server
import os

if __name__ == '__main__':
    host, port = get_host_port.get_host_port (def_host='NCNR-R9nano.campus.nist.gov', def_port=8765)
    flask_dir = os.getcwd() + "/" + os.environ['FLASK_APP']
    print(f'host: {host}')
    print(f'port: {port}')
    print(f'flask directory: {flask_dir}')
    bumps_ws_server.main(serverHost=host, serverPort=port, flask_dir=flask_dir)
    #bumps_ws_server.main(serverHost='0.0.0.0', serverPort='4567', flask_dir='/home/app_user/bumps_flask/bumps_flask')
