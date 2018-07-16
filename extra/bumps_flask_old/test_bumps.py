from bumps import cli
import sys

def main():
    print ("The arguments are: " , str(sys.argv))
    print ("The number of the arguments is: " , len(sys.argv))
    use_celery = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'c':
            use_celery = True
    if use_celery:
        try:
            res = cli.main.delay(['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/app_user/bumps_flask/test/cf1.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/app_user/results', '--fit=newton'])
            res_folder = "Celery computed results:\n" + res.get()
        except:
            res_folder = None

    else:
        res_folder = "no celery results:\n:" + cli.main(['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/app_user/bumps_flask/test/cf1.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/app_user/results', '--fit=newton'])
    if res_folder:
        print("Results are in " + res_folder)
    else:
        print("No Results. Yok!")

if __name__ == '__main__':
    main()

