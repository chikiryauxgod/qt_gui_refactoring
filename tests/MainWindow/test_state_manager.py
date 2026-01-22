import pytest
from unittest.mock import MagicMock
from src.domain.state_manager import StateManager

@pytest.fixture
def state_manager():
    mock_robot = MagicMock()
    sm = StateManager(1.0, 2.0, 3.0, mock_robot)
    yield sm

def test_state_manager_sync_from_robot(state_manager):
    state_manager.robot.current_x = 10.0
    state_manager.robot.current_y = 20.0
    state_manager.robot.current_z = 30.0
    state_manager.sync_from_robot()
    assert state_manager.current_x == 10.0
    assert state_manager.current_y == 20.0
    assert state_manager.current_z == 30.0