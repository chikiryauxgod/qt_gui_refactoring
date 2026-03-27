import sys

from time import sleep

from log import Log, ERROR
from state import State, Ok, Error

try:
    from serial import Serial
    from serial.serialutil import SerialException
except ImportError:  # pragma: no cover - fallback for CI without pyserial
    class Serial:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs):
            raise ImportError("pyserial is not installed")

    SerialException = ImportError  # type: ignore[assignment]

class Port(Serial):

    def __init__(self, port='/dev/ttyUSB0', outfile=sys.stderr, queue=None):
        self.__oufile = outfile
        self.__queue = queue
        self.__work_w_port = 0
        self.log = Log()
        try:
            if port is not None:
                super().__init__(port, baudrate=115200)
                self.__work_w_port = 1
            self.state = State()
        except SerialException as e:
            self.state = Error('sdfdsfds', e)
            self.log(self.state, level=ERROR, file=self.__oufile, queue=self.__queue)
            raise e

    def G00(self, j1=0, j2=0, j3=0, j4=0, j5=0, j6=0):
        try:
            cmd = f'G00 J1={j1} J2={j2} J3={j3} J4={j4} J5={j5} J6={j6}\r\n'
            self.log(f'>> {cmd.strip()}', file=self.__oufile, queue=self.__queue)
            if self.__work_w_port:
                self.write(bytes(cmd,'ascii'))
            self.state = Ok(cmd)
        except Exception as e:
            self.state = Error(cmd, e)

    def set_speed(self, vp=50):
        try:
            cmd = f'G07 VP={vp}\r\n'
            self.log(f'>> {cmd.strip()}', file=self.__oufile, queue=self.__queue)
            if self.__work_w_port:
                self.write(bytes(cmd,'ascii'))
            self.state = Ok(cmd)
            assert self.is_ready()
        except Exception as e:
            self.state = Error(cmd, e)

    def is_ready(self, timeout=10000):
        if self.__work_w_port: 
            try:
                n = 0
                while 1:
                    n += 1
                    assert n < timeout, f'Превышено время ожидания в {timeout / 1000} секунд при выполнении операции {self.state.operation}'
                    x = self.read_all().decode('ascii').strip()
                    if x:
                        self.log(f'<< {x}', file=self.__oufile, queue=self.__queue)
                    if '%' in x:
                        break
                    sleep(0.001)
            except Exception as e:
                self.state = Error(self.state.operation, e)
                raise self.state
        else:
            self.log('<< симуляция!', file=self.__oufile, queue=self.__queue)

if __name__ == '__main__':
    from queue import Queue
    q = Queue()
    p = Port(port=None, outfile=open('/tmp/log','w'), queue=q)
    p.set_speed(1), print(q.get())
    p.set_speed(100), print(q.get())
    p.set_speed(75), print(q.get())
    p.G00(j5=115550, j4=113.5, j6=-90), print(q.get())
    p.is_ready(), print(q.get())
    p.G00(j1=152, j5=115550*2, j4=113.5, j6=-90), print(q.get())
    p.is_ready(), print(q.get())
    # p.G00(j5=115550)
    # p.is_ready()
    p.G00(), print(q.get())
    p.is_ready(), print(q.get())
