from PySide6.QtWidgets import QApplication


class ApplicationFactory:

    @staticmethod
    def create() -> QApplication:
        app = QApplication([])
        app.setStyle("Fusion")
        return app