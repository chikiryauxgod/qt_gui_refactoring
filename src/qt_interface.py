import sys
import os
import cv2
import numpy as np
import json
import re
import time
import threading
import queue
import platform
from .electoerosion import Electroerosion

from .robot import Robot
from .pico import Pico
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QDoubleSpinBox, QSpinBox,
                              QProgressBar, QTextEdit, QGroupBox, QFileDialog, QMessageBox,
                              QScrollArea, QFrame, QSplitter, QSizePolicy, QGridLayout,
                              QLineEdit, QStackedWidget, QListWidget, QListWidgetItem,
                              QCheckBox, QComboBox, QSlider, QDialog, QDialogButtonBox)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, Slot, QPropertyAnimation, QEasingCurve, QEvent
from PySide6.QtGui import QImage, QPixmap, QFont, QPalette, QColor, QTextCursor 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
from .log import Log
from src.arrow3D import Arrow3D, Arrow3DData
from src.widgets.axis_control_widget import AxisControlWidget
from src.erosion_worker.errosion_worker import ErosionWorker, ErosionController, GCodeProcessor
from src.services.xyz_trajectory_service import XYZTrajectoryService
from src.services.joint_trajectory_service import JointTrajectoryService
from src.presenters.xyz_control_presenter import XYZControlPresenter
from src.application.xyz_trajectory_executor import XYZTrajectoryExecutor
from src.application.joint_trajectory_executor import JointTrajectoryExecutor
from src.erosion_worker.errosion_worker import ErosionWorker, ErosionController, GCodeProcessor
from src.LogText.LogTextBoxErrosion import QueueMessageSource, LogTextBoxErrosion
from src.VideoStream.VideoStreamThread import VideoStreamThread
from src.presenters.joint_control_presenter import JointControlPresenter
from src.domain.xyz_availability_service import XYZAvailabilityService
from src.domain.joint_availability_service import JointAvailabilityService
from src.visualization.xyz_kinematics_plotter import XYZKinematicsPlotter
from src.visualization.xyz_trajectory_plotter import XYZTrajectoryPlotter
from src.visualization.joints_trajectory_plotter import JointsTrajectoryPlotter





#+ Передать в electroerosion очередь, она заполняется в port и robot, её нужно просто туда передать
#+ Выводить содержимое очереди в textbox процесса эрозии
#- Сделать независимое управление помпами в UI

try:
    from ikpy.chain import Chain
    from ikpy.link import OriginLink, URDFLink
    IKPY_AVAILABLE = True
except ImportError:
    IKPY_AVAILABLE = False
    Log()("Библиотека ikpy не установлена. Установите: pip install ikpy")

# Константы из electroerosion.py
X0 = 430.0
Y0 = 0.0
Z0 = 277.0
XS = 0
YS = 0
ZS = 0
D_E = 2
logger = Log()
q = queue.Queue()
#filename = None

# Поток для видеозахвата
""" class VideoStreamThread(QThread):
    new_frame = Signal(QImage)
    
    def __init__(self, camera_idx=0, width=640, height=480, latency=30):
        super().__init__()
        self.running = True
        self.latency = latency
        self.cap = cv2.VideoCapture(camera_idx)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
    def run(self):
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    self.running = False
                    break
                if ret:
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
                    self.new_frame.emit(qt_image)
            self.msleep(self.latency)
            
    def stop(self):
        self.running = False
        self.wait()
        if self.cap.isOpened():
            self.cap.release()
 """

# Виджет управления осью
# class AxisControlWidget(QWidget):
#     position_changed = Signal(str, float)
    
#     def __init__(self, axis, initial_value=0.0):
#         super().__init__()
#         self.axis = axis
#         self.create_widgets(initial_value)
        
#     def create_widgets(self, initial_value):
#         layout = QVBoxLayout()
        
#         # Устанавливаем минимальные отступы
#         layout.setContentsMargins(5, 5, 5, 5)
#         layout.setSpacing(5)
        
#         title_label = QLabel(f"Ось {self.axis}")
#         title_label.setAlignment(Qt.AlignCenter)
#         title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
#         layout.addWidget(title_label)
        
#         self.value_label = QLabel(f"{initial_value:.1f} мм")
#         self.value_label.setAlignment(Qt.AlignCenter)
#         self.value_label.setStyleSheet("font-size: 12px; background-color: #f0f0f0; padding: 3px; border-radius: 3px;")
#         layout.addWidget(self.value_label)
        
#         # Добавляем небольшой отступ перед кнопками
#         layout.addSpacing(5)
        
#         button_layout = QGridLayout()
#         button_layout.setHorizontalSpacing(3)  # Уменьшаем горизонтальные промежутки
#         button_layout.setVerticalSpacing(3)    # Уменьшаем вертикальные промежутки
        
#         step_sizes = [0.1, 1.0, 10.0]
        
#         for i, step in enumerate(step_sizes):
#             minus_btn = QPushButton(f"-{step}")
#             minus_btn.setFixedSize(60, 50)  # Фиксированный размер вместо максимальной ширины
#             minus_btn.setStyleSheet("font-size: 10px;")
#             minus_btn.clicked.connect(lambda checked, s=step: self.change_position(-s))
#             button_layout.addWidget(minus_btn, 0, i)
            
#             step_label = QLabel(f"{step} мм")
#             step_label.setAlignment(Qt.AlignCenter)
#             step_label.setStyleSheet("font-size: 10px;")
#             button_layout.addWidget(step_label, 1, i)
            
#             plus_btn = QPushButton(f"+{step}")
#             plus_btn.setFixedSize(60, 50)
#             plus_btn.setStyleSheet("font-size: 10px;")
#             plus_btn.clicked.connect(lambda checked, s=step: self.change_position(s))
#             button_layout.addWidget(plus_btn, 2, i)
        
#         layout.addLayout(button_layout)
        
#         # Добавляем растягивающийся элемент для выравнивания
#         # layout.addStretch(1)
#         self.setLayout(layout)
        
#     def change_position(self, delta):
#         current_value = float(self.value_label.text().split()[0])
#         new_value = current_value + delta
#         self.value_label.setText(f"{new_value:.1f} мм")
#         self.position_changed.emit(self.axis, new_value)
'''
# Рабочий поток для эрозии
class ErosionWorker(QThread):
    progress_updated = Signal(float)
    time_updated = Signal(str)
    finished = Signal()
    paused = Signal()
    resumed = Signal()
    #filename = None
    d_e=2,
    X=0
    Y=0
    Z=0
    XS=0
    YS=0
    ZS=0
    def __init__(self, erode, gcode_points, total_time, electrode_diameter, electrode_length, 
                            erosion_time, erosion_up_time, erosion_depth, filename=None):
        super().__init__()
        self.erode = erode
        self.gcode_points = gcode_points
        self.total_time = total_time
        self.is_running = True
        self.is_paused = False
        self.current_point_index = 0
        self.start_time = None
        self.pause_start_time = None
        self.total_paused_time = 0
        self.filename = filename
        self.electrode_diameter = electrode_diameter 
        self.electrode_length = electrode_length 
        self.erosion_time = erosion_time
        self.erosion_up_time =  erosion_up_time
        self.erosion_depth = erosion_depth
        
    def run(self):
        logger(f"Send parametres: {self.electrode_diameter}, {self.electrode_length}, {self.erosion_time}, {self.erosion_up_time}, {self.erosion_depth}", queue=q)
        self.start_time = time.time()
        self.is_running = True
        self.is_finished = False
        param = [self.electrode_diameter, self.electrode_length, self.erosion_time, self.erosion_up_time, self.erosion_depth]
        # Создаем экземпляр Electroerosion
        # erode = electoerosion.Electroerosion(XS=XS, YS=YS, ZS=ZS, queue=q)
        # Используем переданный filename или fallback
        if self.filename and os.path.exists(self.filename):
            logger("Файел естЪ", queue=q)

            logger(f"Start Electroerosion with file: {self.filename}", queue=q)
        else:
            logger("Файл не найден", queue=q)
        

        
        try:
            # Раскоментировать для работы
            self.erode(self.filename, speed=10, mode='test')
            # Имитация прогресса работы по точкам G-code
            # for i, point in enumerate(self.gcode_points[self.current_point_index:], self.current_point_index):
            #     if not self.is_running:
            #         break
    
            #     # Проверяем паузу в начале каждой точки
            #     while self.is_paused and self.is_running:
            #         if self.pause_start_time is None:
            #             self.pause_start_time = time.time()
            #             # self.paused.emit()
            #         QThread.msleep(100)
            #         continue
                    
            #     # Если возобновили после паузы
            #     if self.pause_start_time is not None:
            #         pause_duration = time.time() - self.pause_start_time
            #         self.total_paused_time += pause_duration
            #         self.pause_start_time = None
            #         # self.resumed.emit()
                
            #     # Устанавливаем позицию (закомментировано, так как electroerosion сам управляет движением)
            #     # self.controller.set_coord_pos(point[0], point[1], point[2])
                
            #     self.current_point_index = i

            #     # Обновляем прогресс
            #     elapsed = time.time() - self.start_time - self.total_paused_time
            #     progress = min(100, (i + 1) / len(self.gcode_points) * 100)
            #     remaining = max(0, self.total_time - elapsed)
                
            #     self.progress_updated.emit(progress)
            #     self.time_updated.emit(f"{int(remaining//60):02d}:{int(remaining%60):02d}")
                
            #     # Время обработки в точке
            #     point_start_time = time.time()
            #     while (time.time() - point_start_time) < (self.total_time / len(self.gcode_points)) and self.is_running:
            #         # logger("Состояние worker", self.is_paused)
            #         # Проверяем паузу во время обработки точки
            #         if self.is_paused:
            #             if self.pause_start_time is None:
            #                 self.pause_start_time = time.time()
            #                 # self.paused.emit()
                        
            #             QThread.msleep(100)
            #             continue
                        
            #         QThread.msleep(50)
            
            self.is_finished = True
            # self.finished.emit()
            
        except Exception as e:
            logger(f"Error procces electroerosion: {e}", queue=q)
            self.finished.emit()
        
    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False
        
    def stop(self):
        self.is_running = False
        self.is_paused = False
'''
# Вкладка процесса эрозии
# class ErosionProcessTab(QWidget):
#     def __init__(self, controller):
#         super().__init__()
#         self.controller = controller
#         self.current_step = 0
#         self.gcode_points = []
#         self.erosion_worker = None
#         self.is_process_paused = False
#         self.queue_reader = None    #Ссылка на поток чтения очереди
#         self.create_widgets()

#     def start_queue_reader(self):
#         """Запуск потока чтения из очереди"""
#         source = QueueMessageSource(q)
#         self.queue_reader = LogTextBoxErrosion(source, latency_ms =100)
#         self.queue_reader.new_message.connect(self.append_to_status_text)
#         self.queue_reader.start()
        
#     def stop_queue_reader(self):
#         """Остановка потока чтения из очереди"""
#         if self.queue_reader and self.queue_reader.isRunning():
#             self.queue_reader.stop()
#             self.queue_reader.wait(1000)  # Ждем до 1 секунды для завершения 

#     @Slot(str)
#     def append_to_status_text(self, message):
#         """Добавление сообщения в текстовый виджет (вызывается из главного потока)"""
#         self.status_text.append(message)

#         # Автопрокрутка вниз
#         cursor = self.status_text.textCursor()
#         cursor.movePosition(QTextCursor.End)
#         self.status_text.setTextCursor(cursor)


#     def create_widgets(self):
#         main_layout = QVBoxLayout()
        
#         title_label = QLabel("Процесс электроэрозии")
#         title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
#         title_label.setAlignment(Qt.AlignCenter)
#         main_layout.addWidget(title_label)
        
#         self.step_indicator = QLabel("Шаг 0: Загрузка G-code файла")
#         self.step_indicator.setStyleSheet("font-weight: bold;")
#         self.step_indicator.setAlignment(Qt.AlignCenter)
#         main_layout.addWidget(self.step_indicator)
        
#         self.stacked_widget = QStackedWidget()
        
#         step0_widget = self.create_step0()
#         self.stacked_widget.addWidget(step0_widget)
        
#         step1_widget = self.create_step1()
#         self.stacked_widget.addWidget(step1_widget)
        
#         step2_widget = self.create_step2()
#         self.stacked_widget.addWidget(step2_widget)
        
#         step3_widget = self.create_step3()
#         self.stacked_widget.addWidget(step3_widget)
        
#         main_layout.addWidget(self.stacked_widget)
        
#         nav_layout = QHBoxLayout()
        
#         self.prev_btn = QPushButton("Назад")
#         self.prev_btn.clicked.connect(self.prev_step)
#         self.prev_btn.setEnabled(False)
#         nav_layout.addWidget(self.prev_btn)
        
#         self.next_btn = QPushButton("Далее")
#         self.next_btn.clicked.connect(self.next_step)
#         # self.next_btn.setStyleSheet("background-color: green; color: white;")
#         nav_layout.addWidget(self.next_btn)
        
        
        
#         nav_layout.addStretch()
#         main_layout.addLayout(nav_layout)
        
#         self.setLayout(main_layout)
#         self.show_step(0)
    
#     def create_step0(self):
#         widget = QWidget()
#         layout = QHBoxLayout()
        
#         left_widget = QGroupBox("Загрузка G-code файла")
#         left_layout = QVBoxLayout()
        
#         file_frame = QWidget()
#         file_layout = QHBoxLayout(file_frame)
        
#         self.gcode_file_edit = QLineEdit()
#         self.gcode_file_edit.setPlaceholderText("Выберите G-code файл...")
#         file_layout.addWidget(self.gcode_file_edit)
        
#         browse_btn = QPushButton("Обзор")
#         browse_btn.clicked.connect(self.select_gcode_file)
#         file_layout.addWidget(browse_btn)
        
#         left_layout.addWidget(file_frame)
        
#         info_group = QGroupBox("Информация о G-code")
#         info_layout = QVBoxLayout()
        
#         self.gcode_info_text = QTextEdit()
#         self.gcode_info_text.setReadOnly(True)
#         info_layout.addWidget(self.gcode_info_text)
        
#         info_group.setLayout(info_layout)
#         left_layout.addWidget(info_group)
        
#         left_widget.setLayout(left_layout)
#         layout.addWidget(left_widget)
        
#         right_widget = QGroupBox("Визуализация G-code")
#         right_layout = QVBoxLayout()
        
#         self.gcode_fig = Figure(figsize=(6, 5), dpi=100)
#         self.gcode_ax = self.gcode_fig.add_subplot(111, projection='3d')
        
#         self.gcode_ax.set_xlabel('X (мм)')
#         self.gcode_ax.set_ylabel('Y (мм)')
#         self.gcode_ax.set_zlabel('Z (мм)')
#         self.gcode_ax.set_title('Визуализация траектории G-code')
        
#         self.gcode_canvas = FigureCanvas(self.gcode_fig)
#         right_layout.addWidget(self.gcode_canvas)
        
#         right_widget.setLayout(right_layout)
#         layout.addWidget(right_widget)
        
#         widget.setLayout(layout)
#         return widget
    
#     def create_step1(self):
#         widget = QWidget()
#         layout = QHBoxLayout()
        
#         left_widget = QGroupBox("Видеопоток с камеры")
#         left_layout = QVBoxLayout()
        
#         self.video_label = QLabel()
#         self.video_label.setAlignment(Qt.AlignCenter)
#         self.video_label.setMinimumSize(640, 480)
#         self.video_label.setStyleSheet("border: 1px solid gray;")
#         self.video_label.setText("Загрузка видеопотока...")
#         left_layout.addWidget(self.video_label)
        
#         left_widget.setLayout(left_layout)
#         layout.addWidget(left_widget)
        
#         right_widget = QGroupBox("Управление положением робота")
#         right_layout = QVBoxLayout()
        
#         axes_widget = QWidget()
#         axes_layout = QHBoxLayout()
        
#         self.x_control = AxisControlWidget('X')
#         self.x_control.set_current_value(self.controller.current_x)

#         self.y_control = AxisControlWidget('Y')
#         self.y_control.set_current_value(self.controller.current_y)
        
#         self.z_control = AxisControlWidget('Z')
#         self.z_control.set_current_value(self.controller.current_z)
        
#                 # Кнопка возврата в нулевое положение
#         reset_btn = QPushButton("Вернуться в нулевое положение")
#         reset_btn.clicked.connect(self.return_to_zero_xyz)
#         reset_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #ff6b6b;
#                 color: white;
#                 font-weight: bold;
#                 border: none;
#                 border-radius: 4px;
#             }
#             QPushButton:hover {
#                 background-color: #ff5252;
#             }
#             QPushButton:pressed {
#                 background-color: #e53935;
#             }
#             QPushButton:disabled {
#                 background-color: #808080;
#             }
#         """)
#         # reset_btn.clicked.connect(self.reset_to_zero)
        

#         self.x_control.position_changed.connect(self.on_position_changed)
#         self.y_control.position_changed.connect(self.on_position_changed)
#         self.z_control.position_changed.connect(self.on_position_changed)
        
#         axes_layout.addWidget(self.x_control)
#         axes_layout.addWidget(self.y_control)
#         axes_layout.addWidget(self.z_control)
#         axes_widget.setLayout(axes_layout)

#         right_layout.addWidget(axes_widget)
#         right_layout.addStretch(1)
#         right_layout.addWidget(reset_btn)       

#         right_widget.setLayout(right_layout)
#         layout.addWidget(right_widget)
        
#         widget.setLayout(layout)
#         return widget
    
#     def create_step2(self):
#         widget = QWidget()
#         layout = QVBoxLayout()
        
#         params_group = QGroupBox("Параметры электроэрозионной обработки")
#         params_layout = QGridLayout()
        
#         parameters = [
#             ('Толщина электрода (мм)', 'electrode_diameter', 2.0, 0.1, 10.0),
#             ('Длина электрода (мм)', 'electrode_length', 100.0, 10.0, 500.0),
#             ('Время прожига (с)', 'erosion_time', 10.0, 1.0, 60.0),
#             ('Время поднятия электрода (с)', 'erosion_up_time', 5.0, 1.0, 30.0),
#             ('Глубина прожига (мм)', 'erosion_depth', 0.1, 0.01, 1.0),
#             ('Скорость перемещения (мм/с)', 'erosion_speed', 10.0, 1.0, 100.0)
#         ]
        
#         self.param_spinboxes = {}
#         self.mode = None
        
#         for i, (label, name, default, min_val, max_val) in enumerate(parameters):
#             params_layout.addWidget(QLabel(label), i, 0)
            
#             spinbox = QDoubleSpinBox()
#             spinbox.setRange(min_val, max_val)
#             spinbox.setValue(default)
#             spinbox.setSingleStep(0.1 if max_val > 10 else 0.01)
#             spinbox.setSuffix(" мм" if "мм" in label else " с")
#             self.param_spinboxes[name] = spinbox
            
#             params_layout.addWidget(spinbox, i, 1)

#         params_layout.addWidget(QLabel("Режим эррозии"), 6, 0)
#         self.coombbox = QComboBox()
#         self.coombbox.addItems(["emulated", "work", "test"])
#         # self.mode = self.coombbox.currentText()
#         params_layout.addWidget(self.coombbox, 6, 1)
        
#         params_group.setLayout(params_layout)
#         layout.addWidget(params_group)
        
#         scheme_label = QLabel("Схема параметров электроэрозии")
#         scheme_label.setAlignment(Qt.AlignCenter)
#         layout.addWidget(scheme_label)
        
#         scheme_placeholder = QLabel("Место для схемы параметров")
#         scheme_placeholder.setAlignment(Qt.AlignCenter)
#         scheme_placeholder.setStyleSheet("border: 1px dashed gray; min-height: 200px;")
#         layout.addWidget(scheme_placeholder)
        
#         layout.addStretch()
#         widget.setLayout(layout)
#         return widget
    
#     def create_step3(self):
#         widget = QWidget()
#         layout = QVBoxLayout()
#         layout.setContentsMargins(10, 10, 10, 10)
    
#         # Статус процесса
#         status_group = QGroupBox("Статус процесса")
#         status_layout = QVBoxLayout()
        
#         self.process_status_label = QLabel("Готов к запуску")
#         self.process_status_label.setStyleSheet("""
#             font-weight: bold; 
#             font-size: 12pt; 
#             padding: 10px;
#             border-radius: 5px;
#             background-color: #ecf0f1;
#         """)
#         self.process_status_label.setAlignment(Qt.AlignCenter)
#         self.process_status_label.setMinimumHeight(40)
#         status_layout.addWidget(self.process_status_label)
        
#         status_group.setLayout(status_layout)
#         layout.addWidget(status_group)
        
#         progress_group = QGroupBox("Прогресс выполнения")
#         progress_layout = QVBoxLayout()
        
#         progress_bar_layout = QHBoxLayout()
#         progress_bar_layout.addWidget(QLabel("Прогресс:"))
        
#         self.progress_bar = QProgressBar()
#         self.progress_bar.setRange(0, 100)
#         progress_bar_layout.addWidget(self.progress_bar, 1)
        
#         self.time_label = QLabel("Осталось: --:--")
#         progress_bar_layout.addWidget(self.time_label)
        
#         progress_layout.addLayout(progress_bar_layout)
#         progress_group.setLayout(progress_layout)
#         layout.addWidget(progress_group)
        
#         status_group = QGroupBox("Текущие параметры")
#         status_layout = QVBoxLayout()
        
#         self.status_text = QTextEdit()
#         self.status_text.setReadOnly(True)


#         status_layout.addWidget(self.status_text)
        
#         status_group.setLayout(status_layout)
#         layout.addWidget(status_group)
        
#         control_layout = QHBoxLayout()
        
#         self.start_btn = QPushButton("Запуск")
#         self.start_btn.clicked.connect(self.start_erosion)
#         control_layout.addWidget(self.start_btn)
        
#         self.pause_btn = QPushButton("⏸ Пауза")
#         self.pause_btn.setEnabled(False)
#         self.pause_btn.setMinimumHeight(40)
#         self.pause_btn.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
#         self.pause_btn.clicked.connect(self.toggle_pause)
#         control_layout.addWidget(self.pause_btn)
        
#         self.stop_btn = QPushButton("Стоп")
#         self.stop_btn.clicked.connect(self.stop_erosion)
#         control_layout.addWidget(self.stop_btn)

#         self.changetool = QPushButton("Заменить инструмент")
#         self.changetool.clicked.connect(self.ChangeTools)
#         control_layout.addWidget(self.changetool)
        
#         control_layout.addStretch()
#         layout.addLayout(control_layout)
        
#         widget.setLayout(layout)
#         return widget

#     @Slot()
#     def select_gcode_file(self):
#         filename, _ = QFileDialog.getOpenFileName(
#             self,
#             "Выберите G-code файл",
#             "",
#             "G-code files (*.gcode *.nc);;All files (*.*)"
#         )
#         if filename:
#             self.gcode_file_edit.setText(filename)

#         if not filename.lower().endswith(('.gcode', '.nc')):
#             QMessageBox.critical(
#                 self, 
#                 "Ошибка", 
#                 "Выбранный файл не является файлом G-code.\n"
#                 "Поддерживаемые расширения: .gcode, .nc"
#             )
#             return

#         if not filename:
#             QMessageBox.critical(self, "Ошибка", "Выберите файл G-code")
#             return
        
#         try:
#             self.gcode_points = self.parse_gcode_file(filename)
#             self.visualize_gcode()
            
#             info_text = f"Файл: {os.path.basename(filename)}\n"
#             info_text += f"Количество точек: {len(self.gcode_points)}\n"
            
#             if self.gcode_points:
#                 x_values = [p[0] for p in self.gcode_points]
#                 y_values = [p[1] for p in self.gcode_points]
#                 z_values = [p[2] for p in self.gcode_points]
                
#                 info_text += f"Диапазон X: {min(x_values):.2f} - {max(x_values):.2f} мм\n"
#                 info_text += f"Диапазон Y: {min(y_values):.2f} - {max(y_values):.2f} мм\n"
#                 info_text += f"Диапазон Z: {min(z_values):.2f} - {max(z_values):.2f} мм\n"
#                 info_text += f"Общая длина траектории: {self.calculate_path_length(self.gcode_points):.2f} мм\n"
            
#             self.gcode_info_text.setPlainText(info_text)
            
            
#         except Exception as e:
#             logger(f"Failed to upload file: {str(e)}", queue=q)            

#     def parse_gcode_file(self, filename):
#         points = []
#         current_x, current_y, current_z = 0, 0, 0
        
#         with open(filename, 'r') as file:
#             for line in file:
#                 line = line.strip()
#                 if line.startswith(';') or not line:
#                     continue
                
#                 if ';' in line:
#                     line = line.split(';')[0].strip()
                
#                 if line.startswith('G1') or line.startswith('G0') or line.startswith('G01') or line.startswith('G00'):
#                     x = self.extract_coordinate(line, 'X', current_x)
#                     y = self.extract_coordinate(line, 'Y', current_y)
#                     z = self.extract_coordinate(line, 'Z', current_z)
                    
#                     if (x, y, z) != (current_x, current_y, current_z):
#                         points.append((x, y, z))
#                         current_x, current_y, current_z = x, y, z
        
#         return points if points else [(0, 0, 0)]

#     def extract_coordinate(self, line, axis, default):
#         pattern = f'{axis}([+-]?\\d*\\.?\\d+)'
#         match = re.search(pattern, line)
#         return float(match.group(1)) if match else default

#     def calculate_path_length(self, points):
#         if len(points) < 2:
#             return 0
        
#         total_length = 0
#         for i in range(1, len(points)):
#             x1, y1, z1 = points[i-1]
#             x2, y2, z2 = points[i]
#             distance = np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
#             total_length += distance
        
#         return total_length

#     def visualize_gcode(self):
#         self.gcode_ax.clear()
        
#         if self.gcode_points:
#             points = np.array(self.gcode_points)
            
#             self.gcode_ax.plot(points[:, 0], points[:, 1], points[:, 2], 'b-', linewidth=2, alpha=0.7)
#             self.gcode_ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=range(len(points)), 
#                                 cmap='viridis', s=20, alpha=0.6)
            
#             if len(points) > 1:
#                 self.gcode_ax.plot([points[0, 0]], [points[0, 1]], [points[0, 2]], 
#                                  'go', markersize=8, label='Начало')
#                 self.gcode_ax.plot([points[-1, 0]], [points[-1, 1]], [points[-1, 2]], 
#                                  'rs', markersize=8, label='Конец')
#                 self.gcode_ax.legend()
            
#             if len(points) > 1:
#                 for i in range(0, len(points)-1, max(1, len(points)//10)):
#                     x1, y1, z1 = points[i]
#                     x2, y2, z2 = points[i+1]
                    
#                     dx, dy, dz = x2-x1, y2-y1, z2-z1
#                     length = np.sqrt(dx**2 + dy**2 + dz**2)
#                     if length > 0:
#                         dx, dy, dz = dx/length*10, dy/length*10, dz/length*10
                        
#                         arrow = Arrow3DData([x1, x1+dx], [y1, y1+dy], [z1, z1+dz], 
#                                        mutation_scale=15, lw=1, arrowstyle="-|>", color="red", alpha=0.7)
#                         self.gcode_ax.add_artist(arrow)
        
#         self.gcode_ax.set_xlabel('X (мм)')
#         self.gcode_ax.set_ylabel('Y (мм)')
#         self.gcode_ax.set_zlabel('Z (мм)')
#         self.gcode_ax.set_title('Визуализация траектории G-code')
        
#         if self.gcode_points and len(self.gcode_points) > 1:
#             points = np.array(self.gcode_points)
#             max_range = max(points[:, 0].max()-points[:, 0].min(), 
#                            points[:, 1].max()-points[:, 1].min(), 
#                            points[:, 2].max()-points[:, 2].min()) * 0.6
            
#             mid_x = (points[:, 0].max()+points[:, 0].min()) * 0.5
#             mid_y = (points[:, 1].max()+points[:, 1].min()) * 0.5
#             mid_z = (points[:, 2].max()+points[:, 2].min()) * 0.5
            
#             self.gcode_ax.set_xlim(mid_x - max_range, mid_x + max_range)
#             self.gcode_ax.set_ylim(mid_y - max_range, mid_y + max_range)
#             self.gcode_ax.set_zlim(max(0, mid_z - max_range), mid_z + max_range)
#         else:
#             self.gcode_ax.set_xlim([-100, 100])
#             self.gcode_ax.set_ylim([-100, 100])
#             self.gcode_ax.set_zlim([0, 200])
        
#         self.gcode_canvas.draw()

#     @Slot()
#     def show_step(self, step_index):
#         self.stacked_widget.setCurrentIndex(step_index)
#         self.current_step = step_index
        
#         step_names = [
#             "Шаг 0: Загрузка G-code файла",
#             "Шаг 1: Настройка начального положения", 
#             "Шаг 2: Настройка процесса эрозии",
#             "Шаг 3: Запуск процесса эрозии"
#         ]
#         self.step_indicator.setText(step_names[step_index])
        
#         self.prev_btn.setEnabled(step_index > 0)
        
#         if step_index < self.stacked_widget.count() - 1:
#             self.next_btn.setEnabled(True)
#         else:
#             self.next_btn.setEnabled(False)


#     @Slot()
#     def next_step(self):
#         if self.current_step < self.stacked_widget.count() - 1:
#             self.show_step(self.current_step + 1)
#             if self.current_step == 2:
#                 XS = self.controller.current_x
#                 YS = self.controller.current_y
#                 ZS = self.controller.current_z
#                 logger(f'Param XS YS ZS set: {XS, YS, ZS}', queue=q)

#             elif self.current_step == 3:
#                 self.mode = self.coombbox.currentText()   
#                 logger(self.mode)
            

#     @Slot()
#     def prev_step(self):
#         if self.current_step > 0:
#             self.show_step(self.current_step - 1)

#     @Slot()
#     def stop_process(self):
#         self.controller.safe_finish()
#         self.show_step(0)

        
#     @Slot(str, float)
#     def on_position_changed(self, axis, value):
#         positions = {
#             'X': self.x_control,
#             'Y': self.y_control, 
#             'Z': self.z_control
#         }
        
#         x = float(positions['X'].value_label.text().split()[0])
#         y = float(positions['Y'].value_label.text().split()[0])
#         z = float(positions['Z'].value_label.text().split()[0])
        
#         self.controller.set_coord_pos(x, y, z)

#     def start_erosion(self):
#         if hasattr(self, 'gcode_points') and self.gcode_points:
                
#                 # Запускаем чтение из очереди ДО начала процесса эрозии
#                 self.start_queue_reader()                
#                 # Получаем filename из поля ввода
#                 filename = self.gcode_file_edit.text().strip()
                
#                 if not filename or not os.path.exists(filename):
#                     QMessageBox.critical(self, "Ошибка", "G-code файл не выбран или не существует")
#                     return
                
#                 # Запускаем процесс с передачей filename
#                 self.controller.start_erosion_process(
#                     self.gcode_points,
#                     self.param_spinboxes['electrode_diameter'].value(),
#                     self.param_spinboxes['electrode_length'].value(),
#                     self.param_spinboxes['erosion_time'].value(),
#                     self.param_spinboxes['erosion_up_time'].value(),
#                     self.param_spinboxes['erosion_depth'].value(),
#                     filename,  # Передаем filename
#                     # self.coombbox.currentText()
#                     self.mode
#                 )
#                 self.start_btn.setEnabled(False)
#                 self.pause_btn.setEnabled(True)
#                 self.pause_btn.setText("⏸ Пауза")
#                 self.is_process_paused = False
#         else:
#             QMessageBox.critical(self, "Ошибка", "Сначала загрузите G-code файл")
    
#     def set_erosion_worker(self, worker):
#         """Установка рабочего потока для управления паузой"""
#         self.erosion_worker = worker
    
#     @Slot()
#     def toggle_pause(self):
#         """Переключение состояния паузы"""
#         # logger(f"Debug: toggle_pause called, worker: {self.erosion_worker}, is_running: {self.erosion_worker.is_running if self.erosion_worker else 'No worker'}", queue=q)
        
#         if self.erosion_worker is not None and self.erosion_worker.isRunning():
#             if not self.is_process_paused:
#                 # Ставим на паузу
#                 logger("Pausing process", queue=q)
#                 self.erosion_worker.pause()
#                 self.pause_btn.setText("▶ Продолжить")
#                 self.pause_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
#                 # logger(f"Процесс приостановлен", queue=q)
#                 self.is_process_paused = True
#                 self.update_process_status("ПРОЦЕСС НА ПАУЗЕ", "#f39c12")
#             else:
#                 # Возобновляем процесс
#                 logger("Resuming process", queue=q)
#                 self.erosion_worker.resume()
#                 self.pause_btn.setText("⏸ Пауза")
#                 self.pause_btn.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
#                 # logger(f" Процесс возобновлен", queue=q)
#                 self.is_process_paused = False
#                 self.update_process_status("ПРОЦЕСС ВЫПОЛНЯЕТСЯ", "#27ae60")
#         else:
#             logger("Worker not running or doesn't exist", queue=q)
#     @Slot()
#     def stop_erosion(self):

#         # Останавливаем чтение из очереди
#         self.stop_queue_reader()
#         """Полная остановка процесса"""
#         if self.erosion_worker and self.erosion_worker.isRunning():
#             self.erosion_worker.stop()
#             self.erosion_worker.wait(1000)  # Ждем до 1 секунды для завершения
        
#         if hasattr(self.controller, 'stop_erosion_process'):
#             self.controller.stop_erosion_process()
        
#         self.start_btn.setEnabled(True)
#         self.pause_btn.setEnabled(False)
#         self.pause_btn.setText("⏸ Пауза")
#         self.pause_btn.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
#         self.is_process_paused = False
        
#         # Сбрасываем прогресс
#         self.progress_bar.setValue(0)
#         self.time_label.setText("Остановлено")
        
#         logger(f"[{time.strftime('%H:%M:%S')}] Процесс остановлен", queue=q)
#         self.update_process_status("ПРОЦЕСС ОСТАНОВЛЕН", "#e74c3c")

#     def update_process_status(self, status, color="#ecf0f1"):
#         """Обновление статуса процесса"""
#         self.process_status_label.setText(status)
#         self.process_status_label.setStyleSheet(f"""
#             font-weight: bold; 
#             font-size: 12pt; 
#             padding: 10px;
#             border-radius: 5px;
#             background-color: {color};
#         """)

#     @Slot()
#     def ChangeTools(self):
#         logger("Pausing process", queue=q)
#         self.erosion_worker.pause()
#         self.pause_btn.setText("▶ Продолжить")
#         self.pause_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
#         self.is_process_paused = True
#         self.update_process_status("ПРОЦЕСС НА ПАУЗЕ", "#f39c12")
#         QMessageBox.information(self, "Смена инструмента", "Замените инструмент, затем нажмите кнопку продолжить")
#         logger("Нажата кнопка замены инструмента")



#     @Slot()
#     def return_to_zero_xyz(self):
#         self.controller.set_coord_pos(self.controller.X0, self.controller.Y0, self.controller.Z0)

# Сервисная вкладка
class ServiceTab(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.xyz_presenter = XYZControlPresenter(controller)
        self.trajectory_service = XYZTrajectoryService()
        self.trajectory_points_joints = JointTrajectoryService()
        
        self.xyz_trajectory_executor = XYZTrajectoryExecutor(
            controller=self.controller,
            trajectory_service=self.trajectory_service,)
        self.joint_presenter = JointControlPresenter(self.controller)
        self.joint_trajectory_executor = JointTrajectoryExecutor(
            joint_presenter=self.joint_presenter,
            trajectory_service=self.trajectory_points_joints,)
        self.xyz_availability_service = XYZAvailabilityService()
        self.joint_availability_service = JointAvailabilityService()    
        
        self.continuous_move_timer = QTimer()
        self.continuous_move_timer.timeout.connect(self.continuous_move)
        self.continuous_move_data = None
        self.robot_chain = self.create_robot_chain()

        
        self.create_widgets()
    
    def create_robot_chain(self):
            """Создание кинематической модели робота из URDF файла"""
            if not IKPY_AVAILABLE:
                logger("The ikpy library is unavailable. The kinematics will not be displayed.", queue=q)
                return None
            
            try:
                # Загрузка модели из URDF файла
                urdf_path = "robot_6_axis.urdf"  # Убедитесь что файл в правильной директории
                if os.path.exists(urdf_path):
                    # Маска активных звеньев (обычно [False, True, True, True, True, True, True, False] для 6-осевого робота)
                    # Первое и последнее обычно OriginLink и ToolLink
                    active_links_mask = [False, True, True, True, True, True, True, False]
                    robot_chain = Chain.from_urdf_file(urdf_path, active_links_mask=active_links_mask)
                    logger("The kinematic model of the robot has been successfully uploaded from URDF", queue=q)
                    return robot_chain
                else:
                    logger(f"URDF file not found: {urdf_path}", file=open('log.txt', "a"))
                    
            except Exception as e:
                logger(f"Error load URDF: {e}", queue=q)

    def create_widgets(self):
        layout = QVBoxLayout()
        
        tab_widget = QTabWidget()
        
        # Вкладки
        xyz_tab = self.create_xyz_tab()
        tab_widget.addTab(xyz_tab, "Управление по осям XYZ")
        
        joints_tab = self.create_joints_tab()
        tab_widget.addTab(joints_tab, "Управление по суставам")
        
        control_tab = self.create_erosion_controls_tab()
        tab_widget.addTab(control_tab, "Управление эрозией и водой")
        
        xyz_traj_tab = self.create_xyz_trajectory_tab()
        tab_widget.addTab(xyz_traj_tab, "Траектория по XYZ")
        
        joints_traj_tab = self.create_joints_trajectory_tab()
        tab_widget.addTab(joints_traj_tab, "Траектория по суставам")

        robot_param_tab = self.robot_settings_tab()
        tab_widget.addTab(robot_param_tab, "Параметры робота")

        layout.addWidget(tab_widget)

        # Аварийная кнопка
        emergency_btn = QPushButton("АВАРИЙНАЯ ОСТАНОВКА")
        emergency_btn.clicked.connect(self.controller.emergency_stop)
        emergency_btn.setStyleSheet("""
            QPushButton {
                background-color: red; 
                color: white; 
                font-weight: bold; 
                font-size: 14pt;
                padding: 10px;
            }
        """)
        #layout.addWidget(emergency_btn)       
        self.setLayout(layout)
    
    def create_xyz_tab(self):
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Левая панель - управление
        control_frame = QGroupBox("Управление осями XYZ")
        control_layout = QVBoxLayout()
        
        axes = ['X', 'Y', 'Z']
        self.xyz_controls = {}
        
        for axis in axes:
            group = QGroupBox(f"Ось {axis}")
            group_layout = QVBoxLayout()
            
            # Текущее положение
            value_layout = QHBoxLayout()
            value_layout.addWidget(QLabel("Текущее положение (мм):"))
            
            current_value = getattr(self.controller, f'current_{axis.lower()}', 0)
            value_display = QLabel(f"{current_value:.2f}")
            value_display.setStyleSheet("font-weight: bold; font-size: 12pt;")
            value_layout.addWidget(value_display)
            value_layout.addStretch()
            
            group_layout.addLayout(value_layout)
            
            # Ручной ввод
            input_layout = QHBoxLayout()
            input_layout.addWidget(QLabel("Задать положение:"))
            
            manual_input = QDoubleSpinBox()
            manual_input.setRange(-1000, 1000)
            manual_input.setValue(current_value)
            manual_input.setSuffix(" мм")
            input_layout.addWidget(manual_input)
            
            set_btn = QPushButton("Установить XYZ")
            manual_input.editingFinished.connect(lambda a=axis, i=manual_input: self.set_xyz_position(a, i.value()))
            set_btn.clicked.connect(lambda checked, a=axis, i=manual_input: self.set_xyz_position(a, i.value()))
            input_layout.addWidget(set_btn)
            
            group_layout.addLayout(input_layout)
            
            # Кнопки с шагами
            steps_layout = QVBoxLayout()
            
            step_sizes = [0.1, 1.0, 10.0]
            for step in step_sizes:
                step_layout = QHBoxLayout()
                step_layout.addWidget(QLabel(f"Шаг {step} мм:"))
                
                minus_btn = QPushButton(f"-{step}")
                minus_btn.clicked.connect(lambda checked, a=axis, s=step: self.move_xyz(a, -s))
                step_layout.addWidget(minus_btn)
                
                plus_btn = QPushButton(f"+{step}")
                plus_btn.clicked.connect(lambda checked, a=axis, s=step: self.move_xyz(a, s))
                step_layout.addWidget(plus_btn)
                
                step_layout.addStretch()
                steps_layout.addLayout(step_layout)
            
            group_layout.addLayout(steps_layout)
            group.setLayout(group_layout)
            control_layout.addWidget(group)
            
            self.xyz_controls[axis] = {
                'display': value_display,
                'input': manual_input
            }
        
        # ★ Добавляем кнопку "Вернуться в нулевое положение"
        reset_btn = QPushButton("Вернуться в нулевое положение")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
            QPushButton:pressed {
                background-color: #e53935;
            }
        """)
        reset_btn.clicked.connect(self.return_to_zero_xyz)
        control_layout.addWidget(reset_btn)
        
        control_frame.setLayout(control_layout)
        layout.addWidget(control_frame)
        
        # Правая панель - визуализация
        vis_frame = QGroupBox("Визуализация положения робота")
        vis_layout = QVBoxLayout()
        
        self.xyz_fig = Figure(figsize=(6, 5), dpi=100)
        self.xyz_ax = self.xyz_fig.add_subplot(111, projection='3d')
        
        self.xyz_ax.set_xlabel('X (мм)')
        self.xyz_ax.set_ylabel('Y (мм)')
        self.xyz_ax.set_zlabel('Z (мм)')
        self.xyz_ax.set_title('Текущее положение робота')
        
        self.xyz_canvas = FigureCanvas(self.xyz_fig)
        vis_layout.addWidget(self.xyz_canvas)
        
        self.xyz_kinematics_plotter = XYZKinematicsPlotter(
            ax=self.xyz_ax,
            canvas=self.xyz_canvas,
            robot_chain=self.robot_chain,
            ikpy_available=IKPY_AVAILABLE,)
        
        update_btn = QPushButton("Обновить визуализацию")
        update_btn.clicked.connect(self.update_xyz_plot)
        vis_layout.addWidget(update_btn)
        
        vis_frame.setLayout(vis_layout)
        layout.addWidget(vis_frame)
        
        widget.setLayout(layout)
        self.update_xyz_plot()
        
        return widget

    def create_joints_tab(self):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Используем splitter для разделения управления и визуализации
        splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель - управление суставами (компактная)
        control_frame = QGroupBox("Управление суставами")
        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setSpacing(5)
        
        # Создаем сетку для компактного расположения суставов 2×3
        joints_grid = QGridLayout()
        joints_grid.setHorizontalSpacing(5)
        joints_grid.setVerticalSpacing(5)
        joints_grid.setContentsMargins(2, 2, 2, 2)
        
        joints = ['J0', 'J1', 'J2', 'J3', 'J4', 'J5']
        self.joints_controls = {}
        
        for i, joint in enumerate(joints):
            # Создаем компактную группу для каждого сустава
            group = QGroupBox(f"Сустав {joint}")
            group.setMaximumWidth(280)  # Ограничиваем ширину
            group.setMaximumHeight(350)
            group_layout = QVBoxLayout()
            group_layout.setContentsMargins(5, 8, 5, 5)
            group_layout.setSpacing(3)
            
            # Верхняя строка: текущее значение и ручной ввод
            top_layout = QHBoxLayout()
            
            # Текущий угол
            current_value = self.controller.current_joints[i] if i < len(self.controller.current_joints) else 0
            value_layout = QVBoxLayout()
            value_display = QLabel(f"{current_value:.1f}°")
            value_display.setStyleSheet("font-weight: bold; font-size: 11px; background-color: #f0f0f0; padding: 2px; border: 1px solid #ccc;")
            value_display.setAlignment(Qt.AlignCenter)
            value_display.setFixedHeight(20)
            value_layout.addWidget(value_display)
            top_layout.addLayout(value_layout)
            
            # Ручной ввод
            input_layout = QVBoxLayout()
            manual_input = QDoubleSpinBox()
            manual_input.setRange(-180, 180)
            manual_input.setValue(current_value)
            manual_input.setSuffix("°")
            manual_input.setFixedHeight(22)
            manual_input.setStyleSheet("font-size: 10px;")
            manual_input.setButtonSymbols(QDoubleSpinBox.NoButtons)  # Убираем кнопки для экономии места
            input_layout.addWidget(manual_input)
            top_layout.addLayout(input_layout)
            group_layout.addLayout(top_layout)
            second_layout = QHBoxLayout()

            # Кнопка установки
            set_btn = QPushButton("Установить")
            set_btn.setFixedSize(150, 42)
            set_btn.setStyleSheet("font-size: 10px;")
            manual_input.editingFinished.connect(lambda j=joint, inp=manual_input: self.set_joint_position(j, inp.value()))
            set_btn.clicked.connect(lambda checked, j=joint, inp=manual_input: self.set_joint_position(j, inp.value()))
            second_layout.addWidget(set_btn)
            
            group_layout.addLayout(second_layout)
            
            # Вертикальное расположение шагов с кнопками в столбик
            steps_layout = QVBoxLayout()
            steps_layout.setSpacing(2)
            
            # steps_label = QLabel("Шаг:")
            # steps_label.setStyleSheet("font-size: 9px;")
            # steps_layout.addWidget(steps_label)
            
            step_sizes = [0.1, 1.0, 5.0]
            
            for step in step_sizes:
                # Горизонтальная строка для каждого шага
                step_row_layout = QHBoxLayout()
                step_row_layout.setSpacing(2)
                
                # Метка с размером шага
                step_label = QLabel(f"{step}°")
                step_label.setAlignment(Qt.AlignLeft)
                step_label.setStyleSheet("font-size: 15px; color: #666;")
                step_label.setFixedWidth(25)
                step_row_layout.addWidget(step_label)
                
                # Кнопка минус
                minus_btn = QPushButton("−")
                minus_btn.setFixedSize(60, 40)
                minus_btn.setStyleSheet("""
                    QPushButton {
                        font-size: 12px;
                        font-weight: bold;
                        background-color: #ff6b6b;
                        color: white;
                        border: 1px solid #ccc;
                        border-radius: 2px;
                    }
                    QPushButton:hover {
                        background-color: #ff5252;
                    }
                """)
                minus_btn.setToolTip(f"Уменьшить на {step}°")
                minus_btn.clicked.connect(lambda checked, j=joint, s=step: self.move_joint(j, -s))
                step_row_layout.addWidget(minus_btn)
                
                # Кнопка плюс
                plus_btn = QPushButton("+")
                plus_btn.setFixedSize(60, 40)
                plus_btn.setStyleSheet("""
                    QPushButton {
                        font-size: 12px;
                        font-weight: bold;
                        background-color: #51cf66;
                        color: white;
                        border: 1px solid #ccc;
                        border-radius: 2px;
                    }
                    QPushButton:hover {
                        background-color: #40c057;
                    }
                """)
                plus_btn.setToolTip(f"Увеличить на {step}°")
                plus_btn.clicked.connect(lambda checked, j=joint, s=step: self.move_joint(j, s))
                step_row_layout.addWidget(plus_btn)
                
                step_row_layout.addStretch()
                steps_layout.addLayout(step_row_layout)
            
            group_layout.addLayout(steps_layout)
            
            group.setLayout(group_layout)
            
            # Располагаем в сетке 2×3
            row = i // 3
            col = i % 3
            joints_grid.addWidget(group, row, col)
            
            self.joints_controls[joint] = {
                'display': value_display,
                'input': manual_input
            }
        
        # Добавляем кнопки общего управления
        common_controls_layout = QHBoxLayout()
        
        home_btn = QPushButton("Вернуться в нулевое положение")
        # home_btn.setFixedSize(440, 50)
        home_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff6b6b;
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #ff5252;
                }
                QPushButton:pressed {
                    background-color: #e53935;
                }
            """)
        home_btn.clicked.connect(self.return_to_zero_joints)
        # common_controls_layout.addWidget(home_btn)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(home_btn)

        common_controls_layout.addStretch()
        
        control_layout.addLayout(joints_grid)
        control_layout.addLayout(common_controls_layout)
        control_layout.addLayout(button_layout)
        control_frame.setLayout(control_layout)
        splitter.addWidget(control_frame)
        
        # Правая панель - визуализация
        vis_frame = QGroupBox("Визуализация положения робота")
        vis_layout = QVBoxLayout()
        vis_layout.setContentsMargins(5, 5, 5, 5)
        vis_layout.setSpacing(5)
        
        self.joints_fig = Figure(figsize=(5, 4), dpi=80)  # Уменьшаем размер фигуры
        self.joints_ax = self.joints_fig.add_subplot(111, projection='3d')
        
        self.joints_ax.set_xlabel('X (мм)')
        self.joints_ax.set_ylabel('Y (мм)')
        self.joints_ax.set_zlabel('Z (мм)')
        self.joints_ax.set_title('Текущее положение робота')
        
        self.joints_canvas = FigureCanvas(self.joints_fig)
        self.joints_canvas.setMinimumSize(400, 350)  # Фиксируем минимальный размер
        vis_layout.addWidget(self.joints_canvas)
        
        self.joints_trajectory_plotter = JointsTrajectoryPlotter(
            self.joints_ax, self.joints_canvas)
        
        update_btn = QPushButton("Обновить визуализацию")
        update_btn.clicked.connect(self.update_joints_plot)
        vis_layout.addWidget(update_btn)
        
        vis_frame.setLayout(vis_layout)
        splitter.addWidget(vis_frame)
        
        # Устанавливаем пропорции splitter
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
        widget.setLayout(layout)
        self.update_joints_plot()
        
        return widget
    
    def create_erosion_controls_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        erosion_group = QGroupBox("Управление эрозией")
        erosion_layout = QHBoxLayout()
        
        erosion_on_btn = QPushButton("Включить эрозию")
        erosion_on_btn.clicked.connect(lambda: self.controller.set_erosion(True))
        erosion_layout.addWidget(erosion_on_btn)
        
        erosion_off_btn = QPushButton("Выключить эрозию")
        erosion_off_btn.clicked.connect(lambda: self.controller.set_erosion(False))
        erosion_layout.addWidget(erosion_off_btn)
        
        erosion_group.setLayout(erosion_layout)
        layout.addWidget(erosion_group)
        
        water_group = QGroupBox("Управление водой")
        # Создаем основную вертикальную компоновку для группы управления водой
        water_main_layout = QVBoxLayout()

        # Первая горизонтальная компоновка для кнопок циркуляции воды
        water_layout = QHBoxLayout()
        water_in_btn = QPushButton("Включение циркуляции воды")
        water_in_btn.clicked.connect(lambda: self.controller.set_water(True))
        water_layout.addWidget(water_in_btn)

        water_out_btn = QPushButton("Отключение циркуляции воды")
        water_out_btn.clicked.connect(lambda: self.controller.set_water(False))
        water_layout.addWidget(water_out_btn)

        # Вторая горизонтальная компоновка для кнопок управления помпами
        water_pump_layout = QHBoxLayout()
        water_pump_one = QPushButton("Включить/выключить накачивание воды")
        water_pump_one.clicked.connect(lambda: self.controller.pump_control_one())  # Убедитесь, что здесь правильный метод контроллера
        water_pump_layout.addWidget(water_pump_one)

        water_pump_two = QPushButton("Включить/выключить откачивание воды")
        water_pump_two.clicked.connect(lambda: self.controller.pump_control_two())  # Убедитесь, что здесь правильный метод контроллера
        water_pump_layout.addWidget(water_pump_two)

        # Добавляем обе горизонтальные компоновки в вертикальную
        water_main_layout.addLayout(water_layout)
        water_main_layout.addLayout(water_pump_layout)

        water_group.setLayout(water_main_layout)
        layout.addWidget(water_group)
        
        status_group = QGroupBox("Статус системы")
        status_layout = QVBoxLayout()
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        status_layout.addWidget(self.status_text)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        update_btn = QPushButton("Обновить статус")
        update_btn.clicked.connect(self.update_status)
        layout.addWidget(update_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        self.update_status()
        
        return widget
    
    def create_xyz_trajectory_tab(self):
        widget = QWidget()
        layout = QHBoxLayout()
        
        control_frame = QGroupBox("Управление траекторией XYZ")
        control_layout = QVBoxLayout()
        
        point_group = QGroupBox("Добавить точку")
        point_layout = QGridLayout()
        
        point_layout.addWidget(QLabel("X (мм):"), 0, 0)
        self.new_x = QDoubleSpinBox()
        self.new_x.setRange(-1000, 1000)
        self.new_x.setValue(self.controller.current_x)
        point_layout.addWidget(self.new_x, 0, 1)
        
        point_layout.addWidget(QLabel("Y (мм):"), 1, 0)
        self.new_y = QDoubleSpinBox()
        self.new_y.setRange(-1000, 1000)
        self.new_y.setValue(self.controller.current_y)
        point_layout.addWidget(self.new_y, 1, 1)
        
        point_layout.addWidget(QLabel("Z (мм):"), 2, 0)
        self.new_z = QDoubleSpinBox()
        self.new_z.setRange(-1000, 1000)
        self.new_z.setValue(self.controller.current_z)
        point_layout.addWidget(self.new_z, 2, 1)

        # self.new_x.editingFinished.connect(self.add_xyz_point)
        # self.new_y.editingFinished.connect(self.add_xyz_point)
        # self.new_z.editingFinished.connect(self.add_xyz_point)
        
        add_btn = QPushButton("Добавить точку")
        add_btn.clicked.connect(self.add_xyz_point)
        point_layout.addWidget(add_btn, 3, 0, 1, 2)
        
        point_group.setLayout(point_layout)
        control_layout.addWidget(point_group)
        
        traj_control_layout = QHBoxLayout()
        
        remove_btn = QPushButton("Удалить точку")
        remove_btn.clicked.connect(self.remove_xyz_point)
        traj_control_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton("Очистить все")
        clear_btn.clicked.connect(self.clear_xyz_trajectory)
        traj_control_layout.addWidget(clear_btn)
        
        home_btn = QPushButton("Вернуться в ноль")
        home_btn.clicked.connect(self.return_to_zero_xyz)
        traj_control_layout.addWidget(home_btn)
        
        control_layout.addLayout(traj_control_layout)
        
        list_group = QGroupBox("Точки траектории")
        list_layout = QVBoxLayout()
        
        self.xyz_listbox = QListWidget()
        list_layout.addWidget(self.xyz_listbox)
        
        execute_btn = QPushButton("Выполнить траекторию")
        execute_btn.clicked.connect(self.execute_xyz_trajectory)
        list_layout.addWidget(execute_btn)
        
        list_group.setLayout(list_layout)
        control_layout.addWidget(list_group)
        
        control_frame.setLayout(control_layout)
        layout.addWidget(control_frame)
        
        vis_frame = QGroupBox("Визуализация траектории")
        vis_layout = QVBoxLayout()
        
        self.xyz_traj_fig = Figure(figsize=(6, 5), dpi=100)
        self.xyz_traj_ax = self.xyz_traj_fig.add_subplot(111, projection='3d')
        
        self.xyz_traj_ax.set_xlabel('X (мм)')
        self.xyz_traj_ax.set_ylabel('Y (мм)')
        self.xyz_traj_ax.set_zlabel('Z (мм)')
        self.xyz_traj_ax.set_title('Траектория движения XYZ')
        
        self.xyz_traj_canvas = FigureCanvas(self.xyz_traj_fig)
        vis_layout.addWidget(self.xyz_traj_canvas)
        
        self.xyz_trajectory_plotter = XYZTrajectoryPlotter(
            ax=self.xyz_traj_ax,
            canvas=self.xyz_traj_canvas,)
        
        vis_frame.setLayout(vis_layout)
        layout.addWidget(vis_frame)
        
        widget.setLayout(layout)
        self.add_initial_xyz_point()
        
        return widget
    
    def create_joints_trajectory_tab(self):
        widget = QWidget()
        main_layout = QHBoxLayout(widget)

        control_frame = QGroupBox("Управление траекторией суставов")
        control_layout = QVBoxLayout(control_frame)

        joints_group = QGroupBox("Добавить позицию суставов")
        joints_layout = QGridLayout(joints_group)

        joints = ['J0', 'J1', 'J2', 'J3', 'J4', 'J5']
        self.new_joints = {}

        for i, joint in enumerate(joints):
            joints_layout.addWidget(QLabel(f"{joint} (°):"), i, 0)
            spinbox = QDoubleSpinBox()
            spinbox.setRange(-180, 180)
            current_value = self.controller.current_joints[i] if i < len(self.controller.current_joints) else 0
            spinbox.setValue(current_value)
            spinbox.setSuffix(" °")
            joints_layout.addWidget(spinbox, i, 1)
            self.new_joints[joint] = spinbox

        add_btn = QPushButton("Добавить позицию")
        add_btn.clicked.connect(self.add_joints_point)
        joints_layout.addWidget(add_btn, 6, 0, 1, 2)

        joints_group.setLayout(joints_layout)
        control_layout.addWidget(joints_group)
        
        traj_control_layout = QHBoxLayout()

        remove_btn = QPushButton("Удалить позицию")
        remove_btn.clicked.connect(self.remove_joints_point)
        traj_control_layout.addWidget(remove_btn)

        clear_btn = QPushButton("Очистить все")
        clear_btn.clicked.connect(self.clear_joints_trajectory)
        traj_control_layout.addWidget(clear_btn)

        home_btn = QPushButton("Вернуться в ноль")
        home_btn.clicked.connect(self.return_to_zero_joints)
        traj_control_layout.addWidget(home_btn)

        control_layout.addLayout(traj_control_layout)

        list_group = QGroupBox("Позиции траектории")
        list_layout = QVBoxLayout(list_group)

        self.joints_listbox = QListWidget()
        list_layout.addWidget(self.joints_listbox)

        execute_btn = QPushButton("Выполнить траекторию")
        execute_btn.clicked.connect(self.execute_joints_trajectory)
        list_layout.addWidget(execute_btn)

        list_group.setLayout(list_layout)
        control_layout.addWidget(list_group)
        control_frame.setLayout(control_layout)
        main_layout.addWidget(control_frame)
        
        vis_frame = QGroupBox("Визуализация траектории")
        vis_layout = QVBoxLayout(vis_frame)

        self.joints_traj_fig = Figure(figsize=(6, 5), dpi=100)
        self.joints_traj_ax = self.joints_traj_fig.add_subplot(111, projection='3d') 

        self.joints_traj_ax.set_xlabel('X (мм)')
        self.joints_traj_ax.set_ylabel('Y (мм)')
        self.joints_traj_ax.set_zlabel('Z (мм)')
        self.joints_traj_ax.set_title('Траектория движения суставов')

        self.joints_traj_canvas = FigureCanvas(self.joints_traj_fig)
        vis_layout.addWidget(self.joints_traj_canvas)

        vis_frame.setLayout(vis_layout)
        main_layout.addWidget(vis_frame)

        widget.setLayout(main_layout)
        return widget


    def robot_settings_tab(self):
        widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Создаем GroupBox для группы настроек
        settings_group = QGroupBox("Настройки скорости робота")
        group_layout = QVBoxLayout()
        
        # → Секция 1: Текущее значение скорости
        current_speed_layout = QHBoxLayout()
        current_speed_layout.addWidget(QLabel("Текущая скорость:"))
        self.current_speed_label = QLabel("10.0 %")  # Начальное значение
        current_speed_layout.addWidget(self.current_speed_label)

        group_layout.addLayout(current_speed_layout)
        
        # → Секция 2: Задание новой скорости
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Задать скорость:"))
        
        self.speed_input = QDoubleSpinBox()
        self.speed_input.setRange(-1000, 1000)
        self.speed_input.setValue(10)  # Текущее значение
        self.speed_input.setSuffix(" %")
        input_layout.addWidget(self.speed_input)
        
        set_speed_btn = QPushButton("Задать")
        # ★ ПРАВИЛЬНОЕ подключение сигнала - разделяем операции
        set_speed_btn.clicked.connect(self.update_speed_display)
        
        input_layout.addWidget(set_speed_btn)
        
        group_layout.addLayout(input_layout)
        group_layout.addStretch(1)
        
        settings_group.setLayout(group_layout)
        main_layout.addWidget(settings_group)
        
        widget.setLayout(main_layout)
        return widget

    def update_speed_display(self):
        """Обновляет отображение текущей скорости"""
        new_speed = self.speed_input.value()
        
        # ★ Обновляем метку с новым значением
        self.current_speed_label.setText(f"{new_speed:.1f} %")
        
        # ★ Вызываем метод контроллера (если нужно)
        self.controller.set_speed_w(new_speed)
        
        # ★ Принудительное обновление интерфейса при необходимости
        self.current_speed_label.repaint()  # :cite[5]

    # Методы управления осями XYZ
    @Slot(str, float)
    def set_xyz_position(self, axis, value):
        if axis in self.xyz_controls:
            self.xyz_controls[axis]['display'].setText(f"{value:.2f}")
            self.xyz_controls[axis]['input'].setValue(value)
        
        positions = {
            'X': self.controller.current_x,
            'Y': self.controller.current_y, 
            'Z': self.controller.current_z
        }
        positions[axis] = value
        
        self.xyz_presenter.set_position(positions['X'], positions['Y'], positions['Z'])

    @Slot(str, float)
    def move_xyz(self, axis, step):
        current = getattr(self.controller, f'current_{axis.lower()}')
        new_value = current + step
        self.set_xyz_position(axis, new_value)

    @Slot()
    def update_xyz_plot(self):
        """Обновление графика XYZ"""
        self.xyz_kinematics_plotter.plot(
            x=self.controller.current_x,
            y=self.controller.current_y,
            z=self.controller.current_z,
        )


    # Методы управления суставами
    @Slot(str, float)
    def set_joint_position(self, joint, value):
        if joint in self.joints_controls:
            self.joints_controls[joint]['display'].setText(f"{value:.2f}")
            self.joints_controls[joint]['input'].setValue(value)
        
        joints = self.controller.current_joints.copy()
        joint_index = int(joint[1])
        if joint_index < len(joints):
            joints[joint_index] = value
            self.controller.set_joint_pos(joints)

    @Slot(str, float)
    def move_joint(self, joint, step):
        joint_index = int(joint[1])
        if joint_index < len(self.controller.current_joints):
            current = self.controller.current_joints[joint_index]
            new_value = current + step
            self.set_joint_position(joint, new_value)

    @Slot()
    def update_joints_plot(self):
            """Обновление графика с кинематической цепочкой для суставов"""
            self.joints_ax.clear()
            
            # Получаем текущие углы суставов
            joints_degrees = self.controller.current_joints
            
            # Отображаем кинематическую цепочку, если доступна
            if self.robot_chain and IKPY_AVAILABLE and len(joints_degrees) >= 6:
                try:
                    # Преобразуем углы из градусов в радианы
                    # Добавляем начальный и конечный углы (обычно 0 для OriginLink и ToolLink)
                    joints_radians = [0] + [np.radians(angle) for angle in joints_degrees[:6]] + [0]
                    
                    # Отображаем кинематическую цепочку
                    self.robot_chain.plot(joints_radians, self.joints_ax)
                    
                except Exception as e:
                    logger(f"Ошибка отображения кинематики суставов: {e}")
                    # Резервный вариант
                    self.joints_ax.scatter([0], [0], [0], c='b', marker='o', s=100, label='База')
            else:
                # Резервный вариант без кинематики
                self.joints_ax.scatter([0], [0], [0], c='b', marker='o', s=100, label='База')
            
            # Настраиваем график
            self.joints_ax.set_xlabel('X (м)')
            self.joints_ax.set_ylabel('Y (м)')
            self.joints_ax.set_zlabel('Z (м)')
            self.joints_ax.set_title('Кинематическая цепочка робота')
            self.joints_ax.legend()
            
            # Устанавливаем разумные пределы для 6-осевого робота
            self.joints_ax.set_xlim([-1, 1])
            self.joints_ax.set_ylim([-1, 1])
            self.joints_ax.set_zlim([0, 1.5])
            
            self.joints_canvas.draw()

    # Методы траекторий XYZ
    @Slot()
    def add_initial_xyz_point(self):
        x = self.controller.current_x
        y = self.controller.current_y
        z = self.controller.current_z

        self.trajectory_service.set_initial_point(x, y, z)

        self.xyz_listbox.clear()
        self.xyz_listbox.addItem(f"1: X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}")

        self.xyz_trajectory_plotter.plot(
            self.trajectory_service.get_points())


    @Slot()
    def add_xyz_point(self):
        x = self.new_x.value()
        y = self.new_y.value()
        z = self.new_z.value()
        
        if self.xyz_availability_service.is_available(x, y, z):
            self.trajectory_service.add_point(x, y, z)
            index = len(self.trajectory_service.get_points())
            self.xyz_listbox.addItem(
                f"{index}: X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}"
            )
            self.xyz_trajectory_plotter.plot(
                self.trajectory_service.get_points())
            
        else:
            logger("The point cannot be moved.", queue=q)

    @Slot()
    def remove_xyz_point(self):
        current_row = self.xyz_listbox.currentRow()
        if current_row >= 0:
            self.xyz_listbox.takeItem(current_row)
            self.trajectory_service.remove_point(current_row)

            self.xyz_listbox.clear()
            for i, (x, y, z) in enumerate(
                self.trajectory_service.get_points()
            ):
                self.xyz_listbox.addItem(
                    f"{i + 1}: X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}"
                )

            self.xyz_trajectory_plotter.plot(
                self.trajectory_service.get_points())

    @Slot()
    def clear_xyz_trajectory(self):
        self.trajectory_service.clear()
        self.xyz_listbox.clear()
        self.xyz_trajectory_plotter.plot(
            self.trajectory_service.get_points())


    @Slot()
    def return_to_zero_xyz(self):
        self.xyz_presenter.return_to_zero()

    @Slot()
    def execute_xyz_trajectory(self):
        if not self.trajectory_service.get_points():
            QMessageBox.critical(self, "Ошибка", "Траектория не задана")
            return
    
        logger('Execution trajectory XYZ...', queue=q)
        self.xyz_trajectory_executor.execute()

    @Slot()
    def update_xyz_trajectory_plot(self):
        self.xyz_traj_ax.clear()

        points_list = self.trajectory_service.get_points()
        if points_list:
            points = np.array(points_list)

            self.xyz_traj_ax.plot(
                points[:, 0], points[:, 1], points[:, 2],
                'b-', linewidth=2, alpha=0.7
            )
            self.xyz_traj_ax.scatter(
                points[:, 0], points[:, 1], points[:, 2],
                c='red', s=30
            )

            for i, (x, y, z) in enumerate(points):
                self.xyz_traj_ax.text(x, y, z, str(i + 1), color='red', fontsize=8)

            if len(points) > 1:
                for i in range(len(points) - 1):
                    x1, y1, z1 = points[i]
                    x2, y2, z2 = points[i + 1]

                    arrow = Arrow3DData(
                        [x1, x2], [y1, y2], [z1, z2],
                        mutation_scale=20,
                        lw=1,
                        arrowstyle="-|>",
                        color="green",
                        alpha=0.7
                    )
                    self.xyz_traj_ax.add_artist(arrow)

        self.xyz_traj_ax.set_xlabel('X (мм)')
        self.xyz_traj_ax.set_ylabel('Y (мм)')
        self.xyz_traj_ax.set_zlabel('Z (мм)')
        self.xyz_traj_ax.set_title('Траектория движения XYZ')

        self.xyz_traj_canvas.draw()

    # Методы траекторий суставов
    @Slot()
    def add_joints_point(self):
        joints = [self.new_joints[f'J{i}'].value() for i in range(6)]
        
        if self.joint_availability_service.is_available(joints):
            self.trajectory_points_joints.add_point(joints)
            index = len(self.trajectory_points_joints.get_points())
            self.joints_listbox.addItem(f"{index}: J0: {joints[0]:.2f}, J1: {joints[1]:.2f}, J2: {joints[2]:.2f}")
            self.joints_trajectory_plotter.plot(
                self.trajectory_points_joints.get_points())
        else:
            # QMessageBox.critical(self, "Ошибка", "Позиция недоступна для перемещения")
            logger("The position cannot be moved.", queue=q)

    @Slot()
    def remove_joints_point(self):
        current_row = self.joints_listbox.currentRow()
        if current_row >= 0:
            self.joints_listbox.takeItem(current_row)
            self.joint_trajectory_service.remove_point(current_row)
            self.joints_trajectory_plotter.plot(
                self.trajectory_points_joints.get_points())
    @Slot()
    def clear_joints_trajectory(self):
        self.joints_listbox.clear()
        self.trajectory_points_joints.clear()
        self.joints_trajectory_plotter.plot(
                self.trajectory_points_joints.get_points())

    @Slot()
    def return_to_zero_joints(self):
        self.controller.set_joint_pos([0, 0, 0, 0, 0, 0])

    @Slot()
    def execute_joints_trajectory(self):
        if not self.trajectory_points_joints.get_points():
            QMessageBox.critical(self, "Ошибка", "Траектория не задана")
            return

        self.joint_trajectory_executor.execute()

    @Slot()
    def update_joints_trajectory_plot(self):
            """Обновление визуализации траектории с кинематической цепочкой"""
            self.joints_traj_ax.clear()
            
            if self.trajectory_points_joints and self.robot_chain and IKPY_AVAILABLE:
                try:
                    # Собираем все позиции инструмента через прямую кинематику
                    tool_positions = []
                    
                    for joints_degrees in self.trajectory_points_joints:
                        if len(joints_degrees) >= 6:
                            # Преобразуем в радианы и добавляем начальный/конечный углы
                            joints_radians = [0] + [np.radians(angle) for angle in joints_degrees[:6]] + [0]
                            
                            # Вычисляем прямую кинематику для получения позиции инструмента
                            transformation_matrix = self.robot_chain.forward_kinematics(joints_radians)
                            tool_position = transformation_matrix[:3, 3]  # Позиция в метрах
                            tool_positions.append(tool_position * 1000)  # Переводим в мм для согласованности
                    
                    if tool_positions:
                        points = np.array(tool_positions)
                        
                        # Рисуем траекторию
                        self.joints_traj_ax.plot(points[:, 0], points[:, 1], points[:, 2], 
                                            'b-', linewidth=2, alpha=0.7, label='Траектория')
                        self.joints_traj_ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                                                c='red', s=30, label='Позиции')
                        
                        # Отображаем кинематическую цепочку для последней позиции
                        last_joints = self.trajectory_points_joints[-1]
                        if len(last_joints) >= 6:
                            joints_radians = [0] + [np.radians(angle) for angle in last_joints[:6]] + [0]
                            self.robot_chain.plot(joints_radians, self.joints_traj_ax)
                            
                except Exception as e:
                    logger(f"Ошибка визуализации траектории суставов: {e}")

            else:
                logger(f"Ошибка визуализации траектории суставов: {e}")
            
            self.joints_traj_ax.set_xlabel('X (мм)')
            self.joints_traj_ax.set_ylabel('Y (мм)')
            self.joints_traj_ax.set_zlabel('Z (мм)')
            self.joints_traj_ax.set_title('Траектория движения суставов с кинематикой')
            self.joints_traj_ax.legend()
            
            self.joints_traj_canvas.draw()

    @Slot()
    def update_status(self):
        status = "Текущий статус системы:\n"
        status += f"- Позиция X: {self.controller.current_x:.2f} мм\n"
        status += f"- Позиция Y: {self.controller.current_y:.2f} мм\n"
        status += f"- Позиция Z: {self.controller.current_z:.2f} мм\n"
        status += f"- Углы суставов: {', '.join([f'{j:.1f}°' for j in self.controller.current_joints])}\n"
        status += "- Эрозия: выключена\n"
        status += "- Вода: отключена\n"
        
        self.status_text.setPlainText(status)

    # Методы непрерывного движения
    def start_continuous_move(self, move_type, target, step):
        self.continuous_move_data = {
            'type': move_type,
            'target': target,
            'step': step
        }
        self.continuous_move_timer.start(50)

    def stop_continuous_move(self):
        self.continuous_move_timer.stop()
        self.continuous_move_data = None

    @Slot()
    def continuous_move(self):
        if not self.continuous_move_data:
            return
        
        move_type = self.continuous_move_data['type']
        target = self.continuous_move_data['target']
        step = self.continuous_move_data['step']
        
        if move_type == 'xyz':
            self.move_xyz(target, step * 0.3)
        elif move_type == 'joint':
            self.move_joint(target, step * 0.3)
# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.X0 = X0
        self.Y0 = Y0
        self.Z0 = Z0
        
        # Централизованное хранение текущих координат
        self.current_x = X0
        self.current_y = Y0
        self.current_z = Z0
        self.current_joints = [0, 0, 0, 0, 0, 0]

        self.state_pump_one = False
        self.state_pump_two = False
        
        # Флаг для предотвращения рекурсивных обновлений
        self.updating_coordinates = False
        
        # Инициализация контроллеров оборудования
        try:
            self.erode = Electroerosion()#, X, Y, Z, XS, YS, ZS)
            self.robot_controller = self.erode.robot
            self.pico_controller = self.erode.erosion
        except Exception as e:
            logger(f'Couldnt connect to the hardware: {str(e)}', queue=q, file=sys.stderr)
            self.robot_controller = None
            self.pico_controller = None
        
        self.video_thread = None
        self.erosion_worker = None
        self.update_textbox = None
        
        self.create_widgets()
        self.setup_video()
        
    def create_widgets(self):
        self.setWindowTitle("Управление электроэрозионной установкой")
        self.setGeometry(100, 100, 1000, 700)
        #self.setFixedSize(1920, 1000) #Фиксированное окно
        self.setMinimumSize(1340, 720)
        self.setMaximumSize(1920, 1000)
        # Центральный виджет с вкладками
        central_widget = QTabWidget()
        self.setCentralWidget(central_widget)
        
        # Вкладка процесса электроэрозии
        self.erosion_tab = ErosionProcessTab(self, q)
        central_widget.addTab(self.erosion_tab, "Процесс электроэрозии")
        
        # Вкладка сервисного управления
        self.service_tab = ServiceTab(self)
        central_widget.addTab(self.service_tab, "Сервисное управление")
        
        # Настройка стиля
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def setup_video(self):
        """Запуск видеопотока"""
        self.video_thread = VideoStreamThread()
        self.video_thread.new_frame.connect(self.update_video_frame)
        self.video_thread.start()
    
    @Slot(QImage)
    def update_video_frame(self, image):
        """Обновление видеокадра"""
        if hasattr(self, 'erosion_tab') and hasattr(self.erosion_tab, 'video_label'):
            pixmap = QPixmap.fromImage(image)
            scaled_pixmap = pixmap.scaled(
                self.erosion_tab.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.erosion_tab.video_label.setPixmap(scaled_pixmap)
    @Slot(int)
    def set_speed_w(self, v):
        if self.robot_controller:
            self.robot_controller.set_speed(v)
        else:
            logger("set speed", v)

    @Slot(float, float, float)
    def set_coord_pos(self, x, y, z):
        """Установка позиции с синхронизацией между вкладками"""
        if self.updating_coordinates:
            return
            
        self.updating_coordinates = True
        
        try:
            # Обновляем центральные координаты
            self.current_x = x
            self.current_y = y
            self.current_z = z
            
            # Отправляем команду роботу (если подключен)
            if self.robot_controller:
                logger(f"Set position: X={x:.2f}, Y={y:.2f}, Z={z:.2f}", queue=q, file=sys.stderr)
                self.erode.set_coord_pos(x, y, z)
            else:
                logger(f"Set position: X={x:.2f}, Y={y:.2f}, Z={z:.2f}", queue=q, file=sys.stderr)
                # if hasattr(self, 'erosion_tab'):
                #     self.erosion_tab.status_text("X={x:.2f}, Y={y:.2f}, Z={z:.2f}")
            
            # Синхронизируем вкладки
            self.sync_coordinates_to_tabs()
            
        except Exception as e:
            # QMessageBox.critical(self, "Ошибка", f"Не удалось установить позицию: {str(e)}")
            logger(f"Couldn't set position:", queue=q)
        finally:
            self.updating_coordinates = False
    
    @Slot(list)
    def set_joint_pos(self, joints):
        """Установка позиции по суставам с синхронизацией"""
        if self.updating_coordinates:
            return
            
        self.updating_coordinates = True
        
        try:
            # Обновляем центральные углы
            self.current_joints = joints[:6]  # Берем только первые 6 суставов
            
            # Отправляем команду роботу (если подключен)
            if self.robot_controller:
                self.robot_controller.set_joint_pos(joints)
            else:

                logger(f"Set joints: {joints}", queue=q)
            
            # Синхронизируем вкладки
            self.sync_joints_to_tabs()
            
        except Exception as e:
            # QMessageBox.critical(self, "Ошибка", f"Не удалось установить углы: {str(e)}")
            logger(f"Couldn't set corners: {str(e)}")
        finally:
            self.updating_coordinates = False
    
    def sync_coordinates_to_tabs(self):
        
        """Синхронизация координат со всеми вкладками"""
        # Синхронизация с сервисной вкладкой
        if hasattr(self, 'service_tab') and self.service_tab:
            # Обновляем отображение в сервисной вкладке
            for axis in ['X', 'Y', 'Z']:
                if (hasattr(self.service_tab, 'xyz_controls') and 
                    axis in self.service_tab.xyz_controls):

                    control = self.service_tab.xyz_controls[axis]
                    value = getattr(self, f'current_{axis.lower()}')
                    control['display'].setText(f"{value:.2f}")
                    control['input'].setValue(value)
            
            # Обновляем графики
            if hasattr(self.service_tab, 'update_xyz_plot'):
                self.service_tab.update_xyz_plot()
        
        # Синхронизация с вкладкой процесса
        if (hasattr(self, 'erosion_tab') and 
            hasattr(self.erosion_tab, 'x_control') and
            hasattr(self.erosion_tab, 'y_control') and 
            hasattr(self.erosion_tab, 'z_control')):
            
            self.erosion_tab.x_control.value_label.setText(f"{self.current_x:.1f} мм")
            self.erosion_tab.y_control.value_label.setText(f"{self.current_y:.1f} мм")
            self.erosion_tab.z_control.value_label.setText(f"{self.current_z:.1f} мм")



        # if (hasattr(self, 'erosion_tab') and
        #     hasattr(self.erosion_tab, 'status_text')):

        #     self.erosion_tab.status_text.append(f"X={self.current_x:.2f}, Y={self.current_y:.2f}, Z={self.current_z:.2f}")
        #     # self.erosion_tab.status_text.clear()
        #     # self.erosion_tab.status_text.append(q.get())
        #     scrollbar = self.erosion_tab.status_text.verticalScrollBar()
        #     scrollbar.setValue(scrollbar.maximum())
    
    def sync_joints_to_tabs(self):
        """Синхронизация углов суставов со вкладками"""
        if hasattr(self, 'service_tab') and self.service_tab:
            for i, joint in enumerate(['J0', 'J1', 'J2', 'J3', 'J4', 'J5']):
                if (hasattr(self.service_tab, 'joints_controls') and 
                    joint in self.service_tab.joints_controls and
                    i < len(self.current_joints)):
                    
                    control = self.service_tab.joints_controls[joint]
                    value = self.current_joints[i]
                    control['display'].setText(f"{value:.2f}")
                    control['input'].setValue(value)
            
            # Обновляем график суставов
            if hasattr(self.service_tab, 'update_joints_plot'):
                self.service_tab.update_joints_plot()
    
    @Slot(bool)
    def set_erosion(self, state):
        """Включение/выключение эрозии"""
        try:
            if self.pico_controller:
                if state:
                    self.pico_controller.erosion(1)
                else:
                    self.pico_controller.erosion(0)
            else:
                status = "ВКЛЮЧЕНА" if state else "ВЫКЛЮЧЕНА"
                logger(f"Эрозия {status} (эмуляция)")
                
                # Обновляем статус в сервисной вкладке
                if hasattr(self, 'service_tab'):
                    self.service_tab.update_status()
                    
        except Exception as e:
            # QMessageBox.critical(self, "Ошибка", f"Не удалось управлять эрозией: {str(e)}")
            logger(f"Erosion control failed: {str(e)}", queue=q)
    
    @Slot(bool)
    def set_water(self, state):
        """Включение/выключение воды"""
        try:
            if self.pico_controller:
                if state:
                    self.pico_controller.pump_in(1)
                    self.pico_controller.pump_out(1)
                else:
                    self.pico_controller.pump_in(0)
                    self.pico_controller.pump_out(0)
            else:
                status = "ВКЛЮЧЕНА" if state else "ВЫКЛЮЧЕНА"
                logger(f"Вода {status} (эмуляция)")
                
                # Обновляем статус в сервисной вкладке
                if hasattr(self, 'service_tab'):
                    self.service_tab.update_status()
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось управлять водой: {str(e)}")
            logger(f"Water control failed: {str(e)}", queue=q)
    
    def pump_control_one(self):
        try:
            if self.pico_controller:
                if not self.state_pump_one:
                    self.pico_controller.pump_in(1)
                    self.state_pump_one = True
                    logger("+")
                else:
                    self.pico_controller.pump_in(0)
                    self.state_pump_one = False
                    logger("-")
            else:
                if not self.state_pump_one:
                    self.state_pump_one = True
                else:
                    self.state_pump_one = False
                status = "ВКЛЮЧЕНА" if self.state_pump_one else "ВЫКЛЮЧЕНА"
                logger(f"Помпа 1 {status} (эмуляция)")
                
                # Обновляем статус в сервисной вкладке
                if hasattr(self, 'service_tab'):
                    self.service_tab.update_status()
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось управлять водой: {str(e)}")
            logger(f"Water control failed: {str(e)}", queue=q)

    def pump_control_two(self):
        try:
            if self.pico_controller:
                if not self.state_pump_two:
                    self.pico_controller.pump_out(1)
                    self.state_pump_two = True
                else:
                    self.pico_controller.pump_out(0)
                    self.state_pump_two = False
            else:
                if not self.state_pump_two:
                    self.state_pump_two = True
                else:
                    self.state_pump_two = False
                status = "ВКЛЮЧЕНА" if self.state_pump_two else "ВЫКЛЮЧЕНА"
                logger(f"Помпа 2 {status} (эмуляция)")
                
                # Обновляем статус в сервисной вкладке
                if hasattr(self, 'service_tab'):
                    self.service_tab.update_status()
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось управлять водой: {str(e)}")
            logger(f"Water control failed: {str(e)}", queue=q)
    

    @Slot(list, float, float, float, float, float,)
    def start_erosion_process(self, gcode_points, electrode_diameter, electrode_length, erosion_time, erosion_up_time, erosion_depth, filename, mode):

        
        logger(f"DEBUG: start_erosion_process called", queue=q)

        """Запуск процесса электроэрозии"""
        try:

            logger(f"Start erosion process with param: ", queue=q)
            logger(f"- Points G-code: {len(gcode_points)} mm", queue=q)
            logger(f"- Diametr electrode: {electrode_diameter} mm", queue=q)
            logger(f"- Length electrode: {electrode_length} mm", queue=q)
            logger(f"- Time erosion: {erosion_time} s", queue=q)
            logger(f"- Time up: {erosion_up_time} s", queue=q)
            logger(f"- Deep: {erosion_depth} mm", queue=q)
            logger(f"- Mode: {mode}", queue=q)

            
            self.erosion_worker = ErosionWorker(self.erode, gcode_points, erosion_time, 
                                            electrode_diameter, electrode_length, 
                                            erosion_time, erosion_up_time, 
                                            erosion_depth, filename)
            
            self.erosion_worker.progress_updated.connect(self.update_erosion_progress)
            self.erosion_worker.time_updated.connect(self.update_erosion_time)
            self.erosion_worker.finished.connect(self.erosion_finished)
            self.erosion_worker.paused.connect(self.erosion_paused)
            self.erosion_worker.resumed.connect(self.erosion_resumed)
            
            self.erosion_worker.start()
            
            # Передаем рабочий поток во вкладку процесса
            self.erosion_tab.set_erosion_worker(self.erosion_worker)
            
            # Обновляем статус во вкладке процесса
            if hasattr(self, 'erosion_tab'):
                self.erosion_tab.status_text.clear()
                self.erosion_tab.update_process_status("ПРОЦЕСС ВЫПОЛНЯЕТСЯ", "#27ae60")
                # self.erosion_tab.status_text.append(f"[{time.strftime('%H:%M:%S')}] Процесс запущен")
                logger("Процесс запущен", queue=q)
                # self.erosion_tab.status_text.append(f"- Всего точек: {len(gcode_points)}")
                # self.erosion_tab.status_text.append(f"- Общее время: {erosion_time} с")
                # self.erosion_tab.status_text.append(f"- Диаметр электрода: {electrode_diameter} мм")
                # self.erosion_tab.status_text.append("="*50)
                
        
            
        except Exception as e:
            # QMessageBox.critical(self, "Ошибка", f"Не удалось запустить процесс: {str(e)}")
            logger(f"Failed to start process: {str(e)}", queue=q)
    @Slot()
    def erosion_paused(self):
        """Обработчик паузы процесса"""
        if hasattr(self, 'erosion_tab'):
            self.erosion_tab.update_process_status("ПРОЦЕСС НА ПАУЗЕ", "#f39c12")
            # self.erosion_tab.status_text.append(f"[{time.strftime('%H:%M:%S')}] Процесс приостановлен")
            logger("Процесс приостановлен", queue=q)

    @Slot()
    def erosion_resumed(self):
        """Обработчик возобновления процесса"""
        if hasattr(self, 'erosion_tab'):
            self.erosion_tab.update_process_status("ПРОЦЕСС ВЫПОЛНЯЕТСЯ", "#27ae60")
            # self.erosion_tab.status_text.append(f"[{time.strftime('%H:%M:%S')}] Процесс возобновлен")
            logger("Процесс возобновлен", queue=q)
            
    @Slot(float)
    def update_erosion_progress(self, progress):
        """Обновление прогресса эрозии"""
        if hasattr(self, 'erosion_tab'):
            self.erosion_tab.progress_bar.setValue(int(progress))
    
    @Slot(str)
    def update_erosion_time(self, time_remaining):
        """Обновление оставшегося времени"""
        if hasattr(self, 'erosion_tab'):
            self.erosion_tab.time_label.setText(f"Осталось: {time_remaining}")
    
    @Slot()
    def erosion_finished(self):
        """Завершение процесса эрозии"""
        if hasattr(self, 'erosion_tab'):
            self.erosion_tab.update_process_status("ПРОЦЕСС ЗАВЕРШЕН", "#3498db")
            self.erosion_tab.start_btn.setEnabled(True)
            self.erosion_tab.pause_btn.setEnabled(False)
            self.erosion_tab.pause_btn.setText("⏸ Пауза")
            self.erosion_tab.progress_bar.setValue(100)
            self.erosion_tab.time_label.setText("Завершено")
            # self.erosion_tab.status_text.append(f"[{time.strftime('%H:%M:%S')}] Процесс завершен")
            logger('Process finished', queue=q)
    
    @Slot()
    def stop_erosion_process(self):
        """Остановка процесса электроэрозии"""
        try:
            if self.erosion_worker and self.erosion_worker.isRunning():
                self.erosion_worker.stop()
                if not self.erosion_worker.wait(2000):  # Ждем до 2 секунд
                    self.erosion_worker.terminate()
                    self.erosion_worker.wait()
            
            # Обновляем UI
            if hasattr(self, 'erosion_tab'):
                self.erosion_tab.start_btn.setEnabled(True)
                self.erosion_tab.pause_btn.setEnabled(False)
                self.erosion_tab.pause_btn.setText("⏸ Пауза")
                self.erosion_tab.pause_btn.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
                self.erosion_tab.progress_bar.setValue(0)
                self.erosion_tab.time_label.setText("Остановлено")
                self.erosion_tab.is_process_paused = False
                self.erosion_tab.update_process_status("ПРОЦЕСС ОСТАНОВЛЕН", "#e74c3c")
            logger("Stop proccess electroerosion")
        except Exception as e:
            logger(f"Couldn't stop the process: {str(e)}", queue=q)
            
    @Slot()
    def emergency_stop(self):
        """Аварийная остановка"""
        if hasattr(self, 'service_tab'):
            self.service_tab.stop_continuous_move()
            
    @Slot()
    def safe_finish(self):
        """Безопасное завершение"""
        try:
            # Останавливаем процесс эрозии
            self.stop_erosion_process()
            
            # Выключаем системы
            self.set_erosion(False)
            self.set_water(False)
            
            # Возвращаем в исходное положение
            self.set_coord_pos(self.X0, self.Y0, self.Z0)
            
            # Останавливаем видео поток
            if self.video_thread:
                self.video_thread.stop()
            
        except Exception as e:
            logger(f"Ошибка при безопасном завершении: {e}")
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        # reply = QMessageBox.question(
        #     self,
        #     "Подтверждение",
        #     "Вы уверены, что хотите закрыть приложение?",
        #     QMessageBox.Yes | QMessageBox.No,
        #     QMessageBox.No
        # )
        
        self.safe_finish()
 
    def update_process_status(self, status, color="#ecf0f1"):
        """Обновление статуса процесса"""
        self.process_status_label.setText(status)
        self.process_status_label.setStyleSheet(f"""
            font-weight: bold; 
            font-size: 12pt; 
            padding: 10px;
            border-radius: 5px;
            background-color: {color};
        """)

""" class LogTextBoxErrosion(QThread):

    new_message = Signal(str)
    def __init__(self, queue, latency=100):
        super().__init__()
        self.queue = queue
        self.running = True

    def run(self):
        while self.running:
            try:
                # Пытаемся получить сообщение из очереди без блокировки
                message = self.queue.get_nowait()
                self.new_message.emit(message)
            except queue.Empty:
                # Если очередь пуста, ждем немного и продолжаем
                self.msleep(self.latency)
                continue

    def stop(self):
        self.running = False """


# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Установка стиля приложения
    app.setStyle('Fusion')
    
    # Настройка глобального стиля
    app.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 8px 16px;
            text-align: center;
            text-decoration: none;
            font-size: 14px;
            margin: 4px 2px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        QProgressBar {
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            width: 20px;
        }
        QTextEdit {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px;
            background-color: white;
        }
        QLineEdit {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px;
            background-color: white;
        }
        QDoubleSpinBox {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px;
            background-color: white;
        }
    """)
    
    window = MainWindow()
    window.showMaximized()
    
    sys.exit(app.exec())