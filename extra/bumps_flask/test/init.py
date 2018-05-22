try:
    BACKEND_SERVER=os.environ['BACKEND_SERVER']
except:
    BACKEND_SERVER='bumps_redis'

try:
    BROKER_SERVER=os.environ['BROKER_SERVER']
except:
    BROKER_SERVER='rabbit-server'

try:
    f = open("oe_debug.txt", "a+")
    f.write("\n")
    f.write("'BACKEND_SERVER'=" + BACKEND_SERVER + "\n")
    f.write("'BROKER_SERVER'="  + BROKER_SERVER + "\n")
    f.close()
except Exception as excp:
    print ("Error: " + str(excp.args))
