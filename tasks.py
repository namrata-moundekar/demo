# from celery import Celery

from view import simple_app
import time

@simple_app.task
def longtime_add(x, y):
 print('long time task begins')
 # sleep 5 seconds
 time.sleep(25)
 print('long time task finished')
 return x + y





