from dataclasses import dataclass
from typing import List


@dataclass
class AxisControlConfig:
    """
    Configuration for axis control widget.
    
    Attributes:
        step_sizes: List of step sizes for movement buttons
        button_width: Width of control buttons
        button_height: Height of control buttons
        font_size: Font size for buttons
        initial_value: Initial position value
    """
    
    step_sizes: List[float] = None
    button_width: int = 60
    button_height: int = 50
    font_size: int = 10
    initial_value: float = 0.0
    
    def __post_init__(self):
        if self.step_sizes is None:
            self.step_sizes = [0.1, 1.0, 10.0]
    
    def validate(self) -> bool:
        if not self.step_sizes:
            raise ValueError("step_sizes cannot be empty")
        
        if any(step <= 0 for step in self.step_sizes):
            raise ValueError("All step sizes must be positive")
        
        if self.button_width <= 0 or self.button_height <= 0:
            raise ValueError("Button dimensions must be positive")
        
        if self.font_size <= 0:
            raise ValueError("Font size must be positive")
        
        return True