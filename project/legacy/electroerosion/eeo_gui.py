import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk

# Импорт ваших модулей (адаптировать при необходимости)
from robot import Robot
from pico import Pico

# Константы из electroerosion.py
X0 = 430.0
Y0 = 0.0
Z0 = 277.0
D_E = 2

class VideoStream:
    def __init__(self, video_label):
        self.video_label = video_label
        self.cap = cv2.VideoCapture(0)
        self.update()
        
    def update(self):
        ret, frame = self.cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.video_label.after(10, self.update)
        
    def release(self):
        self.cap.release()

class ErosionProcessTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_step = 0
        self.create_widgets()
        
    def create_widgets(self):
        # Создаем фреймы для каждого шага
        self.step_frames = []
        
        # Шаг 1: Установка начальной позиции
        step1_frame = ttk.Frame(self)
        self.create_step1(step1_frame)
        self.step_frames.append(step1_frame)
        
        # Шаг 2: Параметры обработки
        step2_frame = ttk.Frame(self)
        self.create_step2(step2_frame)
        self.step_frames.append(step2_frame)
        
        # Шаг 3: Запуск процесса
        step3_frame = ttk.Frame(self)
        self.create_step3(step3_frame)
        self.step_frames.append(step3_frame)
        
        # Показать первый шаг
        self.show_step(0)
        
        # Кнопки навигации
        nav_frame = ttk.Frame(self)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        self.prev_btn = ttk.Button(nav_frame, text="Назад", command=self.prev_step)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(nav_frame, text="Далее", command=self.next_step)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = ttk.Button(nav_frame, text="Отмена", command=self.controller.safe_finish)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        self.emergency_btn = ttk.Button(nav_frame, text="Аварийная остановка", 
                                       command=self.controller.emergency_stop,
                                       style="Emergency.TButton")
        self.emergency_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_step1(self, parent):
        # Видеопоток
        video_frame = ttk.LabelFrame(parent, text="Видеопоток с камеры")
        video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.video_label = ttk.Label(video_frame)
        self.video_label.pack(padx=5, pady=5)
        
        # Запуск видеопотока
        self.video_stream = VideoStream(self.video_label)
        
        # Управление положением
        control_frame = ttk.LabelFrame(parent, text="Управление положением робота")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        axes = ['X', 'Y', 'Z']
        self.position_vars = {}
        self.position_entries = {}
        
        for i, axis in enumerate(axes):
            frame = ttk.Frame(control_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            label = ttk.Label(frame, text=f"{axis} (мм):", width=10)
            label.pack(side=tk.LEFT)
            
            var = tk.DoubleVar(value=getattr(self.controller, f'{axis}0', 0))
            self.position_vars[axis] = var
            
            entry = ttk.Entry(frame, textvariable=var, width=10)
            entry.pack(side=tk.LEFT, padx=5)
            self.position_entries[axis] = entry
            
            # Кнопки для изменения положения
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(side=tk.RIGHT)
            
            minus_btn = ttk.Button(btn_frame, text="-", width=3,
                                  command=lambda a=axis: self.change_position(a, -1))
            minus_btn.pack(side=tk.LEFT, padx=2)
            
            plus_btn = ttk.Button(btn_frame, text="+", width=3,
                                 command=lambda a=axis: self.change_position(a, 1))
            plus_btn.pack(side=tk.LEFT, padx=2)
            
            # Привязка для непрерывного движения при зажатии
            minus_btn.bind("<ButtonPress>", lambda e, a=axis, d=-1: self.start_continuous_move(a, d))
            minus_btn.bind("<ButtonRelease>", lambda e: self.stop_continuous_move())
            plus_btn.bind("<ButtonPress>", lambda e, a=axis, d=1: self.start_continuous_move(a, d))
            plus_btn.bind("<ButtonRelease>", lambda e: self.stop_continuous_move())
    
    def create_step2(self, parent):
        # Параметры обработки
        params_frame = ttk.LabelFrame(parent, text="Параметры электроэрозионной обработки")
        params_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        parameters = [
            ('Толщина электрода (мм)', 'electrode_diameter', 2.0, 0.1, 10.0),
            ('Длина электрода (мм)', 'electrode_length', 100.0, 10.0, 500.0),
            ('Время прожига (с)', 'erosion_time', 10.0, 1.0, 60.0),
            ('Время поднятия электрода (с)', 'erosion_up_time', 5.0, 1.0, 30.0),
            ('Глубина прожига (мм)', 'erosion_depth', 0.1, 0.01, 1.0)
        ]
        
        self.param_vars = {}
        
        for i, (label, name, default, min_val, max_val) in enumerate(parameters):
            frame = ttk.Frame(params_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=label, width=25).pack(side=tk.LEFT)
            
            var = tk.DoubleVar(value=default)
            self.param_vars[name] = var
            
            spinbox = ttk.Spinbox(frame, from_=min_val, to=max_val, textvariable=var, 
                                 increment=0.1 if max_val > 10 else 0.01, width=10)
            spinbox.pack(side=tk.RIGHT)
        
        # Схема параметров (заглушка)
        scheme_label = ttk.Label(params_frame, text="Схема параметров электроэрозии")
        scheme_label.pack(pady=10)
        
        # Здесь можно добавить изображение со схемой
        # scheme_image = ImageTk.PhotoImage(Image.open("scheme.png"))
        # scheme_canvas = ttk.Label(params_frame, image=scheme_image)
        # scheme_canvas.pack()
    
    def create_step3(self, parent):
        # Выбор файла
        file_frame = ttk.Frame(parent)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_frame, text="G-code файл:").pack(side=tk.LEFT)
        
        self.file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_var, width=40).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(file_frame, text="Обзор", command=self.select_file).pack(side=tk.LEFT)
        
        # Прогресс бар
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(progress_frame, text="Прогресс:").pack(side=tk.LEFT)
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.time_label = ttk.Label(progress_frame, text="Осталось: --:--")
        self.time_label.pack(side=tk.RIGHT)
        
        # Текущие параметры
        status_frame = ttk.LabelFrame(parent, text="Текущие параметры")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text = tk.Text(status_frame, height=10, width=50)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_btn = ttk.Button(control_frame, text="Запуск", command=self.start_erosion)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = ttk.Button(control_frame, text="Пауза", state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Стоп", command=self.stop_erosion)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
    
    def show_step(self, step_index):
        # Скрыть все шаги
        for frame in self.step_frames:
            frame.pack_forget()
        
        # Показать выбранный шаг
        self.step_frames[step_index].pack(fill=tk.BOTH, expand=True)
        self.current_step = step_index
        
        # Обновить состояние кнопок навигации
        self.prev_btn.config(state=tk.NORMAL if step_index > 0 else tk.DISABLED)
        
        if step_index < len(self.step_frames) - 1:
            self.next_btn.config(text="Далее")
        else:
            self.next_btn.config(text="Завершить", state=tk.DISABLED)
    
    def next_step(self):
        if self.current_step < len(self.step_frames) - 1:
            self.show_step(self.current_step + 1)
    
    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def change_position(self, axis, delta):
        current = self.position_vars[axis].get()
        new_value = current + delta
        self.position_vars[axis].set(new_value)
        self.controller.set_coord_pos(
            x=self.position_vars['X'].get(),
            y=self.position_vars['Y'].get(),
            z=self.position_vars['Z'].get()
        )
    
    def start_continuous_move(self, axis, direction):
        self.continuous_move_data = {'axis': axis, 'direction': direction}
        self.continuous_move()
    
    def stop_continuous_move(self):
        if hasattr(self, 'continuous_move_data'):
            self.after_cancel(self.continuous_move_id)
            del self.continuous_move_data
    
    def continuous_move(self):
        if hasattr(self, 'continuous_move_data'):
            self.change_position(
                self.continuous_move_data['axis'], 
                self.continuous_move_data['direction']
            )
            self.continuous_move_id = self.after(100, self.continuous_move)
    
    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите G-code файл",
            filetypes=[("G-code files", "*.gcode *.nc"), ("All files", "*.*")]
        )
        if filename:
            self.file_var.set(filename)
    
    def start_erosion(self):
        if self.file_var.get():
            self.controller.start_erosion_process(
                self.file_var.get(),
                self.param_vars['electrode_diameter'].get(),
                self.param_vars['electrode_length'].get(),
                self.param_vars['erosion_time'].get(),
                self.param_vars['erosion_up_time'].get(),
                self.param_vars['erosion_depth'].get()
            )
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
    
    def stop_erosion(self):
        self.controller.stop_erosion_process()
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)

class ServiceTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
    
    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка управления по осям XYZ
        xyz_frame = ttk.Frame(notebook)
        self.create_xyz_controls(xyz_frame)
        notebook.add(xyz_frame, text="Управление по осям XYZ")
        
        # Вкладка управления по суставам
        joints_frame = ttk.Frame(notebook)
        self.create_joints_controls(joints_frame)
        notebook.add(joints_frame, text="Управление по суставам")
        
        # Вкладка управления эрозией и водой
        control_frame = ttk.Frame(notebook)
        self.create_erosion_controls(control_frame)
        notebook.add(control_frame, text="Управление эрозией и водой")
        
        # Кнопка аварийной остановки
        emergency_btn = ttk.Button(self, text="АВАРИЙНАЯ ОСТАНОВКА", 
                                  command=self.controller.emergency_stop,
                                  style="Emergency.TButton")
        emergency_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def create_xyz_controls(self, parent):
        axes = ['X', 'Y', 'Z']
        self.xyz_vars = {}
        
        for i, axis in enumerate(axes):
            frame = ttk.LabelFrame(parent, text=f"Ось {axis}")
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Текущее положение
            var = tk.DoubleVar(value=getattr(self.controller, f'{axis}0', 0))
            self.xyz_vars[axis] = var
            
            value_frame = ttk.Frame(frame)
            value_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(value_frame, text="Текущее положение (мм):").pack(side=tk.LEFT)
            ttk.Label(value_frame, textvariable=var, width=10).pack(side=tk.RIGHT)
            
            # Кнопки управления
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(fill=tk.X, padx=5, pady=5)
            
            step_sizes = [0.1, 1, 10]
            
            for j, step in enumerate(step_sizes):
                step_frame = ttk.Frame(btn_frame)
                step_frame.pack(side=tk.LEFT, expand=True)
                
                ttk.Label(step_frame, text=f"Шаг {step} мм").pack()
                
                btn_subframe = ttk.Frame(step_frame)
                btn_subframe.pack()
                
                minus_btn = ttk.Button(btn_subframe, text="-", 
                                      command=lambda a=axis, s=step: self.move_xyz(a, -s))
                minus_btn.pack(side=tk.LEFT, padx=2)
                
                plus_btn = ttk.Button(btn_subframe, text="+", 
                                     command=lambda a=axis, s=step: self.move_xyz(a, s))
                plus_btn.pack(side=tk.LEFT, padx=2)
                
                # Привязка для непрерывного движения
                minus_btn.bind("<ButtonPress>", lambda e, a=axis, s=-step: self.start_continuous_xyz(a, s))
                minus_btn.bind("<ButtonRelease>", lambda e: self.stop_continuous_move())
                plus_btn.bind("<ButtonPress>", lambda e, a=axis, s=step: self.start_continuous_xyz(a, s))
                plus_btn.bind("<ButtonRelease>", lambda e: self.stop_continuous_move())
    
    def create_joints_controls(self, parent):
        joints = ['J0', 'J1', 'J2', 'J3', 'J4', 'J5']
        self.joints_vars = {}
        
        for i, joint in enumerate(joints):
            frame = ttk.LabelFrame(parent, text=f"Сустав {joint}")
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Текущий угол
            var = tk.DoubleVar(value=0)
            self.joints_vars[joint] = var
            
            value_frame = ttk.Frame(frame)
            value_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(value_frame, text="Текущий угол (°):").pack(side=tk.LEFT)
            ttk.Label(value_frame, textvariable=var, width=10).pack(side=tk.RIGHT)
            
            # Кнопки управления
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(fill=tk.X, padx=5, pady=5)
            
            step_sizes = [0.1, 1, 5]
            
            for j, step in enumerate(step_sizes):
                step_frame = ttk.Frame(btn_frame)
                step_frame.pack(side=tk.LEFT, expand=True)
                
                ttk.Label(step_frame, text=f"Шаг {step}°").pack()
                
                btn_subframe = ttk.Frame(step_frame)
                btn_subframe.pack()
                
                minus_btn = ttk.Button(btn_subframe, text="-", 
                                      command=lambda j=joint, s=step: self.move_joint(j, -s))
                minus_btn.pack(side=tk.LEFT, padx=2)
                
                plus_btn = ttk.Button(btn_subframe, text="+", 
                                     command=lambda j=joint, s=step: self.move_joint(j, s))
                plus_btn.pack(side=tk.LEFT, padx=2)
                
                # Привязка для непрерывного движения
                minus_btn.bind("<ButtonPress>", lambda e, j=joint, s=-step: self.start_continuous_joint(j, s))
                minus_btn.bind("<ButtonRelease>", lambda e: self.stop_continuous_move())
                plus_btn.bind("<ButtonPress>", lambda e, j=joint, s=step: self.start_continuous_joint(j, s))
                plus_btn.bind("<ButtonRelease>", lambda e: self.stop_continuous_move())
    
    def create_erosion_controls(self, parent):
        # Управление эрозией
        erosion_frame = ttk.LabelFrame(parent, text="Управление эрозией")
        erosion_frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn_frame = ttk.Frame(erosion_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Включить эрозию", 
                  command=lambda: self.controller.set_erosion(True)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Выключить эрозию", 
                  command=lambda: self.controller.set_erosion(False)).pack(side=tk.LEFT, padx=5)
        
        # Управление водой
        water_frame = ttk.LabelFrame(parent, text="Управление водой")
        water_frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn_frame = ttk.Frame(water_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Подача воды", 
                  command=lambda: self.controller.set_water(True)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Откачка воды", 
                  command=lambda: self.controller.set_water(False)).pack(side=tk.LEFT, padx=5)
        
        # Статус системы
        status_frame = ttk.LabelFrame(parent, text="Статус системы")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text = tk.Text(status_frame, height=10)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка обновления статуса
        ttk.Button(parent, text="Обновить статус", 
                  command=self.update_status).pack(pady=5)
    
    def move_xyz(self, axis, step):
        current = self.xyz_vars[axis].get()
        new_value = current + step
        self.xyz_vars[axis].set(new_value)
        
        # Обновляем позицию робота
        self.controller.set_coord_pos(
            x=self.xyz_vars['X'].get(),
            y=self.xyz_vars['Y'].get(),
            z=self.xyz_vars['Z'].get()
        )
    
    def move_joint(self, joint, step):
        current = self.joints_vars[joint].get()
        new_value = current + step
        self.joints_vars[joint].set(new_value)
        
        # Обновляем углы робота
        joints = [self.joints_vars[f'J{i}'].get() for i in range(6)]
        self.controller.set_joint_pos(joints)
    
    def start_continuous_xyz(self, axis, step):
        self.continuous_move_data = {'type': 'xyz', 'axis': axis, 'step': step}
        self.continuous_move()
    
    def start_continuous_joint(self, joint, step):
        self.continuous_move_data = {'type': 'joint', 'joint': joint, 'step': step}
        self.continuous_move()
    
    def stop_continuous_move(self):
        if hasattr(self, 'continuous_move_data'):
            self.after_cancel(self.continuous_move_id)
            del self.continuous_move_data
    
    def continuous_move(self):
        if hasattr(self, 'continuous_move_data'):
            if self.continuous_move_data['type'] == 'xyz':
                self.move_xyz(
                    self.continuous_move_data['axis'], 
                    self.continuous_move_data['step']
                )
            else:
                self.move_joint(
                    self.continuous_move_data['joint'], 
                    self.continuous_move_data['step']
                )
            
            self.continuous_move_id = self.after(100, self.continuous_move)
    
    def update_status(self):
        # Здесь можно добавить код для получения статуса системы
        status = "Текущий статус системы:\n"
        status += f"- Позиция X: {self.xyz_vars['X'].get()} мм\n"
        status += f"- Позиция Y: {self.xyz_vars['Y'].get()} мм\n"
        status += f"- Позиция Z: {self.xyz_vars['Z'].get()} мм\n"
        status += "- Эрозия: выключена\n"
        status += "- Вода: отключена\n"
        
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, status)

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.X0 = X0
        self.Y0 = Y0
        self.Z0 = Z0
        
        self.title("Управление электроэрозионной установкой")
        self.geometry("800x600")
        
        # Инициализация контроллеров
        try:
            self.robot_controller = Robot()
            self.pico_controller = Pico()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к оборудованию: {str(e)}")
            # Режим эмуляции
            self.robot_controller = Robot(port=None)
            self.pico_controller = Pico(port=None)
        
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Создаем стиль для аварийной кнопки
        style = ttk.Style()
        style.configure("Emergency.TButton", foreground="white", background="red")
        
        # Создаем вкладки
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка процесса электроэрозии
        self.erosion_tab = ErosionProcessTab(self.notebook, self)
        self.notebook.add(self.erosion_tab, text="Процесс электроэрозии")
        
        # Вкладка сервисного управления
        self.service_tab = ServiceTab(self.notebook, self)
        self.notebook.add(self.service_tab, text="Сервисное управление")
    
    def set_coord_pos(self, x, y, z):
        # Установка позиции робота по координатам
        try:
            self.robot_controller.set_coord_pos(x, y, z)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось установить позицию: {str(e)}")
    
    def set_joint_pos(self, joints):
        # Установка позиции робота по суставам
        try:
            self.robot_controller.set_joint_pos(joints)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось установить углы: {str(e)}")
    
    def set_erosion(self, state):
        # Включение/выключение эрозии
        try:
            if state:
                self.pico_controller.erosion(1)
            else:
                self.pico_controller.erosion(0)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось управлять эрозией: {str(e)}")
    
    def set_water(self, state):
        # Включение/выключение воды
        try:
            if state:
                self.pico_controller.pump_in(1)
                self.pico_controller.pump_out(1)
            else:
                self.pico_controller.pump_in(0)
                self.pico_controller.pump_out(0)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось управлять водой: {str(e)}")
    
    def start_erosion_process(self, gcode_file, electrode_diameter, electrode_length, 
                             erosion_time, erosion_up_time, erosion_depth):
        # Запуск процесса электроэрозии
        try:
            # Здесь должен быть код запуска процесса
            messagebox.showinfo("Информация", "Процесс электроэрозии запущен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить процесс: {str(e)}")
    
    def stop_erosion_process(self):
        # Остановка процесса электроэрозии
        try:
            # Здесь должен быть код остановки процесса
            messagebox.showinfo("Информация", "Процесс электроэрозии остановлен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось остановить процесс: {str(e)}")
    
    def emergency_stop(self):
        # Аварийная остановка
        if messagebox.askyesno("Подтверждение", 
                              "Вы уверены, что хотите выполнить аварийную остановку?"):
            self.safe_finish()
    
    def safe_finish(self):
        # Безопасное завершение
        try:
            self.set_erosion(False)
            self.set_water(False)
            self.set_coord_pos(self.X0, self.Y0, self.Z0)
            messagebox.showinfo("Информация", "Система переведена в безопасный режим")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось безопасно завершить работу: {str(e)}")
    
    def on_closing(self):
        # Обработка закрытия окна
        if messagebox.askyesno("Подтверждение", 
                              "Вы уверены, что хотите закрыть приложение?"):
            self.safe_finish()
            self.destroy()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()