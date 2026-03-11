from PySide6.QtWidgets import QApplication

from src.ui.theme.colors import LIGHT_PALETTE
from src.ui.theme.style_builder import QtStyleBuilder
from src.ui.theme.global_style import GLOBAL_QT_STYLE


class StyleConfigurator:

    def configure(self, app: QApplication) -> QtStyleBuilder:
        app.setStyleSheet(GLOBAL_QT_STYLE)

        palette = LIGHT_PALETTE
        style_builder = QtStyleBuilder(palette)

        return style_builder