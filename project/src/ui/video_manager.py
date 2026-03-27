from src.video_stream.video_stream_thread import VideoStreamThread
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap

# Video management (SRP)
class VideoManager:
    def __init__(self, video_label=None):
        self.video_thread = VideoStreamThread()
        self.video_label = video_label
        self._started = False

    def start(self):
        if self._started:
            return
        self.video_thread.new_frame.connect(self.update_frame)
        self.video_thread.start()
        self._started = True

    def stop(self):
        if not self._started:
            return
        self.video_thread.stop()
        self._started = False

    @Slot(QImage)
    def update_frame(self, image):
        if self.video_label:
            pixmap = QPixmap.fromImage(image)
            scaled = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.video_label.setPixmap(scaled)
