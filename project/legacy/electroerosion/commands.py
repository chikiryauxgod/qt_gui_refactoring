import sys
from queue import Queue, Empty
from threading import Thread, Event
from robot import Robot
from time import time, sleep

DT = 0.5

class CommandThread(Thread):

    def __init__(self, q_cmd, q_result, robot, debug=False):
        super().__init__()
        self.__dt, t = 0,0
        self.stop_event = Event()

        self.robot = robot

        self.__do_debug = debug
        self.__configure_queues(q_cmd, q_result)


    def __configure_queues(self, q_cmd, q_result):
        self.cmd = None
        self.q_cmd = q_cmd
        self.q_result = q_result


    def run(self):

        while 1:
            if self.stop_event.is_set():
                print("Gracefully stopping..", file=sys.stderr)
                break
            if self.__do_debug: print(f'{time()}, {self.cmd}', file=sys.stderr)
            try:
                self.cmd = self.q_cmd.get(block=False)
                if 'j' in self.cmd:
                    try:
                        self.robot.set_joint_pos(joints=self.cmd['j'])
                        j_values = self.robot.get_joint_pos()
                        print(f"j--> {j_values}", file=sys.stderr)
                        self.q_result.put({'response': j_values})
                        # self.cmd = None
                    except AssertionError as e:
                        self.q_result.put({'error': str(e)})
                elif 'gj' in self.cmd:
                    try:
                        j_values = self.robot.get_joint_pos()
                        print(f"g--> {j_values}", file=sys.stderr)
                        self.q_result.put({'response': j_values})
                        # self.cmd = None
                    except AssertionError as e:
                        self.q_result.put({'error': str(e)})
                elif 'exit' in self.cmd:
                    self.stop_event.set()
                    # self.cmd = None
            except Empty:
                pass

            sleep(DT)
    