import subprocess
#------------------------------------------------------------------------------
def main():
    subprocess.Popen(["python","-m","celery","-A","bumps_celery","worker","-l" "info","-E"])
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()

