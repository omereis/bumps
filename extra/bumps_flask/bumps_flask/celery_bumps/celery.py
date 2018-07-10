from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
from .oe_debug import print_debug
from .celery_misc import get_backend_url, get_broker_url
#------------------------------------------------------------------------------
backend_url = get_backend_url()
broker_url   = get_broker_url()
#------------------------------------------------------------------------------
app = Celery('bumps', broker=broker_url, backend=backend_url)
#------------------------------------------------------------------------------
app.conf.update(result_expires=3600,)
#------------------------------------------------------------------------------
if __name__ == '__main__':
    app.start()
