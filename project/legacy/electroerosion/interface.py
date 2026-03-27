
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 19:10:39 2020

@author: dan
"""
import matplotlib
import numpy as np
# import time

# from matplotlib import pyplot as plt
# from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
# from tkinter import filedialog as fd
from time import sleep
from queue import Queue, Empty
from chain import my_chain
from commands import CommandThread
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from robot import Robot
from tkinter import BOTH, X, Y, Button, DoubleVar, Entry, IntVar, StringVar, Text, Listbox, Frame, HORIZONTAL, LabelFrame, Label, LEFT, RIGHT, BOTTOM, Scale, Tk, TOP
from tkinter import X as by_X, Y as by_Y
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from gauge import Gauge

matplotlib.use("TkAgg")  # NOTE: import order matters

X, Y, Z, rX, rY, rZ = 0, 1, 2, 3, 4, 5

CURA_DIR_NAME = 'cura'
DEFAULT_SPEED = 30

class RobotWindow(Tk):

    def plot(self, point=[0,0,0], rotation=[0,0,0]):
  
        # the figure that will contain the plot 
        # fig = Figure(figsize = (5, 5), 
        #              dpi = 100) 
        self.plot2 = self.fig.add_subplot(111, projection='3d')

        ik = my_chain.inverse_kinematics(point, rotation, 'Z')
        my_chain.plot(ik, self.plot2)
        # pk = my_chain.forward_kinematics(ik)[:3, 3]
        
        self.canvas.draw()
        # matplotlib.pyplot.show()
    def select_file(self):
        self.filetypes = (
            ('STL', '*.stl'),
        )

        self.filename = fd.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=self.filetypes)

    def do_stl_process(self):
        pass

    def repeat_stl_process(self):
        pass

    def do_stl_process_2(self):
        pass

    def repeat_stl_process_2(self):
        pass

    def to_gcode(self):
        pass

    def start_cura(script='cura_run.sh', cura_dir=CURA_DIR_NAME, out_file='object.gcode'):
        status = 0
        res = {}
        cura_path = '/'.join(os.path.abspath(BASE_DIR).split('/')[:-1] + [cura_dir])
        try:
            subprocess.call(['bash', f'{cura_path}/{script}'])
            time.sleep(3)
            app_cur_dir = ''
            if 'dev_settings' in os.getenv('DJANGO_SETTINGS_MODULE'):
                app_cur_dir = 'core/'
            web_interface_gcode_path = f'{app_cur_dir}static/3d_models/{out_file}'
            print(web_interface_gcode_path)
            shutil.move(f'{cura_path}/{out_file}', web_interface_gcode_path)
            res = {'gcode': f'/static/3d_models/{out_file}'} # no {app_cur_dir} because static url is the same in browser for dev and prod
        except FileNotFoundError as e:
            res['error'] = f'File not found error! Калбаски снова нас обманули!!: {e}'
        except OSError as e:
            res['error'] = f'Seems that dest is not writable! Опять калабасики...: {e}'
        except IOError as e:
            res['error'] = f'IO error is here! Калбаски снова нас обманули!!: {e}'
        except subprocess.CalledProcessError as e:
            res['error'] = f'CalledProcessError -> CuraEngine error: {e}'
        except subprocess.SubprocessError as e:
            res['error'] = f'SubprocessError: {e}'
        except subprocess.TimeoutExpired as e:
            res['error'] = f'TimeoutExpired: {e}'
        except Exception as e:
            res['error'] = f'Aaaaa калбаска фаталити еррор!!: {e}'

    #     return res

    def go_home(self):
        # set robot to initial pos
        self.robot.set_joint_pos((0,0,0,0,0,0))
        self.q_cmd.put({'gj': 'get'})
        res = self.q_result.get()
        # print(res)
        [self.joints[j].set(res['response'][j]) for j in range(len(self.joints))]
        pk = my_chain.forward_kinematics([0]+list(res['response'])+[0])
        pos = pk[:3,3]
        print(pos)

        [self.position[i].set(pos[i]) for i in range(len(pos))]
      

    def __configure(self, values=[0,0,0,0,0,0,], joints=[0,0,0,0,0,0,]):
        self.bind('<Escape>', lambda x : self.destroy())        
        # my_chain.__repr__()

        self.speed = DEFAULT_SPEED
        try:
            self.robot = Robot()
        except Exception:
            self.robot = Robot(port=None)

        self.q_cmd = Queue()
        self.q_result = Queue()

        self.commands_thread = CommandThread(q_cmd=self.q_cmd, q_result=self.q_result, robot=self.robot, debug=True)
        self.commands_thread.start()


        self.joints = (DoubleVar(self, value = 0, name = 'J1'), 
                    DoubleVar(self, value = 0, name = 'J2'), 
                    DoubleVar(self, value = 0, name = 'J3'),
                    DoubleVar(self, value = 0, name = 'J4'), 
                    DoubleVar(self, value = 0, name = 'J5'), 
                    DoubleVar(self, value = 0, name = 'J6'))

        self.position = (DoubleVar(self, value = 0, name = 'Уст. Х'),
                    DoubleVar(self, value = 0, name = 'Уст. Y'),
                    DoubleVar(self, value = 0, name = 'Уст. Z'),
                    )
        self.rotation = (DoubleVar(self, value = 0, name = 'Уст. rХ'),
                    DoubleVar(self, value = 0, name = 'Уст. rY'),
                    DoubleVar(self, value = 0, name = 'Уст. rZ'),
                    )
        
        self.go_home()
        # [self.rotation[i].set(rot[i]) for i in range(len(rot))]

        # self.X = DoubleVar(self, value = 0, name = 'Уст. Х')
        # self.Y = DoubleVar(self, value = 0, name = 'Уст. Y')
        # self.Z = DoubleVar(self, value = 0, name = 'Уст. Z')
        # self.rX = DoubleVar(self, value = 0, name = 'Уст. rХ')
        # self.rY = DoubleVar(self, value = 0, name = 'Уст. rY') 
        # self.rZ = DoubleVar(self, value = 0, name = 'Уст. rZ')

        # @property
        # def x_coord(self):
        #     return self.X.get()
     
        # @x_coord.setter
        # def x_coord(self, x):
        #     self.X = x

        # Errosion settings
        self.current = DoubleVar(self, value=0, name='Ток')

        self.update_graph = False
        # self.R = DoubleVar(self, value = 0)
        # self.P = DoubleVar(self, value = 0)
        
        # self.mpos = (DoubleVar(self, value = 0, name = 'Маш. Х'), 
        #              DoubleVar(self, value = 0, name = 'Маш. Y'), 
        #              DoubleVar(self, value = 0, name = 'Маш. Z'))
        # self.wpos = (DoubleVar(self, value = 0, name = 'Мир. Х'), 
        #              DoubleVar(self, value = 0, name = 'Мир. Y'), 
        #              DoubleVar(self, value = 0, name = 'Мир. Z'))
        # self.speed = IntVar(self, value=50, name ='')
        # self.topFrame = Frame(self, height=20) 
        self.title("Управление роботом")       
        self.labelFrame = LabelFrame(self, text='Управление')
        self.contFrame = Frame(self, width=400, height=200)
        # self.label = Label(text="")
        # self.label.pack()
        self.plotFrame = LabelFrame(self.contFrame, width=200, height=200, text='График')
        self.workFrame = LabelFrame(self.contFrame, width=200, height=200, text='Позиционирование')
        self.tabControlWork = ttk.Notebook(self.workFrame)
        self.tab1 = ttk.Frame(self.tabControlWork)
        self.tab2 = ttk.Frame(self.tabControlWork)
        self.tabControlWork.add(self.tab1, text='Координаты')
        self.tabControlWork.add(self.tab2, text='Звенья')

        self.tabControlPlot = ttk.Notebook(self.plotFrame)
        self.tab3 = ttk.Frame(self.tabControlPlot)
        self.tab4 = ttk.Frame(self.tabControlPlot)
        self.tab7 = ttk.Frame(self.tabControlWork)
        self.tabControlPlot.add(self.tab3, text='График')
        self.tabControlPlot.add(self.tab4, text='Терминал')
        self.tabControlWork.add(self.tab7, text='Эрозия')

        ttk.Frame(self.tab1).grid(column=0, row=0, padx=30, pady=30)
        ttk.Frame(self.tab2).grid(column=0, row=0, padx=30, pady=30)
        ttk.Frame(self.tab3).grid(column=0, row=0, padx=30, pady=30)
        ttk.Frame(self.tab4).grid(column=0, row=0, padx=30, pady=30)
        ttk.Frame(self.tab7).grid(column=0, row=0, padx=30, pady=30)

        self.xPosScroll = Scale(self.tab1, orient=HORIZONTAL, from_ = -640.6, to = 640.6, showvalue = 1, variable = self.position[0])
        self.yPosScroll = Scale(self.tab1, orient=HORIZONTAL, from_ = -424, to = 673, showvalue = 1, variable = self.position[1])
        self.zPosScroll = Scale(self.tab1, orient=HORIZONTAL, from_ = 200, to = 1001, showvalue = 1, variable = self.position[2])
        self.xPosRotate = Scale(self.tab1, orient=HORIZONTAL, from_ = 0, to = 359, showvalue = 1, variable = self.rotation[0])
        self.yPosRotate = Scale(self.tab1, orient=HORIZONTAL, from_ = 0, to = 359, showvalue = 1, variable = self.rotation[1])
        self.zPosRotate = Scale(self.tab1, orient=HORIZONTAL, from_ = 0, to = 359, showvalue = 1, variable = self.rotation[2])

        self.j1_pos = Scale(self.tab2, orient=HORIZONTAL, from_ = self.robot.state.mins[0], to = self.robot.state.maxs[0], showvalue = 1, variable = self.joints[0])
        self.j2_pos = Scale(self.tab2, orient=HORIZONTAL, from_ = self.robot.state.mins[1], to = self.robot.state.maxs[1], showvalue = 1, variable = self.joints[1])
        self.j3_pos = Scale(self.tab2, orient=HORIZONTAL, from_ = self.robot.state.mins[2], to = self.robot.state.maxs[2], showvalue = 1, variable = self.joints[2])
        self.j4_pos = Scale(self.tab2, orient=HORIZONTAL, from_ = self.robot.state.mins[3], to = self.robot.state.maxs[3], showvalue = 1, variable = self.joints[3])
        self.j5_pos = Scale(self.tab2, orient=HORIZONTAL, from_ = self.robot.state.mins[4], to = self.robot.state.maxs[4], showvalue = 1, variable = self.joints[4])
        self.j6_pos = Scale(self.tab2, orient=HORIZONTAL, from_ = self.robot.state.mins[5], to = self.robot.state.maxs[5], showvalue = 1, variable = self.joints[5])

        # self.current_indicator = Gauge(self.tab7)
        self.currentControl = Scale(self.tab7, orient=HORIZONTAL, from_=0, to=10, showvalue=1, variable=self.current)

        self.paramsFrame = LabelFrame(self.tab1, height=50, text='Выбор режима')
        self.tabControlParams = ttk.Notebook(self.paramsFrame)
        self.tab5 = ttk.Frame(self.tabControlParams)
        self.tab6 = ttk.Frame(self.tabControlParams)
        self.tabControlParams.add(self.tab5, text='STL')
        self.tabControlParams.add(self.tab6, text='Углы и глубина')
        ttk.Frame(self.tab5).grid(column=0, row=12, padx=30, pady=30)
        ttk.Frame(self.tab6).grid(column=0, row=12, padx=30, pady=30)


        items = ['Ст45', 'АМГ30']
        self.var = StringVar()
        self.var.set(items)
        self.lb = Listbox(self.tab1, listvariable=self.var)
        # self.lb_label = Label(self.lb, )
        self.lb_label = Label(self.tab1, text='Выбор материала')
        # self.filename = fd.askopenfilename()
        self.open_button = Button(
            self.tab5,
            text='Открыть STL',
            command=self.select_file
        )

        self.do_button = Button(
            self.tab6,
            text='Выполнить',
            command=self.do_stl_process
        )
        self.repeat_button = Button(
            self.tab6,
            text='Повтор',
            command=self.repeat_stl_process
        )

        self.do_button_2 = Button(
            self.tab5,
            text='Выполнить',
            command=self.do_stl_process
        )
        self.repeat_button_2 = Button(
            self.tab5,
            text='Повтор',
            command=self.repeat_stl_process
        )

        self.to_gcode_button = Button(
            self.tab5,
            text='Преобразовать в gcode',
            command=self.to_gcode
        )

        self.eq_0 = IntVar(
            self.tab6,
            value=0, name='Rx:', 
            # maxvalue=45, minvalue=-45
        )
        self.eq_label_0 = Label(self.tab6, text='Rx:')
        self.eq_label_entry_0 = Entry(self.tab6, textvariable=self.eq_0)
        self.eq_1 = IntVar(
            self.tab6,
            value=0, name='Ry:', 
            # maxvalue=45, minvalue=-45
        )
        self.eq_label_1 = Label(self.tab6, text='Ry:')
        self.eq_label_entry_1 = Entry(self.tab6, textvariable=self.eq_1)
        self.eq_2 = IntVar(
            self.tab6,
            value=0, name='D: ', 
            # maxvalue=350
        )
        self.eq_label_2 = Label(self.tab6, text='D: ')
        self.eq_label_entry_2 = Entry(self.tab6, textvariable=self.eq_2)
        self.stl_progress = ttk.Progressbar(self.tab6, orient="horizontal", length=150, value=20)
        self.stl_progress_2 = ttk.Progressbar(self.tab5, orient="horizontal", length=150, value=40)
    # showinfo(
    #     title='Selected File',
    #     message=filename
    # )

        # self.xPosScroll = Scale(self.tab1, orient=HORIZONTAL, from_ = 0, to = 255, showvalue = 1, variable = self.pos[X])
        # self.yPosScroll = Scale(self.tab1, orient=HORIZONTAL, from_ = 0, to = 255, showvalue = 1, variable = self.pos[Y])
        # self.zPosScroll = Scale(self.tab1, orient=HORIZONTAL, from_ = 0, to = 255, showvalue = 1, variable = self.pos[Z])
        # self.xPosRotate = Scale(self.tab1, orient=HORIZONTAL, from_ = 0, to = 255, showvalue = 1, variable = self.pos[rX])
        # self.yPosRotate = Scale(self.tab1, orient=HORIZONTAL, from_ = 0, to = 255, showvalue = 1, variable = self.pos[rY])
        # self.zPosRotate = Scale(self.tab1, orient=HORIZONTAL, from_ = 0, to = 255, showvalue = 1, variable = self.pos[rZ])
        # self.canvas     = Canvas(self.workFrame, width=640, height=480, bg='white')

        # self.setTopLeftCornerBtn = Button(self.contFrame, text = 'Верхний левый угол')
        # self.setBottomRigthCornerBtn = Button(self.contFrame, text = 'Нижний правый угол')
        # self.cncStopBtn = Button(self.contFrame, text = 'Стоп')
        self.setPos = Button(master=self.tab1, command=self.get_controls, height=2, width=10, text='Занять позицию')
        self.goHome = Button(master=self.tab1, command=self.go_home, height=2, width=10, text='Домой (в 0)')
        self.goJHome = Button(master=self.tab2, command=self.go_home, height=2, width=10, text='Домой (в 0)')
        self.setJPos = Button(master=self.tab2, command=self.get_controls, height=2, width=10, text='Занять позицию')
        self.speedControl = Scale(self.contFrame, orient=HORIZONTAL, length=200, from_=0, to=100, tickinterval=5,
               resolution=5)

        # self.robot = Robot()
        
        # self.cncMoveFrame.bind('', set_speed)


        # for p in P:
        #     robot.set_joint_pos(p)
        #     print(robot.get_joint_pos())


        # robot.set_joint_pos((0,0,0,0,0,0))
        # print(robot.get_joint_pos())

        self.fig = Figure(figsize=(5, 5), dpi=100)
        # self.y = [i**2 for i in range(101)]
        # self.plot1 = self.fig.add_subplot(111)
        # self.plot1.plot(self.y)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab3)
        # self.canvas.draw()
        # self.toolbar = NavigationToolbar2Tk(self.canvas, self.tab3)
        # self.toolbar.update()
        self.canvas.get_tk_widget().grid(column=0, row=0, padx=30, pady=30)

        # self.plot_button = Button(master=self.tab3, command=self.plot, height = 2, width = 10, text = "Plot")
        # self.exitBtn.grid(column=0, row=0)
        self.setPos.grid(column=3, row=4)
        self.setJPos.grid(column=4, row=4)
        self.goHome.grid(column=5, row=4)
        self.goJHome.grid(column=6, row=4)
        self.lb_label.grid(column=0, row=5)
        self.lb.grid(column=0, row=6)
        self.open_button.grid(column=3, row=5)
        self.to_gcode_button.grid(column=3, row=6)
        self.do_button_2.grid(column=3, row=7)
        self.stl_progress_2.grid(column=3, row=8)
        self.repeat_button_2.grid(column=3, row=9)
        # self.eq_label.grid(column=3, row=6)
        self.eq_label_0.grid(column=2, row=6)
        self.eq_label_entry_0.grid(column=4, row=6)
        self.eq_label_1.grid(column=2, row=7)
        self.eq_label_entry_1.grid(column=4, row=7)
        self.eq_label_2.grid(column=2, row=8)
        self.eq_label_entry_2.grid(column=4, row=8)
        self.do_button.grid(column=2, row=9)
        self.stl_progress.grid(column=2, row=10)
        self.repeat_button.grid(column=2, row=11)

        self.labelFrame.pack(side=TOP,  expand=0, fill=BOTH)
        self.contFrame.pack(side=TOP, expand=0, fill=by_Y)
        self.speedControl.pack(side=TOP, expand=1, fill=BOTH)
        self.plotFrame.pack(side=LEFT, expand=1, fill=BOTH)
        self.workFrame.pack(side=RIGHT, expand=1, fill=BOTH)
        self.paramsFrame.grid(column=0, row=12)
        self.tabControlWork.pack(expand=1, fill=BOTH)
        self.tabControlPlot.pack(expand=1, fill=BOTH)
        self.tabControlParams.pack(expand=1, fill=BOTH)
        self.currentControl.grid(column=0, row=0)
        self.xPosScroll.grid(column=0, row=0)
        self.yPosScroll.grid(column=1, row=0)
        self.zPosScroll.grid(column=2, row=0)
        self.xPosRotate.grid(column=0, row=1)
        self.yPosRotate.grid(column=1, row=1)
        self.zPosRotate.grid(column=2, row=1)
        self.j1_pos.grid(column=0, row=0)
        self.j2_pos.grid(column=1, row=0)
        self.j3_pos.grid(column=2, row=0)
        self.j4_pos.grid(column=0, row=1)
        self.j5_pos.grid(column=1, row=1)
        self.j6_pos.grid(column=2, row=1)

    
    def __init__(self):
        super().__init__()
        self.__configure()
        # self.after(100, self.timer)
        self.set_speed(self.speed)
        self.get_speed()
        self.joints_values_old = [0,0,0,0,0,0]
        self.position_old = [0,0,0]
        self.rotation_old = [0,0,0]
        self.config_process = False

    def set_speed(self, speed):
        print(speed)
        self.robot.set_speed(speed)

    def get_speed(self):
        speed = self.robot.get_speed()
        self.speedControl.set(speed)

    def exit(self):
        self.q_cmd.put({'exit': 'exit'})
        sleep(2)
        try:
            res = self.q_result.get(block=False)
        except Empty:
            pass
    
    def get_controls(self):
            speed = self.speedControl.get()
            try:
                joints_values_current = [j.get() for j in self.joints]
                if joints_values_current != self.joints_values_old:
                    self.update_graph = True
                    self.q_cmd.put({'j': joints_values_current})
                    j_values = self.q_result.get(block=False)

                    print(j_values)
                    [self.joints[j].set(j_values[j]) for j in range(len(self.joints))]
                    self.joints_values_old = joints_values_current
            except Exception as e:
                print(str(e))

            if speed != self.speed:
                print(speed)
                self.set_speed(speed)
                self.speed = speed

    ######### TESTTTT ITTT!!!
            position_current = [j.get() for j in self.position]
            rotation_current = [j.get() for j in self.rotation]
            print("=================================")
            print(position_current, rotation_current)
            print("=================================")
            print(self.position_old, self.rotation_old)
            print("=================================")

            if position_current != self.position_old or rotation_current != self.rotation_old:
                self.update_graph = True
                ik = my_chain.inverse_kinematics(position_current, rotation_current, 'Z')
                joints = [ round(x,4) for x in np.degrees(ik) ][1:7]
                print(111, joints)
                self.q_cmd.put({'j': joints})
                try:
                    j_values = self.q_result.get(timeout=2)
                except Empty:
                    print(f"[ WARNING ] Empty response for cmd j: {joints}.")
                print(f"[ INFO ] j_values: {j_values}")
                try:
                    [self.joints[j].set(j_values['response'][j]) for j in range(len(self.joints))]
                    self.position_old = position_current
                    self.rotation_old = rotation_current
                    print(222, j_values)
                except KeyError:
                    print(j_values['error'])

            if self.update_graph == True:
                self.plot(self.position_old, self.rotation_old)
                self.update_graph = False

            # self.after(1000, self.timer)

    def destroy(self, **kwargs):
        self.exit()
        self.commands_thread.join()
        super().destroy()

    def __del__(self):
        self.destroy()
        
if __name__ == "__main__":
    # from sys import argv
    # print(my_chain)
    robot = RobotWindow()
    robot.mainloop()
    
