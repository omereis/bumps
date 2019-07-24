try:
    from .res_dir import run_bumps
except:
    from bumps_celery.res_dir import run_bumps
import sys
#------------------------------------------------------------------------------
class ClientMessage:
    host_ip      = None
    key          = None
    message      = None
    tag          = None
    message_time = None
    command      = None
    job_dir      = None
    results_dir  = './results'
    problem_text = None
    problem_file_name = None
    params       = None
    multi_proc   = None
    local_id     = None
#------------------------------------------------------------------------------
import zipfile, shutil, os
if __name__ == '__main__':
    client_message = ClientMessage()
    if len(sys.argv) >= 2:
        client_message.tag = sys.argv[1]
        client_message.problem_file_name = sys.argv[2]
        f = open(client_message.problem_file_name, 'r')
        client_message.problem_text = f.read()
        f.close()
        bin_data = run_bumps(client_message)
        f = open('myfile.zip', 'wb')
        f.write(bin_data)
        f.close()
        if os.path.exists('res'):
            shutil.rmtree('res')
        os.makedirs('res')
        zip = zipfile.ZipFile('myfile.zip', 'r')
        zip.extractall('res')
    else:
        print(f'Usage:')
        print(f'python {__file__} <tag> <problem_file>')
