from celery_bumps import tasks
import time

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
        print("result: " + str(res.get()))
        print("Processing time: " + str(tDelta))
    else:
        print("results not ready :-(")


#print("calling 'run_celery_bumps'")
run_celery_bumps()
