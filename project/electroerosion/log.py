import queue
import sys

from datetime import datetime

INFO = 'INFO'
ERROR = 'ERROR'
WARNING = 'WARNING'

class Log:

    def __call__(self, data, level=INFO, file=None, queue=None):
        s = f'{datetime.now()}: [{level}]: {data}'
        if file is not None:
            print(s, file=file)
        if queue is not None:
            queue.put(s)
        if queue is None and file is None:
            print(s, file=sys.stderr)


if __name__ == '__main__':
    logger = Log()
    q = queue.Queue()

    logger('Это сообщение будет записано в файл', file=open('log.txt', 'a'))
    logger('Это сообщение будет помещено в очередь', queue=q)
    logger('Это сообщение будет выведено в stderr')

    print(f"Получено из очереди: {q.get()}")
