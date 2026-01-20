import pytest
from src.widgets.axis_control_config import AxisControlConfig

class TestAxisControlConfig:
    
    def test_default_initialization(self):
        """Test default configuration values."""
        config = AxisControlConfig()
        
        assert config.step_sizes == [0.1, 1.0, 10.0]
        assert config.button_width == 60
        assert config.button_height == 50
        assert config.font_size == 10
        assert config.initial_value == 0.0
    
    def test_custom_initialization(self):
        """Test custom configuration values."""
        config = AxisControlConfig(
            step_sizes=[0.5, 2.0, 5.0],
            button_width=80,
            button_height=60,
            font_size=12,
            initial_value=100.0
        )
        
        assert config.step_sizes == [0.5, 2.0, 5.0]
        assert config.button_width == 80
        assert config.button_height == 60
        assert config.font_size == 12
        assert config.initial_value == 100.0
    
    def test_validate_valid_config(self):
        """Test validation with valid configuration."""
        config = AxisControlConfig()
        assert config.validate() is True
    
    def test_validate_empty_step_sizes(self):
        """Test validation fails with empty step sizes."""
        config = AxisControlConfig(step_sizes=[])
        
        with pytest.raises(ValueError, match="step_sizes cannot be empty"):
            config.validate()
    
    def test_validate_negative_step_size(self):
        """Test validation fails with negative step size."""
        config = AxisControlConfig(step_sizes=[0.1, -1.0, 10.0])
        
        with pytest.raises(ValueError, match="All step sizes must be positive"):
            config.validate()
    
    def test_validate_zero_step_size(self):
        """Test validation fails with zero step size."""
        config = AxisControlConfig(step_sizes=[0.1, 0.0, 10.0])
        
        with pytest.raises(ValueError, match="All step sizes must be positive"):
            config.validate()
    
    def test_validate_negative_button_width(self):
        """Test validation fails with negative button width."""
        config = AxisControlConfig(button_width=-60)
        
        with pytest.raises(ValueError, match="Button dimensions must be positive"):
            config.validate()
    
    def test_validate_zero_button_height(self):
        """Test validation fails with zero button height."""
        config = AxisControlConfig(button_height=0)
        
        with pytest.raises(ValueError, match="Button dimensions must be positive"):
            config.validate()
    
    def test_validate_negative_font_size(self):
        """Test validation fails with negative font size."""
        config = AxisControlConfig(font_size=-10)
        
        with pytest.raises(ValueError, match="Font size must be positive"):
            config.validate()