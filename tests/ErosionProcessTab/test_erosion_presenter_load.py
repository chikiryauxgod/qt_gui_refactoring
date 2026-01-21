from src.erosion_process.erosion_process_tab import ErosionProcessPresenter
import pytest


def test_load_gcode_success(tmp_path, fake_view, fake_controller, q_ref):
    gcode = "G1 X1 Y2 Z3"
    path = tmp_path / "ok.gcode"
    path.write_text(gcode)

    presenter = ErosionProcessPresenter(fake_controller, fake_view, q_ref)
    presenter.load_gcode(str(path))

    fake_view.set_gcode_info.assert_called_once()
    fake_view.plot_gcode.assert_called_once()

    points = fake_view.plot_gcode.call_args.args[0]
    assert points == [(1.0, 2.0, 3.0)]


def test_load_gcode_wrong_extension(fake_view, fake_controller, q_ref):
    presenter = ErosionProcessPresenter(fake_controller, fake_view, q_ref)
    presenter.load_gcode("file.txt")

    fake_view.show_error.assert_called_once()


def test_load_gcode_missing_file(fake_view, fake_controller, q_ref):
    presenter = ErosionProcessPresenter(fake_controller, fake_view, q_ref)
    presenter.load_gcode("missing.gcode")

    fake_view.show_error.assert_called_once()
