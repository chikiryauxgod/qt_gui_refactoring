from __future__ import annotations

from src.ports.robot_controller_port import RobotControllerPort


class LegacyRobotControllerAdapter(RobotControllerPort):
    def __init__(self, robot):
        self._robot = robot

    @property
    def current_x(self) -> float:
        return self._robot.current_x

    @property
    def current_y(self) -> float:
        return self._robot.current_y

    @property
    def current_z(self) -> float:
        return self._robot.current_z

    def set_coord_pos(self, x: float, y: float, z: float) -> None:
        self._robot.current_x = x
        self._robot.current_y = y
        self._robot.current_z = z

    def set_joint_pos(self, joints: list[float]) -> None:
        self._robot.set_joint_pos(joints)

    def set_speed(self, v: int) -> None:
        self._robot.set_speed(v)

    def emergency_stop(self) -> None:
        self._robot.emergency_stop()
