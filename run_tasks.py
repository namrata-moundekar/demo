from tasks import longtime_add
from celery_app import *
import time

# if __name__ == '__main__':
#     # app.start()
#     app.run(host="0.0.0.0", debug=True)
    # results = longtime_add(23, 2)
    # print(results)
    # result = longtime_add.delay(23, 2)
    # print(result)
    # # at this time, our task is not finished, so it will return False
    # print('Task finished? ', result.ready())
    # print('Task result: ', result.result)
    # # sleep 10 seconds to ensure the task has been finished
    # time.sleep(30)
    # # now the task should be finished and ready method will return True
    # print('Task finished? ', result.ready())
    # print('Task result: ', result.result)