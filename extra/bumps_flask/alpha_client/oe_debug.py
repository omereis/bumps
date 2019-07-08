import datetime
#-------------------------------------------------------------------------------
def print_debug(strMessage):
    try:
        f = open ("debug_oe.txt", "a+")
        f.write("\n--------------------------------------------------\n")
        f.write(str(datetime.datetime.now()) + "\n")
        f.write("Message: " + strMessage + "\n")
        f.write("--------------------------------------------------\n")
        f.flush()
        f.close()
    finally:
        f.close()
#-------------------------------------------------------------------------------
def print_stack():
    try:
        import traceback
        f = open ("debug_oe.txt", "a+")
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
#-------------------------------------------------------------------------------
