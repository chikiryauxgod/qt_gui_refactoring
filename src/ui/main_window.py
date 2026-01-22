from src.services.hardware_controller import HardwareController
from src.domain.state_manager import StateManager
from src.ui.video_manager import VideoManager
from src.application.process_manager import ProcessManager
from PySide6.QtWidgets import QMainWindow, QTabWidget
from PySide6.QtCore import Slot
from src.log import logger, q
from src.ui.ui_manager import UIManager
from src.services.service_tab import ServiceTab
from src.erosion_process.erosion_process_tab import ErosionProcessTab
from src.domain.constants import X0, Y0, Z0

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hardware = HardwareController()
        self.state = StateManager(X0, Y0, Z0, self.hardware.robot)
        self.video_manager = VideoManager()
        self.process_manager = None
        self.ui_manager = None
        self.create_widgets()
        self.video_manager.start()

    def create_widgets(self):
        self.setWindowTitle("Управление электроэрозионной установкой")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(1340, 720)
        self.setMaximumSize(1920, 1000)

        central_widget = QTabWidget()
        self.setCentralWidget(central_widget)

        self.erosion_tab = ErosionProcessTab(self, q)
        central_widget.addTab(self.erosion_tab, "Процесс электроэрозии")

        self.service_tab = ServiceTab(self)
        central_widget.addTab(self.service_tab, "Сервисное управление")

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

        self.video_manager.video_label = self.erosion_tab.video_label
        self.process_manager = ProcessManager(self.hardware, self.erosion_tab, self.state)
        self.ui_manager = UIManager(self.erosion_tab, self.service_tab, self.state)

    @Slot(float, float, float)
    def set_coord_pos(self, x, y, z):
        if self.state.updating:
            return
        self.state.updating = True
        try:
            self.hardware.set_coord_pos(x, y, z)
            self.state.sync_from_robot()
            self.ui_manager.sync_coordinates_to_tabs()
        except Exception as e:
            logger(f"Couldn't set position: {str(e)}", queue=q)
        finally:
            self.state.updating = False

    @Slot(list)
    def set_joint_pos(self, joints):
        if self.state.updating:
            return
        self.state.updating = True
        try:
            self.hardware.set_joint_pos(joints)
            self.state.current_joints = joints[:6]
            self.ui_manager.sync_joints_to_tabs()
        except Exception as e:
            logger(f"Couldn't set joints: {str(e)}", queue=q)
        finally:
            self.state.updating = False

    @Slot(bool)
    def set_erosion(self, state):
        self.hardware.set_erosion(state)
        if hasattr(self.service_tab, 'update_status'):
            self.service_tab.update_status()

    @Slot(bool)
    def set_water(self, state):
        self.hardware.set_water(state)
        if hasattr(self.service_tab, 'update_status'):
            self.service_tab.update_status()

    def pump_control_one(self):
        self.hardware.pump_control_one()
        if hasattr(self.service_tab, 'update_status'):
            self.service_tab.update_status()

    def pump_control_two(self):
        self.hardware.pump_control_two()
        if hasattr(self.service_tab, 'update_status'):
            self.service_tab.update_status()

    @Slot(int)
    def set_speed_w(self, v):
        self.hardware.set_speed(v)

    @Slot(list, float, float, float, float, float, str, str)
    def start_erosion_process(self, gcode_points, electrode_diameter, electrode_length, erosion_time, erosion_up_time, erosion_depth, filename, mode):
        self.process_manager.start_erosion_process(gcode_points, electrode_diameter, electrode_length, erosion_time, erosion_up_time, erosion_depth, filename, mode)

    @Slot()
    def stop_erosion_process(self):
        self.process_manager.stop_erosion_process()

    @Slot()
    def emergency_stop(self):
        self.hardware.emergency_stop()
        if hasattr(self.service_tab, 'stop_continuous_move'):
            self.service_tab.stop_continuous_move()

    def safe_finish(self):
        self.process_manager.stop_erosion_process()
        self.hardware.set_erosion(False)
        self.hardware.set_water(False)
        self.set_coord_pos(X0, Y0, Z0)
        self.video_manager.stop()

    def closeEvent(self, event):
        self.safe_finish()
        super().closeEvent(event)