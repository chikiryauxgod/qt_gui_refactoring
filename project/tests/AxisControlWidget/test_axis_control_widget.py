import pytest
from pytestqt.qtbot import QtBot
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from src.widgets.axis_control_widget import AxisControlWidget
from src.widgets.axis_control_config import AxisControlConfig


class TestAxisControlWidget:
    """Test cases for AxisControlWidget."""
    
    def test_initialization_default_config(self, qtbot: QtBot):
        """Test widget initialization with default config."""
        widget = AxisControlWidget('X')
        qtbot.addWidget(widget)
        
        assert widget.axis == 'X'
        assert widget.get_current_value() == 0.0
        assert widget.value_label.text() == "0.0 мм"
    
    def test_initialization_custom_config(self, qtbot: QtBot):
        """Test widget initialization with custom config."""
        config = AxisControlConfig(
            step_sizes=[0.5, 2.0],
            initial_value=50.0
        )
        widget = AxisControlWidget('Y', config)
        qtbot.addWidget(widget)
        
        assert widget.axis == 'Y'
        assert widget.get_current_value() == 50.0
        assert widget.config.step_sizes == [0.5, 2.0]
    
    def test_change_position_positive(self, qtbot: QtBot):
        """Test position change with positive delta."""
        widget = AxisControlWidget('Z')
        qtbot.addWidget(widget)
        
        with qtbot.waitSignal(widget.position_changed, timeout=1000) as blocker:
            widget.change_position(10.0)
        
        assert widget.get_current_value() == 10.0
        assert blocker.args == ['Z', 10.0]
        assert widget.value_label.text() == "10.0 мм"
    
    def test_change_position_negative(self, qtbot: QtBot):
        """Test position change with negative delta."""
        widget = AxisControlWidget('X')
        qtbot.addWidget(widget)
        
        widget.set_current_value(20.0)
        
        with qtbot.waitSignal(widget.position_changed, timeout=1000) as blocker:
            widget.change_position(-5.0)
        
        assert widget.get_current_value() == 15.0
        assert blocker.args == ['X', 15.0]
    
    def test_change_position_multiple_times(self, qtbot: QtBot):
        """Test multiple position changes."""
        widget = AxisControlWidget('Y')
        qtbot.addWidget(widget)
        
        widget.change_position(1.0)
        widget.change_position(2.0)
        widget.change_position(-0.5)
        
        assert widget.get_current_value() == 2.5
    
    def test_set_current_value(self, qtbot: QtBot):
        """Test setting current value directly."""
        widget = AxisControlWidget('Z')
        qtbot.addWidget(widget)
        
        widget.set_current_value(123.45)
        
        assert widget.get_current_value() == 123.45
        assert widget.value_label.text() == "123.5 мм"  
    
    def test_button_click_increment(self, qtbot: QtBot):
        """Test increment button click."""
        config = AxisControlConfig(step_sizes=[1.0])
        widget = AxisControlWidget('X', config)
        qtbot.addWidget(widget)
    
        buttons = widget.findChildren(QPushButton)
        plus_button = [b for b in buttons if b.text() == "+1.0"][0]
        
        with qtbot.waitSignal(widget.position_changed, timeout=1000):
            qtbot.mouseClick(plus_button, Qt.LeftButton)
        
        assert widget.get_current_value() == 1.0
    
    def test_button_click_decrement(self, qtbot: QtBot):
        """Test decrement button click."""
        config = AxisControlConfig(step_sizes=[0.1], initial_value=5.0)
        widget = AxisControlWidget('Y', config)
        qtbot.addWidget(widget)
        
        buttons = widget.findChildren(QPushButton)
        minus_button = [b for b in buttons if b.text() == "-0.1"][0]
        
        with qtbot.waitSignal(widget.position_changed, timeout=1000):
            qtbot.mouseClick(minus_button, Qt.LeftButton)
        
        assert widget.get_current_value() == 4.9
    
    def test_invalid_config_raises_error(self, qtbot: QtBot):
        """Test that invalid config raises error."""
        config = AxisControlConfig(step_sizes=[])
        
        with pytest.raises(ValueError):
            widget = AxisControlWidget('X', config)