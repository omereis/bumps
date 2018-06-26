from celery_bumps import tasks
import time

from .misc import get_celery_queue_names, print_debug

def run_celery_bumps():
#    res = tasks.add.delay(4,5)
    tEnd = tStart = time.time()
    res = tasks.run_bumps1.delay('/home/bumps_user/bumps_flask/test/cf1.py')
    tDelta = tEnd - tStart
    fReady = res.ready()
    while ((fReady == False) and (tDelta < 10)):
        fReady = res.ready()
#        tEnd = time.time()
        tDelta = time.time() - tStart
    if (res.ready()):
        print_debug("result: " + str(res.get()))
        print_debug("Processing time: " + str(tDelta))
#        print("result: " + str(res.get()))
#        print("Processing time: " + str(tDelta))
    else:
        print_debug("results not ready :-(")


#print("calling 'run_celery_bumps'")
if __name__ == 'mainchik':
    run_celery_bumps()
