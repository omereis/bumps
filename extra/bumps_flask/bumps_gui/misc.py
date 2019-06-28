import os

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
