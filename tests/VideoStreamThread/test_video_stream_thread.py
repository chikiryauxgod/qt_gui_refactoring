import numpy as np
import pytest

from src.VideoStream.VideoStreamThread import *
from PySide6.QtGui import QImage


class FakeSource(FrameSource):
    """1 кадр -> потом ret=False."""
    def __init__(self):
        self._opened = False
        self._read_count = 0
        self.closed = False

    def open(self) -> bool:
        self._opened = True
        return True

    def is_opened(self) -> bool:
        return self._opened and not self.closed

    def read(self):
        self._read_count += 1
        if self._read_count == 1:
            frame = np.zeros((10, 10, 3), dtype=np.uint8)
            return True, frame
        # заканчиваем поток
        self.closed = True
        return False, None

    def close(self) -> None:
        self.closed = True


class FakeConverter(FrameConverter):
    def to_qimage(self, frame_bgr: np.ndarray) -> QImage:
        h, w, ch = frame_bgr.shape
        return QImage(w, h, QImage.Format_RGB888)


def test_run_finishes_when_source_ends():
    source = FakeSource()
    converter = FakeConverter()

    t = VideoStreamThread(source=source, converter=converter, latency=1)

    # Важно: мы вызываем run() напрямую (как ты делал), без start()
    t.run()

    assert source.closed is True