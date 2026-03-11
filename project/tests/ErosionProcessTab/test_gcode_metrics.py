from src.erosion_process.erosion_process_tab import GCodeMetrics


def test_path_length():
    points = [
        (0, 0, 0),
        (3, 4, 0),  # 5
        (3, 4, 12), # 12
    ]
    length = GCodeMetrics.path_length(points)
    assert length == 17.0


def test_ranges():
    points = [
        (-1, 2, 3),
        (4, -2, 10),
        (0, 0, -1),
    ]

    xr, yr, zr = GCodeMetrics.ranges(points)

    assert xr == (-1, 4)
    assert yr == (-2, 2)
    assert zr == (-1, 10)