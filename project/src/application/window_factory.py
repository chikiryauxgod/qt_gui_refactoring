from src.ui.main_window import MainWindow
from src.ui.theme.style_builder import QtStyleBuilder


class WindowFactory:

    @staticmethod
    def create_main_window(style_builder: QtStyleBuilder, hardware_controller=None, q_ref=None) -> MainWindow:
        window = MainWindow(style_builder, hardware_controller=hardware_controller, q_ref=q_ref)
        window.showMaximized()
        return window
