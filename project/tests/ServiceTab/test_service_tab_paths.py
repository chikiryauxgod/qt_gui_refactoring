from unittest.mock import Mock

from src.services import service_tab
from src.services.service_tab import ServiceTab


def test_create_robot_chain_uses_module_relative_urdf_path(monkeypatch):
    monkeypatch.setattr(service_tab.Chain, "from_urdf_file", Mock(return_value="robot-chain"))

    tab = ServiceTab.__new__(ServiceTab)
    robot_chain = ServiceTab.create_robot_chain(tab)

    service_tab.Chain.from_urdf_file.assert_called_once_with(
        str(service_tab.URDF_PATH),
        active_links_mask=[False, True, True, True, True, True, True, False],
    )
    assert robot_chain == "robot-chain"
    assert service_tab.URDF_PATH.is_absolute()
    assert service_tab.URDF_PATH.name == "robot_6_axis.urdf"
