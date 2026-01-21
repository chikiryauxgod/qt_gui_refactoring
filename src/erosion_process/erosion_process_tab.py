from __future__ import annotations

import os
import re
import time
import queue
from dataclasses import dataclass
from typing import Callable, Optional, Protocol, Sequence, Tuple, List

import numpy as np

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDoubleSpinBox,
    QProgressBar, QTextEdit, QGroupBox, QFileDialog, QMessageBox, QGridLayout,
    QLineEdit, QStackedWidget, QComboBox
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QTextCursor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from src.log_text.log_text_box_erosion import QueueMessageSource, LogTextBoxErrosion
from src.widgets.axis_control_widget import AxisControlWidget
from src.arrow3D import Arrow3DData


Point3D = Tuple[float, float, float]

class ILogReader(Protocol):
    def isRunning(self) -> bool: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def wait(self, msec: int) -> bool: ...


class ILogReaderFactory(Protocol):
    def create(self, on_message: Callable[[str], None]) -> ILogReader: ...


class QtQueueLogReaderFactory:
    def __init__(self, q_ref: "queue.Queue"):
        self._q = q_ref

    def create(self, on_message: Callable[[str], None]) -> ILogReader:
        source = QueueMessageSource(self._q)
        reader = LogTextBoxErrosion(source, latency_ms=100)
        reader.new_message.connect(on_message)
        return reader


class LogReaderController:
    def __init__(self, factory: ILogReaderFactory):
        self._factory = factory
        self._reader: Optional[ILogReader] = None

    def start(self, on_message: Callable[[str], None]) -> None:
        if self._reader and self._reader.isRunning():
            return
        self._reader = self._factory.create(on_message)
        self._reader.start()

    def stop(self) -> None:
        if self._reader and self._reader.isRunning():
            self._reader.stop()
            self._reader.wait(1000)


class GCodeParser:
    def parse_file(self, filename: str) -> List[Point3D]:
        points: List[Point3D] = []
        cx = cy = cz = 0.0

        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith(";"):
                    continue
                if ";" in line:
                    line = line.split(";", 1)[0].strip()
                    if not line:
                        continue

                if line.startswith(("G0", "G1", "G00", "G01")):
                    x = self._extract(line, "X", cx)
                    y = self._extract(line, "Y", cy)
                    z = self._extract(line, "Z", cz)
                    if (x, y, z) != (cx, cy, cz):
                        points.append((x, y, z))
                        cx, cy, cz = x, y, z

        return points or [(0.0, 0.0, 0.0)]

    @staticmethod
    def _extract(line: str, axis: str, default: float) -> float:
        m = re.search(rf"{axis}([+-]?\d*\.?\d+)", line)
        return float(m.group(1)) if m else default


class GCodeMetrics:
    @staticmethod
    def path_length(points: Sequence[Point3D]) -> float:
        if len(points) < 2:
            return 0.0
        total = 0.0
        for i in range(1, len(points)):
            x1, y1, z1 = points[i - 1]
            x2, y2, z2 = points[i]
            total += float(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2))
        return total

    @staticmethod
    def ranges(points: Sequence[Point3D]):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        zs = [p[2] for p in points]
        return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))


@dataclass(frozen=True)
class ErosionRunParams:
    electrode_diameter: float
    electrode_length: float
    erosion_time: float
    erosion_up_time: float
    erosion_depth: float
    mode: str


class IErosionProcessView(Protocol):
    def show_error(self, title: str, text: str) -> None: ...
    def set_gcode_info(self, text: str) -> None: ...
    def plot_gcode(self, points: Sequence[Point3D]) -> None: ...
    def append_log(self, message: str) -> None: ...
    def set_started_ui_state(self) -> None: ...
    def set_stopped_ui_state(self) -> None: ...
    def set_paused_ui_state(self) -> None: ...
    def set_running_ui_state(self) -> None: ...


class ErosionProcessPresenter:
    def __init__(self, controller, view: IErosionProcessView, q_ref: "queue.Queue"):
        self._controller = controller
        self._view = view
        self._parser = GCodeParser()
        self._metrics = GCodeMetrics()
        self._log_reader = LogReaderController(QtQueueLogReaderFactory(q_ref))

        self._points: List[Point3D] = []
        self._filename: str = ""

    def load_gcode(self, filename: str) -> None:
        if not filename:
            self._view.show_error("Ошибка", "Выберите файл G-code")
            return
        if not filename.lower().endswith((".gcode", ".nc")):
            self._view.show_error("Ошибка", "Файл должен быть .gcode или .nc")
            return
        if not os.path.exists(filename):
            self._view.show_error("Ошибка", "G-code файл не найден")
            return

        points = self._parser.parse_file(filename)
        self._points = points
        self._filename = filename

        (xmin, xmax), (ymin, ymax), (zmin, zmax) = self._metrics.ranges(points)
        info_text = (
            f"Файл: {os.path.basename(filename)}\n"
            f"Количество точек: {len(points)}\n"
            f"Диапазон X: {xmin:.2f} - {xmax:.2f} мм\n"
            f"Диапазон Y: {ymin:.2f} - {ymax:.2f} мм\n"
            f"Диапазон Z: {zmin:.2f} - {zmax:.2f} мм\n"
            f"Общая длина траектории: {self._metrics.path_length(points):.2f} мм\n"
        )
        self._view.set_gcode_info(info_text)
        self._view.plot_gcode(points)

    def start_erosion(self, params: ErosionRunParams) -> None:
        if not self._points:
            self._view.show_error("Ошибка", "Сначала загрузите G-code файл")
            return
        if not self._filename or not os.path.exists(self._filename):
            self._view.show_error("Ошибка", "G-code файл не выбран или не существует")
            return

        self._log_reader.start(self._view.append_log)

        self._controller.start_erosion_process(
            self._points,
            params.electrode_diameter,
            params.electrode_length,
            params.erosion_time,
            params.erosion_up_time,
            params.erosion_depth,
            self._filename,
            params.mode,
        )
        self._view.set_started_ui_state()

    def stop_erosion(self, worker) -> None:
        self._log_reader.stop()

        if worker and worker.isRunning():
            worker.stop()
            worker.wait(1000)

        if hasattr(self._controller, "stop_erosion_process"):
            self._controller.stop_erosion_process()

        self._view.set_stopped_ui_state()

    def toggle_pause(self, worker, paused: bool) -> bool:
        if worker is None or not worker.isRunning():
            self._view.append_log("Worker not running or doesn't exist")
            return paused

        if not paused:
            worker.pause()
            self._view.set_paused_ui_state()
            return True

        worker.resume()
        self._view.set_running_ui_state()
        return False

    def return_to_zero(self) -> None:
        self._controller.set_coord_pos(self._controller.X0, self._controller.Y0, self._controller.Z0)

class ErosionProcessTab(QWidget):
    def __init__(self, controller, q_ref):
        super().__init__()
        self.controller = controller
        self._q = q_ref

        self.current_step = 0
        self.gcode_points: List[Point3D] = []
        self.erosion_worker = None
        self.is_process_paused = False

        self._presenter = ErosionProcessPresenter(
            controller=controller,
            view=self,
            q_ref=q_ref,
        )

        self.create_widgets()

    
    def show_error(self, title: str, text: str) -> None:
        QMessageBox.critical(self, title, text)

    def set_gcode_info(self, text: str) -> None:
        self.gcode_info_text.setPlainText(text)

    def plot_gcode(self, points: Sequence[Point3D]) -> None:
        self.gcode_points = list(points)
        self.visualize_gcode()

    @Slot(str)
    def append_log(self, message: str) -> None:
        self.status_text.append(message)
        cursor = self.status_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.status_text.setTextCursor(cursor)

    def set_started_ui_state(self) -> None:
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.pause_btn.setText("⏸ Пауза")
        self.is_process_paused = False
        self.update_process_status("ПРОЦЕСС ВЫПОЛНЯЕТСЯ", "#27ae60")

    def set_stopped_ui_state(self) -> None:
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸ Пауза")
        self.pause_btn.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
        self.is_process_paused = False
        self.progress_bar.setValue(0)
        self.time_label.setText("Остановлено")

    def set_paused_ui_state(self) -> None:
        self.pause_btn.setText("▶ Продолжить")
        self.pause_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        self.update_process_status("ПРОЦЕСС НА ПАУЗЕ", "#f39c12")

    def set_running_ui_state(self) -> None:
        self.pause_btn.setText("⏸ Пауза")
        self.pause_btn.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
        self.update_process_status("ПРОЦЕСС ВЫПОЛНЯЕТСЯ", "#27ae60")


    def create_widgets(self):
        main_layout = QVBoxLayout()

        title_label = QLabel("Процесс электроэрозии")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        self.step_indicator = QLabel("Шаг 0: Загрузка G-code файла")
        self.step_indicator.setStyleSheet("font-weight: bold;")
        self.step_indicator.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.step_indicator)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.create_step0())
        self.stacked_widget.addWidget(self.create_step1())
        self.stacked_widget.addWidget(self.create_step2())
        self.stacked_widget.addWidget(self.create_step3())
        main_layout.addWidget(self.stacked_widget)

        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("Назад")
        self.prev_btn.clicked.connect(self.prev_step)
        self.prev_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Далее")
        self.next_btn.clicked.connect(self.next_step)
        nav_layout.addWidget(self.next_btn)

        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)

        self.setLayout(main_layout)
        self.show_step(0)

    def create_step0(self):
        widget = QWidget()
        layout = QHBoxLayout()

        left_widget = QGroupBox("Загрузка G-code файла")
        left_layout = QVBoxLayout()

        file_frame = QWidget()
        file_layout = QHBoxLayout(file_frame)

        self.gcode_file_edit = QLineEdit()
        self.gcode_file_edit.setPlaceholderText("Выберите G-code файл...")
        file_layout.addWidget(self.gcode_file_edit)

        browse_btn = QPushButton("Обзор")
        browse_btn.clicked.connect(self.select_gcode_file)
        file_layout.addWidget(browse_btn)

        left_layout.addWidget(file_frame)

        info_group = QGroupBox("Информация о G-code")
        info_layout = QVBoxLayout()

        self.gcode_info_text = QTextEdit()
        self.gcode_info_text.setReadOnly(True)
        info_layout.addWidget(self.gcode_info_text)

        info_group.setLayout(info_layout)
        left_layout.addWidget(info_group)

        left_widget.setLayout(left_layout)
        layout.addWidget(left_widget)

        right_widget = QGroupBox("Визуализация G-code")
        right_layout = QVBoxLayout()

        self.gcode_fig = Figure(figsize=(6, 5), dpi=100)
        self.gcode_ax = self.gcode_fig.add_subplot(111, projection="3d")
        self.gcode_ax.set_xlabel("X (мм)")
        self.gcode_ax.set_ylabel("Y (мм)")
        self.gcode_ax.set_zlabel("Z (мм)")
        self.gcode_ax.set_title("Визуализация траектории G-code")

        self.gcode_canvas = FigureCanvas(self.gcode_fig)
        right_layout.addWidget(self.gcode_canvas)

        right_widget.setLayout(right_layout)
        layout.addWidget(right_widget)

        widget.setLayout(layout)
        return widget

    def create_step1(self):
        widget = QWidget()
        layout = QHBoxLayout()

        left_widget = QGroupBox("Видеопоток с камеры")
        left_layout = QVBoxLayout()

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("border: 1px solid gray;")
        self.video_label.setText("Загрузка видеопотока...")
        left_layout.addWidget(self.video_label)

        left_widget.setLayout(left_layout)
        layout.addWidget(left_widget)

        right_widget = QGroupBox("Управление положением робота")
        right_layout = QVBoxLayout()

        axes_widget = QWidget()
        axes_layout = QHBoxLayout()

        self.x_control = AxisControlWidget("X")
        self.x_control.set_current_value(self.controller.current_x)

        self.y_control = AxisControlWidget("Y")
        self.y_control.set_current_value(self.controller.current_y)

        self.z_control = AxisControlWidget("Z")
        self.z_control.set_current_value(self.controller.current_z)

        reset_btn = QPushButton("Вернуться в нулевое положение")
        reset_btn.clicked.connect(self.return_to_zero_xyz)
        reset_btn.setStyleSheet("""
            QPushButton { background-color: #ff6b6b; color: white; font-weight: bold; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #ff5252; }
            QPushButton:pressed { background-color: #e53935; }
            QPushButton:disabled { background-color: #808080; }
        """)

        self.x_control.position_changed.connect(self.on_position_changed)
        self.y_control.position_changed.connect(self.on_position_changed)
        self.z_control.position_changed.connect(self.on_position_changed)

        axes_layout.addWidget(self.x_control)
        axes_layout.addWidget(self.y_control)
        axes_layout.addWidget(self.z_control)
        axes_widget.setLayout(axes_layout)

        right_layout.addWidget(axes_widget)
        right_layout.addStretch(1)
        right_layout.addWidget(reset_btn)

        right_widget.setLayout(right_layout)
        layout.addWidget(right_widget)

        widget.setLayout(layout)
        return widget

    def create_step2(self):
        widget = QWidget()
        layout = QVBoxLayout()

        params_group = QGroupBox("Параметры электроэрозионной обработки")
        params_layout = QGridLayout()

        parameters = [
            ("Толщина электрода (мм)", "electrode_diameter", 2.0, 0.1, 10.0),
            ("Длина электрода (мм)", "electrode_length", 100.0, 10.0, 500.0),
            ("Время прожига (с)", "erosion_time", 10.0, 1.0, 60.0),
            ("Время поднятия электрода (с)", "erosion_up_time", 5.0, 1.0, 30.0),
            ("Глубина прожига (мм)", "erosion_depth", 0.1, 0.01, 1.0),
            ("Скорость перемещения (мм/с)", "erosion_speed", 10.0, 1.0, 100.0),
        ]

        self.param_spinboxes = {}
        for i, (label, name, default, min_val, max_val) in enumerate(parameters):
            params_layout.addWidget(QLabel(label), i, 0)
            spin = QDoubleSpinBox()
            spin.setRange(min_val, max_val)
            spin.setValue(default)
            spin.setSingleStep(0.1 if max_val > 10 else 0.01)
            spin.setSuffix(" мм" if "мм" in label else " с")
            self.param_spinboxes[name] = spin
            params_layout.addWidget(spin, i, 1)

        params_layout.addWidget(QLabel("Режим эррозии"), 6, 0)
        self.coombbox = QComboBox()
        self.coombbox.addItems(["emulated", "work", "test"])
        params_layout.addWidget(self.coombbox, 6, 1)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        scheme_label = QLabel("Схема параметров электроэрозии")
        scheme_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(scheme_label)

        scheme_placeholder = QLabel("Место для схемы параметров")
        scheme_placeholder.setAlignment(Qt.AlignCenter)
        scheme_placeholder.setStyleSheet("border: 1px dashed gray; min-height: 200px;")
        layout.addWidget(scheme_placeholder)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_step3(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        status_group = QGroupBox("Статус процесса")
        status_layout = QVBoxLayout()

        self.process_status_label = QLabel("Готов к запуску")
        self.process_status_label.setStyleSheet("""
            font-weight: bold; font-size: 12pt; padding: 10px; border-radius: 5px; background-color: #ecf0f1;
        """)
        self.process_status_label.setAlignment(Qt.AlignCenter)
        self.process_status_label.setMinimumHeight(40)
        status_layout.addWidget(self.process_status_label)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        progress_group = QGroupBox("Прогресс выполнения")
        progress_layout = QVBoxLayout()
        progress_bar_layout = QHBoxLayout()
        progress_bar_layout.addWidget(QLabel("Прогресс:"))

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_bar_layout.addWidget(self.progress_bar, 1)

        self.time_label = QLabel("Осталось: --:--")
        progress_bar_layout.addWidget(self.time_label)

        progress_layout.addLayout(progress_bar_layout)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        current_group = QGroupBox("Текущие параметры")
        current_layout = QVBoxLayout()

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        current_layout.addWidget(self.status_text)

        current_group.setLayout(current_layout)
        layout.addWidget(current_group)

        control_layout = QHBoxLayout()

        self.start_btn = QPushButton("Запуск")
        self.start_btn.clicked.connect(self.start_erosion)
        control_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("⏸ Пауза")
        self.pause_btn.setEnabled(False)
        self.pause_btn.setMinimumHeight(40)
        self.pause_btn.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
        self.pause_btn.clicked.connect(self.toggle_pause)
        control_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("Стоп")
        self.stop_btn.clicked.connect(self.stop_erosion)
        control_layout.addWidget(self.stop_btn)

        self.changetool = QPushButton("Заменить инструмент")
        self.changetool.clicked.connect(self.ChangeTools)
        control_layout.addWidget(self.changetool)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        widget.setLayout(layout)
        return widget

    # -------- wired handlers --------
    @Slot()
    def select_gcode_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите G-code файл", "", "G-code files (*.gcode *.nc);;All files (*.*)"
        )
        if filename:
            self.gcode_file_edit.setText(filename)
            self._presenter.load_gcode(filename)

    @Slot()
    def start_erosion(self):
        params = ErosionRunParams(
            electrode_diameter=self.param_spinboxes["electrode_diameter"].value(),
            electrode_length=self.param_spinboxes["electrode_length"].value(),
            erosion_time=self.param_spinboxes["erosion_time"].value(),
            erosion_up_time=self.param_spinboxes["erosion_up_time"].value(),
            erosion_depth=self.param_spinboxes["erosion_depth"].value(),
            mode=self.coombbox.currentText(),
        )
        self._presenter.start_erosion(params)

    def set_erosion_worker(self, worker):
        self.erosion_worker = worker

    @Slot()
    def toggle_pause(self):
        self.is_process_paused = self._presenter.toggle_pause(self.erosion_worker, self.is_process_paused)

    @Slot()
    def stop_erosion(self):
        self._presenter.stop_erosion(self.erosion_worker)
        self.update_process_status("ПРОЦЕСС ОСТАНОВЛЕН", "#e74c3c")

    def visualize_gcode(self):
        self.gcode_ax.clear()
        if self.gcode_points:
            points = np.array(self.gcode_points)
            self.gcode_ax.plot(points[:, 0], points[:, 1], points[:, 2], "b-", linewidth=2, alpha=0.7)
            self.gcode_ax.scatter(
                points[:, 0], points[:, 1], points[:, 2],
                c=range(len(points)), cmap="viridis", s=20, alpha=0.6
            )

            if len(points) > 1:
                for i in range(0, len(points) - 1, max(1, len(points) // 10)):
                    x1, y1, z1 = points[i]
                    x2, y2, z2 = points[i + 1]
                    dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
                    length = np.sqrt(dx**2 + dy**2 + dz**2)
                    if length > 0:
                        dx, dy, dz = dx / length * 10, dy / length * 10, dz / length * 10
                        arrow = Arrow3DData(
                            [x1, x1 + dx], [y1, y1 + dy], [z1, z1 + dz],
                            mutation_scale=15, lw=1, arrowstyle="-|>", color="red", alpha=0.7
                        )
                        self.gcode_ax.add_artist(arrow)
        self.gcode_canvas.draw()

    @Slot()
    def show_step(self, step_index):
        self.stacked_widget.setCurrentIndex(step_index)
        self.current_step = step_index
        step_names = [
            "Шаг 0: Загрузка G-code файла",
            "Шаг 1: Настройка начального положения",
            "Шаг 2: Настройка процесса эрозии",
            "Шаг 3: Запуск процесса эрозии",
        ]
        self.step_indicator.setText(step_names[step_index])
        self.prev_btn.setEnabled(step_index > 0)
        self.next_btn.setEnabled(step_index < self.stacked_widget.count() - 1)

    @Slot()
    def next_step(self):
        if self.current_step < self.stacked_widget.count() - 1:
            self.show_step(self.current_step + 1)

    @Slot()
    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    @Slot(str, float)
    def on_position_changed(self, axis, value):
        positions = {"X": self.x_control, "Y": self.y_control, "Z": self.z_control}
        x = float(positions["X"].value_label.text().split()[0])
        y = float(positions["Y"].value_label.text().split()[0])
        z = float(positions["Z"].value_label.text().split()[0])
        self.controller.set_coord_pos(x, y, z)

    def update_process_status(self, status, color="#ecf0f1"):
        self.process_status_label.setText(status)
        self.process_status_label.setStyleSheet(f"""
            font-weight: bold;
            font-size: 12pt;
            padding: 10px;
            border-radius: 5px;
            background-color: {color};
        """)

    @Slot()
    def ChangeTools(self):
        if self.erosion_worker and self.erosion_worker.isRunning():
            self.erosion_worker.pause()
            self.is_process_paused = True
            self.set_paused_ui_state()
        QMessageBox.information(self, "Смена инструмента", "Замените инструмент, затем нажмите кнопку продолжить")

    @Slot()
    def return_to_zero_xyz(self):
        self._presenter.return_to_zero()
