import queue
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QFileDialog, QMessageBox

from src.erosion_process.erosion_process_tab import ErosionProcessTab
from tests.physical_gui_helpers import find_button, physical_click, require_x11_environment


pytestmark = pytest.mark.physical_gui


def _make_controller():
    controller = Mock()
    controller.state = SimpleNamespace(current_x=1.0, current_y=2.0, current_z=3.0)
    controller.set_coord_pos = Mock()
    controller.start_erosion_process = Mock()
    controller.stop_erosion_process = Mock()
    controller.X0 = 0.0
    controller.Y0 = 0.0
    controller.Z0 = 0.0
    return controller
@pytest.fixture
def shown_tab(qtbot):
    require_x11_environment()
    controller = _make_controller()
    tab = ErosionProcessTab(controller, queue.Queue())
    qtbot.addWidget(tab)
    tab.resize(1340, 720)
    tab.show()
    tab.raise_()
    tab.activateWindow()
    qtbot.waitUntil(lambda: tab.isVisible())
    qtbot.wait(250)
    return tab, controller


def test_next_and_prev_buttons_are_clicked_physically(shown_tab, qtbot):
    tab, _controller = shown_tab

    assert tab.current_step == 0

    physical_click(qtbot, tab.next_btn)
    qtbot.waitUntil(lambda: tab.current_step == 1)

    physical_click(qtbot, tab.prev_btn)
    qtbot.waitUntil(lambda: tab.current_step == 0)


def test_start_button_is_clicked_physically_and_shows_error(shown_tab, qtbot, monkeypatch):
    tab, controller = shown_tab
    critical = Mock()
    monkeypatch.setattr(QMessageBox, "critical", critical)

    physical_click(qtbot, tab.next_btn)
    qtbot.waitUntil(lambda: tab.current_step == 1)
    physical_click(qtbot, tab.next_btn)
    qtbot.waitUntil(lambda: tab.current_step == 2)
    physical_click(qtbot, tab.next_btn)
    qtbot.waitUntil(lambda: tab.current_step == 3)

    physical_click(qtbot, tab.start_btn)
    qtbot.waitUntil(lambda: critical.called)

    controller.start_erosion_process.assert_not_called()
    assert critical.call_args.args[1:] == ("Ошибка", "Сначала загрузите G-code файл")


def test_return_to_zero_button_is_clicked_physically(shown_tab, qtbot):
    tab, controller = shown_tab

    physical_click(qtbot, tab.next_btn)
    qtbot.waitUntil(lambda: tab.current_step == 1)

    reset_button = find_button(tab.stacked_widget.currentWidget(), "Вернуться в нулевое положение")
    physical_click(qtbot, reset_button)

    controller.set_coord_pos.assert_called_once_with(0.0, 0.0, 0.0)


def test_stop_button_is_clicked_physically(shown_tab, qtbot):
    tab, controller = shown_tab

    physical_click(qtbot, tab.next_btn)
    qtbot.waitUntil(lambda: tab.current_step == 1)
    physical_click(qtbot, tab.next_btn)
    qtbot.waitUntil(lambda: tab.current_step == 2)
    physical_click(qtbot, tab.next_btn)
    qtbot.waitUntil(lambda: tab.current_step == 3)

    tab.set_started_ui_state()
    tab.progress_bar.setValue(64)
    tab.time_label.setText("Осталось: 00:21")

    physical_click(qtbot, tab.stop_btn)

    controller.stop_erosion_process.assert_called_once()
    assert tab.start_btn.isEnabled()
    assert not tab.pause_btn.isEnabled()
    assert tab.progress_bar.value() == 0
    assert tab.time_label.text() == "Остановлено"


def test_browse_button_is_clicked_physically_and_loads_gcode(shown_tab, qtbot, tmp_path, monkeypatch):
    tab, _controller = shown_tab
    gcode_file = tmp_path / "path.gcode"
    gcode_file.write_text("G1 X1 Y2 Z3\nG1 X2 Y3 Z4\n", encoding="utf-8")

    monkeypatch.setattr(QFileDialog, "getOpenFileName", Mock(return_value=(str(gcode_file), "")))

    browse_button = find_button(tab.stacked_widget.currentWidget(), "Обзор")
    physical_click(qtbot, browse_button)

    qtbot.waitUntil(lambda: tab.gcode_file_edit.text() == str(gcode_file))
    assert "Количество точек: 2" in tab.gcode_info_text.toPlainText()


def test_axis_buttons_are_clicked_physically(shown_tab, qtbot):
    tab, controller = shown_tab

    physical_click(qtbot, tab.next_btn)
    qtbot.waitUntil(lambda: tab.current_step == 1)

    expected_calls = 0
    for control, initial in (
        (tab.x_control, 1.0),
        (tab.y_control, 2.0),
        (tab.z_control, 3.0),
    ):
        buttons = [button for button in control.findChildren(type(tab.next_btn)) if button.isEnabled()]
        for button in buttons:
            physical_click(qtbot, button)
            expected_calls += 1

        expected_value = initial
        for button in buttons:
            text = button.text()
            step = float(text[1:])
            expected_value += step if text.startswith("+") else -step

        assert control.value_label.text() == f"{expected_value:.1f} мм"

    assert controller.set_coord_pos.call_count == expected_calls


def test_pause_and_change_tool_buttons_are_clicked_physically(shown_tab, qtbot, monkeypatch):
    tab, _controller = shown_tab
    worker = Mock()
    worker.isRunning.return_value = True
    tab.set_erosion_worker(worker)

    information = Mock()
    monkeypatch.setattr(QMessageBox, "information", information)

    physical_click(qtbot, tab.next_btn)
    qtbot.waitUntil(lambda: tab.current_step == 1)
    physical_click(qtbot, tab.next_btn)
    qtbot.waitUntil(lambda: tab.current_step == 2)
    physical_click(qtbot, tab.next_btn)
    qtbot.waitUntil(lambda: tab.current_step == 3)

    tab.set_started_ui_state()

    physical_click(qtbot, tab.pause_btn)
    qtbot.waitUntil(lambda: tab.is_process_paused is True)
    assert tab.pause_btn.text() == "▶ Продолжить"

    physical_click(qtbot, tab.pause_btn)
    qtbot.waitUntil(lambda: tab.is_process_paused is False)
    assert tab.pause_btn.text() == "⏸ Пауза"

    physical_click(qtbot, tab.changetool)
    qtbot.waitUntil(lambda: information.called)
    assert tab.is_process_paused is True
    assert worker.pause.call_count >= 2
