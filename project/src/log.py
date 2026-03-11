import sys
import queue

class Log:
    def __call__(self, message, queue=None, file=None):
        # вывод в указанный поток или в stdout по умолчанию
        if file is None:
            file = sys.stdout
        print(f"LOG: {message}", file=file)
        if queue is not None:
            queue.put(message)

logger = Log()
q = queue.Queue()