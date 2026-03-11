from typing import Sequence


class JointAvailabilityService:
    MIN_ANGLE = -180
    MAX_ANGLE = 180

    def is_available(self, joints: Sequence[float]) -> bool:
        return all(
            self.MIN_ANGLE <= angle <= self.MAX_ANGLE
            for angle in joints
        )
