from src.erosion_worker.erosion_worker import ErosionWorker, ErosionController, GCodeProcessor
from src.electoerosion import Electroerosion
from src.log import logger, q

# Process management (SRP)
class ProcessManager:
    def __init__(self, hardware_controller, erosion_tab, state_manager):
        self.hardware = hardware_controller
        self.erosion_tab = erosion_tab
        self.state = state_manager
        self.erosion_worker = None

    def start_erosion_process(self, gcode_points, electrode_diameter, electrode_length, erosion_time, erosion_up_time, erosion_depth, filename, mode):
        erosion_controller = ErosionController(Electroerosion, filename, logger=logger, speed=10, mode=mode)
        gcode_processor = GCodeProcessor(gcode_points, erosion_time)
        self.erosion_worker = ErosionWorker(erosion_controller, gcode_processor)
        self.erosion_worker.progress_updated.connect(lambda p: self.erosion_tab.progress_bar.setValue(int(p)))
        self.erosion_worker.time_updated.connect(lambda t: self.erosion_tab.time_label.setText(f"Осталось: {t}"))
        self.erosion_worker.finished.connect(self.erosion_finished)
        self.erosion_worker.paused.connect(self.erosion_paused)
        self.erosion_worker.resumed.connect(self.erosion_resumed)
        self.erosion_worker.start()
        self.erosion_tab.set_erosion_worker(self.erosion_worker)
        self.erosion_tab.update_process_status("ПРОЦЕСС ВЫПОЛНЯЕТСЯ", "#27ae60")
        logger("Процесс запущен", queue=q)

    def stop_erosion_process(self):
        if self.erosion_worker and self.erosion_worker.isRunning():
            self.erosion_worker.stop()
            self.erosion_worker.wait(2000) or self.erosion_worker.terminate()
        self.erosion_tab.set_stopped_ui_state()
        self.erosion_tab.update_process_status("ПРОЦЕСС ОСТАНОВЛЕН", "#e74c3c")

    def erosion_finished(self):
        self.erosion_tab.update_process_status("ПРОЦЕСС ЗАВЕРШЕН", "#3498db")

    def erosion_paused(self):
        self.erosion_tab.update_process_status("ПРОЦЕСС НА ПАУЗЕ", "#f39c12")

    def erosion_resumed(self):
        self.erosion_tab.update_process_status("ПРОЦЕСС ВЫПОЛНЯЕТСЯ", "#27ae60")