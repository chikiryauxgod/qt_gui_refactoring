from src.integration.legacy_robot_controller_adapter import LegacyRobotControllerAdapter


def test_adapter_exposes_robot_coordinates():
    class Robot:
        current_x = 10.0
        current_y = 20.0
        current_z = 30.0

    adapter = LegacyRobotControllerAdapter(Robot())

    assert adapter.current_x == 10.0
    assert adapter.current_y == 20.0
    assert adapter.current_z == 30.0


def test_adapter_delegates_robot_commands():
    calls = []

    class Robot:
        current_x = 0.0
        current_y = 0.0
        current_z = 0.0

        def set_joint_pos(self, joints):
            calls.append(("set_joint_pos", joints))

        def set_speed(self, speed):
            calls.append(("set_speed", speed))

        def emergency_stop(self):
            calls.append(("emergency_stop", None))

    robot = Robot()
    adapter = LegacyRobotControllerAdapter(robot)

    adapter.set_coord_pos(1.0, 2.0, 3.0)
    adapter.set_joint_pos([1, 2, 3, 4, 5, 6])
    adapter.set_speed(42)
    adapter.emergency_stop()

    assert (robot.current_x, robot.current_y, robot.current_z) == (1.0, 2.0, 3.0)
    assert calls == [
        ("set_joint_pos", [1, 2, 3, 4, 5, 6]),
        ("set_speed", 42),
        ("emergency_stop", None),
    ]
