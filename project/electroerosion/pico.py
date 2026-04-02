import re
import sys

from json import loads, JSONDecodeError
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

TIMEOUT_OPENING_PORT = 5
DEFAULTS = {
    'current':  0,
    'down':     0,
    'erosion':  0,
    'position': 0,
    'pump':     0,
    'pump_in':  0,
    'pump_out': 0,
    'reset':    0,
    'test':     0,
    'up':       0,
}


class Pico(Serial):

    def __init__(self, port='/dev/ttyACM0', outfile=sys.stderr, queue=None):
        self.__oufile = outfile
        self.__queue = queue
        self.__work_w_port = 0
        self.log = Log()
        try:
            if port is not None:
                super().__init__(port, timeout=0.2)
                
                t = 0
                while not self.read_all() and t < 1:
                    sleep(0.1)
                    t += 0.1
                assert t < TIMEOUT_OPENING_PORT, f'TimeoutExpired t = {t}'
                self.__work_w_port = 1
            self.state = State()
        except (SerialException, AssertionError) as e:
            self.state = Error('', e)
            self.log(self.state, file=self.__oufile, queue=self.__queue, level=ERROR)
            raise e

    def __repr__(self):
        return f"Pico({self.port})"

    def __update_state(self, ask=True):
        if self.__work_w_port:
            try:
                if ask:
                    self.write(b'{}\r\n')
                sleep(0.01)
                out = self.read_all().decode('ascii').strip()
                self.log(f'<< {out}', file=self.__oufile, queue=self.__queue)
                out = re.findall(r'\{[^}]{3,}\}', out)[0]
                out = loads(out)
                return out
            except (SerialException, JSONDecodeError) as e:
                self.state = Error('', e)
                self.log(self.state, file=self.__oufile, queue=self.__queue)
                raise e
        else:
            return DEFAULTS


    def get_current(self):
        try:
            return self.__update_state()['current']
        except KeyError as e:
            self.state = Error('', e)
            self.log(self.state, file=self.__oufile, queue=self.__queue)
            raise e


    def is_down(self):
        try:
            return self.__update_state()['down']
        except KeyError as e:
            self.state = Error('', e)
            self.log(self.state, file=self.__oufile, queue=self.__queue)
            raise e


    def is_up(self):
        try:
            return self.__update_state()['up']
        except KeyError as e:
            self.state = Error('', e)
            self.log(self.state, file=self.__oufile, queue=self.__queue)
            raise e


    def erosion(self, x):
        try:
            cmd = '{"erosion": %s}\r\n' % x
            self.log(f'>> {cmd.strip()}', file=self.__oufile, queue=self.__queue)
            if self.__work_w_port:
                self.write(bytes(cmd,'ascii'))
            sleep(0.1)
            self.read_all()
            self.state = Ok(cmd)
        except Exception as e:
            self.state = Error('', e)


    def position(self, x):
        # POSITIONS = ['up', 'down', 'middle', 'none']
        try:
            cmd = '{"position": "%s"}\r\n' % x
            self.log(f'>> {cmd.strip()}', file=self.__oufile, queue=self.__queue)
            if self.__work_w_port:
                self.write(bytes(cmd,'ascii'))
            sleep(0.1)
            self.read_all()
            self.state = Ok(cmd)
        except Exception as e:
            self.state = Error('', e)


    def pump(self, x):
        try:
            cmd = '{"pump": %s}\r\n' % x
            self.log(f'>> {cmd.strip()}', file=self.__oufile, queue=self.__queue)
            if self.__work_w_port:
                self.write(bytes(cmd,'ascii'))
            sleep(0.1)
            self.read_all()
            self.state = Ok(cmd)
        except Exception as e:
            self.state = Error('', e)


    def pump_in(self, x):
        try:
            cmd = '{"pump_in": %s}\r\n' % x 
            self.log(f'>> {cmd.strip()}', file=self.__oufile, queue=self.__queue)
            if self.__work_w_port:
                self.write(bytes(cmd,'ascii'))
            sleep(0.1)
            self.read_all()
            self.state = Ok(cmd)
        except Exception as e:
            self.state = Error('', e)


    def pump_out(self, x):
        try:
            cmd = '{"pump_out": %s}\r\n' % x
            self.log(f'>> {cmd.strip()}', file=self.__oufile, queue=self.__queue)
            if self.__work_w_port:
                self.write(bytes(cmd,'ascii'))
            sleep(0.1)
            self.read_all()
            self.state = Ok(cmd)
        except Exception as e:
            self.state = Error('', e)

    
    def reset(self):
        try:
            cmd = '{"reset":1}\r\n'
            self.log(f'>> {cmd.strip()}', file=self.__oufile, queue=self.__queue)
            if self.__work_w_port:
                self.write(bytes(cmd,'ascii'))
            sleep(2)
            self.read_all()
            self.state = Ok(cmd)
        except Exception as e:
            self.state = Error('', e)


    def test(self):
        try:
            cmd = '{"test":1}\r\n'
            self.log(f'>> {cmd.strip()}', file=self.__oufile, queue=self.__queue)
            if self.__work_w_port:
                self.write(bytes(cmd,'ascii'))
            sleep(2)
            out = self.read_all()
            self.log(f'<< {out}', file=self.__oufile, queue=self.__queue)
            self.state = Ok(cmd)
        except Exception as e:
            self.state = Error('', e)


    def is_ready(self):
        if self.__work_w_port: 
            out = self.__update_state()
            return out 
        self.log('<< emulated!', file=self.__oufile, queue=self.__queue)
        return DEFAULTS

if __name__ == '__main__':
    from queue import Queue

    log = Log()
    q = Queue()

    try:
        p = Pico(outfile=open('/tmp/log','w'), queue=q)
    except Exception:
        log('[INFO] работа в режиме эмуляции')
        p = Pico(port=None, outfile=open('/tmp/log','w'), queue=q)

#    p.test(), sleep(1), print(1, q.get())

#    print(2, p.get_current())
#    print(3, p.is_down())
#    print(4, p.is_up())
#    p.erosion(1), print(5, q.get())
    #sleep(3)
    p.position("up"), print(5, q.get())
#    sleep(10)
    #p.pump(1), print(6, q.get())
    # p.pump_in(1), print(7, q.get())
    # p.pump_out(0), print(8, q.get())
#    p.reset(), print(9, q.get())
    #p.is_ready(), print(10, q.get())
    
    
