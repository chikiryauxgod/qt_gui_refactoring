class XYZAvailabilityService:
    X_MIN = -500
    X_MAX = 500
    Y_MIN = -500
    Y_MAX = 500
    Z_MIN = 0
    Z_MAX = 500

    def is_available(self, x: float, y: float, z: float) -> bool:
        return (
            self.X_MIN <= x <= self.X_MAX and
            self.Y_MIN <= y <= self.Y_MAX and
            self.Z_MIN <= z <= self.Z_MAX
        )
