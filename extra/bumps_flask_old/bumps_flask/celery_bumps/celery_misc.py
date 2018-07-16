import os
#------------------------------------------------------------------------------
def get_env_value (env_var, default_value):
    try:
        env_value = os.environ[env_var]
    except:
        env_value = default_value
    return env_value
#------------------------------------------------------------------------------
def get_backend_url():
        return "redis://" + get_env_value ('BACKEND_SERVER', 'ncnr-r9nano')
#------------------------------------------------------------------------------
def get_broker_url():
    broker_url   = "amqp://" + get_env_value ('BROKER_SERVER', 'ncnr-r9nano')
    return broker_url
    