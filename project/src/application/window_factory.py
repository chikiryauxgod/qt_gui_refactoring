from src.ui.main_window import MainWindow
from src.ui.theme.style_builder import QtStyleBuilder


class WindowFactory:

    @staticmethod
    def create_main_window(style_builder: QtStyleBuilder) -> MainWindow:
        window = MainWindow(style_builder)
        window.showMaximized()
        return window