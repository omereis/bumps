import datetime
from celery import Celery
########################################################################################
def print_debug(strMessage):
    try:
        f = open ("oe_debug.txt", "a+")
        f.write("\n--------------------------------------------------\n")
        f.write(str(datetime.datetime.now()) + "\n")
        f.write("Message: " + strMessage + "\n")
        f.write("--------------------------------------------------\n")
        f.close()
    finally:
        f.close()
########################################################################################
def print_stack():
    try:
        import traceback
        f = open ("oe_debug.txt", "a+")
        f.write("-----------------------------\n")
        f.write("Printing Stack:\n")
        stack = traceback.extract_stack ()
        f.write("Stack length: " + str(len(stack)) + "\n")
        for n in range(len(stack)):
            f.write(str(n+1) + ": " + str(stack[n]) + "\n")
#        for s in stack:
#            f.write(str(s) + "\n")
    finally:
        f.close()
########################################################################################
def get_celery_queue_names():
    lstQueueNames = []
    appCeleryBumps = Celery('bumps', broker='amqp://rabbit-server', \
                    backend='redis://redis-server')
    dictQueues = appCeleryBumps.control.inspect().active_queues()
    for email in dictQueues:
        queue_list = dictQueues[email]
        for n in range(len(queue_list)):
            try:
                s = dictQueues[email][n]['name']
            except:
                s = ""
            lstQueueNames.append(s)
    return lstQueueNames
