from src.ui.theme.colors import ColorPalette


class QtStyleBuilder:
    def __init__(self, palette: ColorPalette):
        self._palette = palette

    def build(self) -> str:
        return f"""
            QMainWindow {{
                background-color: {self._palette.main_background};
            }}

            QGroupBox {{
                font-weight: bold;
                border: 2px solid {self._palette.group_border};
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """