import sys

from PySide6.QtCore import qInstallMessageHandler
from PySide6.QtWidgets import QApplication


_QT_MESSAGE_PATTERNS_TO_SUPPRESS = (
    "QPainter::begin:",
    "QPainter::end: Painter ended with",
)
_previous_qt_message_handler = None


def _qt_message_handler(mode, context, message) -> None:
    if any(message.startswith(pattern) for pattern in _QT_MESSAGE_PATTERNS_TO_SUPPRESS):
        return

    if _previous_qt_message_handler is not None:
        _previous_qt_message_handler(mode, context, message)
        return

    print(message, file=sys.stderr)


class ApplicationFactory:

    @staticmethod
    def create() -> QApplication:
        global _previous_qt_message_handler
        app = QApplication([])
        app.setStyle("Fusion")
        if _previous_qt_message_handler is None:
            _previous_qt_message_handler = qInstallMessageHandler(_qt_message_handler)
        return app
