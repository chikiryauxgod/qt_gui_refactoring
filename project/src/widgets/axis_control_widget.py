from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
from PySide6.QtCore import Qt, Signal

from .axis_control_config import AxisControlConfig


class AxisControlWidget(QWidget):
    """
    Widget for controlling single axis movement.
    
    Provides buttons for incremental movement with configurable step sizes.
    Emits signal when position changes.
    
    Signals:
        position_changed: Emitted with (axis_name, new_position)
    """
    
    position_changed = Signal(str, float)
    
    def __init__(self, axis: str, config: AxisControlConfig = None):
        """
        Initialize axis control widget.
        
        Args:
            axis: Axis identifier (e.g., 'X', 'Y', 'Z')
            config: Configuration object. If None, uses default config.
        """
        super().__init__()
        self.axis = axis
        self.config = config if config is not None else AxisControlConfig()
        self.config.validate()
        
        self._current_value = self.config.initial_value
        self._create_widgets()
        
    def _create_widgets(self):
        """Create and layout UI widgets."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        title_label = QLabel(f"Ось {self.axis}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        self.value_label = QLabel(f"{self._current_value:.1f} мм")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet(
            "font-size: 12px; background-color: #f0f0f0; "
            "padding: 3px; border-radius: 3px;"
        )
        layout.addWidget(self.value_label)
        
        layout.addSpacing(5)
        
        button_layout = self._create_button_layout()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def _create_button_layout(self) -> QGridLayout:
        button_layout = QGridLayout()
        button_layout.setHorizontalSpacing(3)
        button_layout.setVerticalSpacing(3)
        
        for i, step in enumerate(self.config.step_sizes):
            minus_btn = self._create_button(f"-{step}", step, decrement=True)
            button_layout.addWidget(minus_btn, 0, i)
            
            step_label = QLabel(f"{step} мм")
            step_label.setAlignment(Qt.AlignCenter)
            step_label.setStyleSheet(f"font-size: {self.config.font_size}px;")
            button_layout.addWidget(step_label, 1, i)
            
            plus_btn = self._create_button(f"+{step}", step, decrement=False)
            button_layout.addWidget(plus_btn, 2, i)
        
        return button_layout
    
    def _create_button(self, text: str, step: float, decrement: bool) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(self.config.button_width, self.config.button_height)
        button.setStyleSheet(f"font-size: {self.config.font_size}px;")
        
        delta = -step if decrement else step
        button.clicked.connect(lambda: self.change_position(delta))
        
        return button
        
    def change_position(self, delta: float):
        self._current_value += delta
        self.value_label.setText(f"{self._current_value:.1f} мм")
        self.position_changed.emit(self.axis, self._current_value)
    
    def get_current_value(self) -> float:
        return self._current_value
    
    def set_current_value(self, value: float):
        self._current_value = value
        self.value_label.setText(f"{self._current_value:.1f} мм")