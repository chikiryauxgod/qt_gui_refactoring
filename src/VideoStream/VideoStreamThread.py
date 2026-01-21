from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Tuple

import cv2
import numpy as np

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

class FrameSource(ABC):
    @abstractmethod
    def open(self) -> bool: ...
    @abstractmethod
    def is_opened(self) -> bool: ...
    @abstractmethod
    def read(self) -> Tuple[bool, Optional[np.ndarray]]: ...
    @abstractmethod
    def close(self) -> None: ...


class FrameConverter(ABC):
    @abstractmethod
    def to_qimage(self, frame_bgr: np.ndarray) -> QImage: ...


class OpenCVCameraSource(FrameSource):
    def __init__(self, camera_idx: int = 0, width: int = 640, height: int = 480):
        self._camera_idx = camera_idx
        self._width = width
        self._height = height
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        self._cap = cv2.VideoCapture(self._camera_idx)
        if not self._cap or not self._cap.isOpened():
            self._cap = None
            return False

        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        return True

    def is_opened(self) -> bool:
        return bool(self._cap and self._cap.isOpened())

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if not self.is_opened():
            return False, None
        ret, frame = self._cap.read()
        return ret, frame if ret else None

    def close(self) -> None:
        if self._cap and self._cap.isOpened():
            self._cap.release()
        self._cap = None


class BGRToRGB888QImageConverter(FrameConverter):
    def to_qimage(self, frame_bgr: np.ndarray) -> QImage:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        return QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()

class VideoStreamThread(QThread):
    new_frame = Signal(QImage)
    error = Signal(str)

    def __init__(
        self,
        source: Optional[FrameSource] = None,
        converter: Optional[FrameConverter] = None,
        latency: int = 30,
    ):
        super().__init__()
        self._source = source or OpenCVCameraSource(camera_idx=0, width=640, height=480)
        self._converter = converter or BGRToRGB888QImageConverter()
        self._latency = latency
        self._running = True

    def run(self):
        if not self._source.open():
            self.error.emit("Не удалось открыть видеопоток (источник не открылся).")
            return

        try:
            while self._running:
                if not self._source.is_opened():
                    self.error.emit("Видеопоток недоступен (источник закрылся).")
                    break

                ret, frame = self._source.read()
                if not ret or frame is None:
                    self.error.emit("Ошибка чтения кадра (ret=False).")
                    break

                qt_image = self._converter.to_qimage(frame)
                self.new_frame.emit(qt_image)

                self.msleep(self._latency)
        finally:
            self._source.close()

    def stop(self):
        self._running = False
        self.wait()