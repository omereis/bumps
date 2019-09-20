import os, sys, socket, shutil
sys.path.append(os.path.abspath(os.path.join('.', os.pardir)))
import message_parser
import ntpath, tempfile
from refl1d.main import cli as refl1d_cli
import sys, bumps, os
import zipfile
#------------------------------------------------------------------------------
def print_debug(msg):
    f = open('debug_oe.txt', 'a+')
    f.write('--------------------------------------------------\n')
    f.write(f'{msg}\n')
    f.write('--------------------------------------------------\n')
    f.close()
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
def get_work_dir(tag='bumps_results', base_dir='.'):
    try:
        #base_dir = "."
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
    try:
        zip_file = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
        zipdir(work_dir, zip_file)
        zip_file.close()
    except Exception as e:
        print (f'"zip_directory" runtime error: {e}')
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
def run_local_fit(message):
    client_message = message_parser.ClientMessage()
    host_ip = socket.gethostbyname(socket.gethostname())
    client_message.parse_message(host_ip, message, None)
    if client_message.is_bumps_fitter():
        results = run_local_bumps(client_message)
    elif client_message.is_refl1d_fitter():
        results = run_local_rfl1d(client_message)
    return results
#------------------------------------------------------------------------------
def run_local_bumps(client_message):
    work_dir = get_work_dir(client_message.tag)
    client_message.set_job_directory(work_dir)
    save_problem_file (client_message)
    params = client_message.prepare_bumps_params()
    try:
        system_args = sys.argv
        s_out = sys.stdout
        sys.argv = params
        bumps.cli.main()
        hex_result = finalize_fit_result_to_hex(client_message)
    except Exception as e:
        print(f'"run_local_bumps" runtime error: {e}')
        hex_result = None
    finally:
        sys.argv = system_args
        sys.stdout = s_out
    return hex_result
#------------------------------------------------------------------------------
def read_json_results(client_message):
    path = ntpath.split(client_message.problem_file_name)
    if len(path) > 0:
        json_file_name = path[1]
    else:
        json_file_name = path[0]
    name = json_file_name.split('.')[0]
    json_file_path = f'{client_message.results_dir}{os.sep}{name}-expt.json'
    try:
        f = open(json_file_path, 'r')
        content = f.read()
        f.close()
    except Exception as e:
        content = ''
        print(f'read_json_results runtime error: {e}')
    return content
#------------------------------------------------------------------------------
def run_local_rfl1d(client_message):
    work_dir = get_work_dir(client_message.tag, tempfile.gettempdir())
    client_message.set_job_directory(work_dir)
    client_message.save_refl1d_problem_file()
    params = client_message.prepare_refl1d_params()
    sys.argv = params
    try:
        s_out = sys.stdout
        refl1d_cli()
        sys.stdout = s_out
        hex_result = finalize_fit_result_to_hex(client_message)
    except Exception as e:
        print(f'run_local_rfl1d runtime error: {e}')
    return hex_result
#------------------------------------------------------------------------------
def finalize_fit_result_to_hex(client_message):
    try:
        zipname = zip_results(client_message)
        f = open(zipname, 'rb')
        bin_content = f.read()
        f.close()
        os.remove(zipname)
        shutil.rmtree(client_message.job_dir)
        hex_result = bin_content.hex()
    except Exception as e:
        hex_result = f'Error: {e}'
        print(f'run_local_rfl1d runtime error: {e}')
    return hex_result
#------------------------------------------------------------------------------
