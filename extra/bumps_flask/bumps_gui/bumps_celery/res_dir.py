import os, sys, socket, shutil
# Add parent to path
sys.path.append(os.path.abspath(os.path.join('.', os.pardir)))
# import message parser from parent
import message_parser
#------------------------------------------------------------------------------
def item_from_list (item, src_list):
    try:
        n = 0
        iFound = -1
        while (n < len(src_list)) and (iFound < 0):
            if src_list[n].find(item) >= 0:
                iFound = n
            n += 1
        if iFound >= 0:
            result = src_list[iFound]
        else:
            result = None
    except Exception as e:
        print(f'runtime error: {e}')
    return result
#------------------------------------------------------------------------------
def get_param_res_dir (params):
    key_store = '--store'
    if key_store in ''.join(params):
        store = item_from_list (key_store, params)
        try:
            if store.find('='):
                res = store.split('=')[1]
            else:
                res = store.split(' ')[1]
        except:
            res = None
    return res
#------------------------------------------------------------------------------
def get_results_directory (params):
    res_dir = get_param_res_dir(params)
    if res_dir == None:
        n = 1
        base_res = os.getcwd() + os.sep
        if res_file:
            base_res += res_file
        else:
            base_res += 'resuts'
        candidate = base_res
        params.append('--store')
        params.append(candidate)
    else:
        candidate = res_dir
    return candidate
#------------------------------------------------------------------------------
def get_work_dir(tag='bumps_results'):
    try:
        base_dir = "."
        n = 1
        work_dir = f'{base_dir}{os.sep}{tag}'
        fExists = os.path.exists(work_dir)
        while fExists:
            work_dir = f'{base_dir}{os.sep}{tag}_{n}'
            fExists = os.path.exists(work_dir)
            n += 1
    except:
        work_dir = None
    return work_dir
#------------------------------------------------------------------------------
def get_problem_file_name(work_dir, client_message):
    if client_message.problem_file_name:
        file_name = client_message.problem_file_name
    elif client_message.tag:
        file_name = f'{client_message.tag}.py'
    else:
        file_name = 'bumps_problem.py'
    return file_name
#------------------------------------------------------------------------------
import zipfile
def zipdir(path, ziph):
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                #_zip = os.path.join(root, file)
                ziph.write(os.path.join(root, file))
                #ziph.write(_zip)
    except Exception as e:
        print(f'"zipdir" runtime error: {e}')
#------------------------------------------------------------------------------
import sys, bumps, os
#------------------------------------------------------------------------------
def save_problem_file (client_message):
    name = client_message.problem_file_name
    if (name == None) or (len(name) == 0):
        name = client_message.tag
        #file_name = client_message.problem_file_name = client_message.tag
    client_message.problem_file_name = f'{client_message.job_dir}{os.sep}{name}.py'
    f = open(client_message.problem_file_name, 'w')
    f.write(client_message.problem_text)
    f.close()
#------------------------------------------------------------------------------
def zip_directory (zip_file_name, work_dir):
#    zip_name = 'bumps_results.zip'
    zip_file = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
    zipdir(work_dir, zip_file)
    zip_file.close()
#------------------------------------------------------------------------------
import ntpath, tempfile
#------------------------------------------------------------------------------
def zip_results(client_message):
    try:
        zipname = f'{tempfile.gettempdir()}{os.sep}{ntpath.basename(client_message.job_dir)}.zip'
        current_dir = os.getcwd()
        os.chdir(client_message.job_dir)
        zip_directory (zipname, f'.{os.sep}')
    except Exception as e:
        print (f'"zip_results" runtime error: {e}')
        zipname = None
    finally:
        os.chdir(current_dir)
    return zipname
#------------------------------------------------------------------------------
def run_local_bumps(message):
    client_message = message_parser.ClientMessage()
    host_ip = socket.gethostbyname(socket.gethostname())
    client_message.parse_message(host_ip, message, None)
    work_dir = get_work_dir(client_message.tag)
    client_message.set_job_directory(work_dir)
    save_problem_file (client_message)
    params = client_message.prepare_bumps_params()
    print(f'"run_local_bumps" params: {params}')
    print(f'""run_local_bumps" job directory: {client_message.job_dir}')
    try:
        system_args = sys.argv
        s_out = sys.stdout
        sys.argv = params
        #
        bumps.cli.main()
        #
        sys.stdout = s_out
        zipname = zip_results(client_message)
        print(f'results zipped to "{zipname}"')
        f = open(zipname, 'rb')
        bin_content = f.read()
        f.close()
        os.remove(zipname)
        shutil.rmtree(client_message.job_dir)
        hex_result = bin_content.hex()
    except Exception as e:
        print(f'"run_local_bumps" runtime error: {e}')
        hex_result = None
    finally:
        sys.argv = system_args
    return hex_result
#------------------------------------------------------------------------------
def run_local_bumps1(client_message):
    work_dir = get_work_dir(client_message.tag)
    if work_dir:
        os.makedirs(work_dir)
        fname = f'{work_dir}{os.sep}{get_problem_file_name(work_dir, client_message)}'
        f = open(fname, 'w')
        f.write(client_message.problem_text)
        f.close()
        zip_name = 'bumps_results.zip'
        zip_file = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
        zipdir(work_dir, zip_file)
        zip_file.close()
        f = open(zip_name, 'rb')
        resuts = f.read()
        f.close()
        shutil.rmtree(work_dir)
        #sleep (3)
    else:
        resuts = None
    return resuts
#------------------------------------------------------------------------------
