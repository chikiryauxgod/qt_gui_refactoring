from board import GP2 as PIN_PUMP_OUT
from board import GP3 as PIN_PUMP_IN
from board import GP4 as PIN_PUMP
from board import GP5 as PIN_EROSION_1
from board import GP6 as PIN_EROSION_2
from board import GP7 as PIN_RESET
from board import GP8 as NC_1
from board import GP9 as NC_2

from board import A0 as PIN_CURRENT
from board import GP22 as NC_3
from board import GP27 as PIN_RED
from board import GP28 as PIN_GREEN

from board import GP20 as CS
from board import GP19 as SCK
from board import GP18 as SI

from digitalio import DigitalInOut, Direction
from analogio import AnalogIn
from time import sleep
from json import dumps, loads

OUTS = {
    'nc_1': NC_1, 
    'nc_2': NC_2, 

    'pin_erosion_1': PIN_EROSION_1, 
    'pin_erosion_2': PIN_EROSION_2, 
    'pin_pump':      PIN_PUMP, 
    'pin_pump_in':   PIN_PUMP_IN, 
    'pin_pump_out':  PIN_PUMP_OUT, 
    'pin_reset':     PIN_RESET, 

    'cs':  CS, 
    'sck': SCK, 
    'si':  SI,
}

INS = {
    'nc_3':      NC_3,
    'pin_green': PIN_GREEN,
    'pin_red':   PIN_RED,
}

ANALOGUES = {
    'pin_current': PIN_CURRENT,
}

POSITIONS = ['up', 'down', 'middle', 'none']

class WrongStateError(ValueError):
    pass

class Board():

    K = [ 
          0.88644944,  
         -9.07677325,  
         38.04803849, 
        -83.64163218,
        102.80379551, 
        -69.69227352,  
         24.06916283, 
         -2.68196174,
          0.1758256,
    ]


    def __init__(self, ins, outs, analogues):
        self.__set_pins(ins, outs, analogues)

        self.__state = {
            'current':  0,
            'voltage':  0,

            'down':     0,
            'up':       0,
            
            'erosion':  0,
            'position': 0,
            
            'pump':     0,
            'pump_in':  0,
            'pump_out': 0,
            
            'reset':    0,
            'test':     0,
        }

        self.__state_checks = {
            'current':  lambda x: 0 <= x <= 10,
            'voltage':  lambda x: 0 <= x <= 3.3,
            
            'down':     lambda x: x in [0, 1],
            'up':       lambda x: x in [0, 1],
            
            'erosion':  lambda x: x in [0, 1],
            'position': lambda x: x in POSITIONS,
            
            'pump':     lambda x: x in [0, 1],
            'pump_in':  lambda x: x in [0, 1],
            'pump_out': lambda x: x in [0, 1],
            
            'reset':    lambda x: x in [0, 1],
            'test':     lambda x: x in [0, 1],
        }


    def __set_pins(self, ins, outs, analogues):
        self.__outs = {}
        for k, v in outs.items():
            y = DigitalInOut(v)
            y.direction = Direction.OUTPUT
            y.value = 1
            self.__outs.update({k: y})

        self.__ins = {}
        for k, v in ins.items():
            y = DigitalInOut(v)
            y.direction = Direction.INPUT
            self.__ins.update({k: y})

        self.__analogues = {}
        for k, v in analogues.items():
            y = AnalogIn(v)
            self.__analogues.update({k: y})


    def __read(self):
        voltage = self.__adc_to_voltage()
        current = self.__voltage_to_current(voltage)
        is_green = int(not self.__ins['pin_green'].value)
        is_red = int(not self.__ins['pin_red'].value)

        return voltage, current, is_green, is_red


    def __adc_to_voltage(self):
        return (65535 - self.__analogues['pin_current'].value) / 65535 * 3.3

    
    def __voltage_to_current(self, x):
        if x < 0.18:
            s = 0
        else:
            s = 0
            degree = len(self.K) - 1
            for power in range(degree, -1, -1):
                s += self.K[degree - power] * x ** power
        return s


    def __check_input(self, state):
        for k, v in state.items():
            try:
                f = self.__state_checks[k]
                if not f(v): 
                    raise WrongStateError(f'k = {k}, v = {v}')
            except KeyError:
                raise WrongStateError(f'state = {state}')


    def __reset(self):
        self.__set_position('none')
        self.__erosion(0)
        self.__pump(0)
        self.__pump_in(0)
        self.__pump_out(0)
        self.__state.update({
            "reset":0,
            "erosion": 0,
            "pump": 0,
            "pump_in": 0,
            "pump_out": 0,
        })
        sleep(0.1)
        x = self.__outs['pin_reset']
        x.value = 0
        sleep(0.5)
        x.value = 1
        sleep(0.1)


    def __erosion(self, v):
        self.__outs['pin_erosion_1'].value = not v
        self.__outs['pin_erosion_2'].value = not v
        sleep(0.1)


    def __pump(self, v):
        self.__outs['pin_pump'].value = not v
        sleep(0.1)


    def __pump_in(self, v):
        self.__outs['pin_pump_in'].value = not v
        sleep(0.1)


    def __pump_out(self, v):
        self.__outs['pin_pump_out'].value = not v
        sleep(0.1)


    def __set_position(self, v):
        do_position = {
            'up'    : {'pin_erosion_1':0, 'pin_erosion_2':1, 'nc_1': 0, 'nc_2': 0},
            'middle': {'pin_erosion_1':1, 'pin_erosion_2':1, 'nc_1': 0, 'nc_2': 1},
            'down'  : {'pin_erosion_1':1, 'pin_erosion_2':1, 'nc_1': 0, 'nc_2': 0},
            'none'  : {'pin_erosion_1':0, 'pin_erosion_2':0, 'nc_1': 0, 'nc_2': 0},
        }

        for pin in do_position[v]:
            self.__outs[pin].value = not do_position[v][pin]
        sleep(0.1)


    def __write(self, state):
        for k, v in state.items():
            if k == 'reset' and v: 
                self.__reset()
            if k == 'erosion':     
                self.__erosion(v)
            if k == 'pump':        
                self.__pump(v)
            if k == 'pump_in':     
                self.__pump_in(v)
            if k == 'pump_out':    
                self.__pump_out(v)
            if k == 'position':    
                self.__set_position(v)
            if k == 'test':
                self.__test()


    def __update(self, state):
        try:
            self.__check_input(state)
            self.__state.update(state)
            self.__write(state)
            error = 'none'            
        except WrongStateError as e:
            error = str(e)
        finally:
            voltage, current, is_green, is_red = self.__read()

        self.__state.update({
            'voltage': voltage,
            'current': current,
            'down':    is_red,
            'up':      is_green,
            'error':   error,
        })

    
    def __test(self):
        for v in POSITIONS:
            self.__set_position(v)
        self.__erosion(1)
        self.__pump(1)
        self.__pump_in(1)
        self.__pump_out(1)
        self.__reset()
        

    def update(self, state):
        self.__update(state)
        return self.__state


controller_board = Board(INS, OUTS, ANALOGUES)

while True:
    try:
        state = loads(input('state = '))
    except ValueError:
        continue
    state = controller_board.update(state)
    print(dumps(state).replace(',',',\n'))
    
