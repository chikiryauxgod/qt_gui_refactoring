import threading
import time

from PySide6.QtCore import QThread, Signal

class ErosionController:
    def __init__(self, erosion_target, filename=None, logger=None, **params):
        self.filename = filename
        self.params = params
        self.logger = logger
        self.erosion_target = erosion_target
        self.erosion_instance = None

        if isinstance(erosion_target, type):
            self.erosion_instance = erosion_target(filename=filename, **params)
        elif hasattr(erosion_target, "start") or hasattr(erosion_target, "stop"):
            self.erosion_instance = erosion_target

    def start_erosion(self):
        if self.logger:
            self.logger(f"Starting erosion: filename={self.filename}, params={self.params}")

        target = self.erosion_instance or self.erosion_target
        if hasattr(target, "start"):
            target.start()
            return
        if callable(target):
            target(self.filename, **self.params)
            return

        raise TypeError("Unsupported erosion target: expected class, callable, or object with start()")

    def stop_erosion(self):
        target = self.erosion_instance or self.erosion_target
        if hasattr(target, "stop"):
            target.stop()
            return
        if hasattr(target, "safe_finish"):
            target.safe_finish()


class GCodeProcessor:
    # Отвечает за прогресс по точкам G-code
    def __init__(self, gcode_points, total_time):
        self.gcode_points = gcode_points
        self.total_time = total_time
        self.current_index = 0
        self.total_points = len(gcode_points)

    def get_progress(self):
        return min(100, (self.current_index + 1) / self.total_points * 100)

    def get_remaining_time(self, elapsed):
        remaining = max(0, self.total_time - elapsed)
        return f"{int(remaining // 60):02d}:{int(remaining % 60):02d}"


#Поток выполнения
class ErosionWorker(QThread):
    progress_updated = Signal(float)
    time_updated = Signal(str)
    finished = Signal()
    paused = Signal()
    resumed = Signal()

    def __init__(self, erosion_controller: ErosionController, gcode_processor: GCodeProcessor):
        super().__init__()
        self.controller = erosion_controller
        self.processor = gcode_processor
        self.is_running = True
        self.is_paused = False
        self.start_time = None
        self.pause_start_time = None
        self.total_paused_time = 0
        self._stop_requested = False
        self._stop_lock = threading.Lock()

    def run(self):
        self.start_time = time.time()
        try:
            # Раскоментировать для работы
            self.controller.start_erosion()

            # Имитация прогресса по G-code
            #for i, point in enumerate(self.processor.gcode_points[self.processor.current_index:],
            #                          self.processor.current_index):
            #    if not self.is_running:
            #        break

            #    # Обработка паузы
            #    while self.is_paused and self.is_running:
            #        if self.pause_start_time is None:
            #            self.pause_start_time = time.time()
            #            self.paused.emit()
            #        QThread.msleep(100)
            #    if self.pause_start_time is not None:
            #        self.total_paused_time += time.time() - self.pause_start_time
            #        self.pause_start_time = None
            #        self.resumed.emit()

            #    # Обновляем прогресс
            #    self.processor.current_index = i
            #    elapsed = time.time() - self.start_time - self.total_paused_time
            #    self.progress_updated.emit(self.processor.get_progress())
            #   self.time_updated.emit(self.processor.get_remaining_time(elapsed))

            #    QThread.msleep(50)  # имитация обработки точки

            #self.finished.emit()
        except Exception as e:
            if self.controller.logger:
                self.controller.logger(f"Error processing electroerosion: {e}")
        finally:
            self.is_running = False
            self.finished.emit()

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def stop(self):
        with self._stop_lock:
            if self._stop_requested:
                return
            self._stop_requested = True

        self.is_running = False
        self.is_paused = False
        self.requestInterruption()
        threading.Thread(target=self._stop_controller, daemon=True).start()

    def _stop_controller(self):
        try:
            self.controller.stop_erosion()
        except Exception as exc:
            if self.controller.logger:
                self.controller.logger(f"Error stopping electroerosion: {exc}")
