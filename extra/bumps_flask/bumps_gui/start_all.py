import subprocess
#------------------------------------------------------------------------------
def main():
    subprocess.Popen(["python","-m","celery","-A","bumps_celery","worker","-l" "info","-E", "-Q", "bumps_queue"])
    subprocess.run(["python", "app_bumps.py", "-s 0.0.0.0", "-p 4000", "-m 4567"])
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()

