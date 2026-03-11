from typing import Sequence


class JointControlPresenter:
    def __init__(self, controller):
        self._controller = controller

    def set_position(self, joints: Sequence[float]) -> None:
        self._controller.set_joint_pos(list(joints))
