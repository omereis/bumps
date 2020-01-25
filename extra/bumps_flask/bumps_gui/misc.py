import os, zipfile

#------------------------------------------------------------------------------
def get_results_dir ():
    try:
        results_dir = os.environ['FIT_RESULTS_DIR']
    except Exception as e:
        print ('Environment variable not found. Using default')
        results_dir = '/home/app_user/bumps_flask/bumps_flask/static/fit_results'
    if results_dir[len(results_dir) - 1] != '/':
        results_dir += '/'
    return results_dir
#------------------------------------------------------------------------------
def get_web_results_dir ():
    return '/static/fit_results/'
#------------------------------------------------------------------------------
def get_files_list(lst_files, dir):
    dir_list = os.listdir(dir)
    for file in dir_list:
        full_name = f'{dir}{os.path.sep}{file}'
        if os.path.isdir(full_name):
            get_files_list(lst_files, full_name)
        else:
            lst_files.append(full_name)
#------------------------------------------------------------------------------
def zip_directory(zip_name, dir):
    try:
        full_zip = f'{dir}{os.path.sep}{zip_name}'
        zip_file = zipfile.ZipFile(full_zip, 'w')
        lst_files = []
        if os.path.exists(dir):
            if os.path.isdir(dir):
                get_files_list(lst_files, dir)
                for file_name in lst_files:
                    if full_zip != file_name:
                    #print(f'zipping {file_name}')
                        zip_file.write(file_name)
        zip_file.close()
    except Exception as e:
        print(f'zip_directory runtime error: {e}')
    print(f'zip done {full_zip}')
#------------------------------------------------------------------------------
