from src.erosion_process.erosion_process_tab import GCodeParser


def test_parse_simple_gcode(tmp_path):
    gcode = """
    G0 X0 Y0 Z0
    G1 X10 Y0 Z0
    G1 X10 Y10 Z-1
    """
    path = tmp_path / "test.gcode"
    path.write_text(gcode)

    parser = GCodeParser()
    points = parser.parse_file(str(path))

    assert points == [
    (10.0, 0.0, 0.0),
    (10.0, 10.0, -1.0),
]


def test_parse_empty_file_returns_origin(tmp_path):
    path = tmp_path / "empty.gcode"
    path.write_text("")

    parser = GCodeParser()
    points = parser.parse_file(str(path))

    assert points == [(0.0, 0.0, 0.0)]