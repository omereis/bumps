import os, sys, zipfile
#------------------------------------------------------------------------------
def zip_directory(zip_name, dir):
    full_zip = f'{dir}{os.path.sep}{zip_name}'
    zip_file = zipfile.ZipFile(full_zip, 'w')
    lst_files = []
    if os.path.exists(dir):
        if os.path.isdir(dir):
            get_files_list(lst_files, dir)
            for file_name in lst_files:
                if full_zip != file_name:
                    print(f'zipping {file_name}')
                    zip_file.write(file_name)
    zip_file.close()

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
if __name__ == "__main__":
    print(f'current path: "{os.getcwd()}"')
    if len(sys.argv) > 1:
        dir = sys.argv[1]
    else:
        dir = "."
    if len(sys.argv) > 2:
        zip_name = sys.argv[2]
    else:
        zip_name = 'zipdir.zip'
    lst_files = []
    if os.path.exists(dir):
        if os.path.isdir(dir):
            zip_directory(zip_name, dir)
            #get_files_list(lst_files, dir, dirsep)
            #print(len(lst_files))
            print(f'{zip_name} written')
