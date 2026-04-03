from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QDoubleSpinBox, QGroupBox, QMessageBox, QPushButton, QTabWidget

from src.services.service_tab import ServiceTab
from tests.physical_gui_helpers import find_button, open_tab_by_text, physical_click, require_x11_environment


pytestmark = pytest.mark.physical_gui


def _make_controller():
    state = SimpleNamespace(
        current_x=10.0,
        current_y=20.0,
        current_z=30.0,
        current_joints=[0.0, 10.0, 20.0, 30.0, 40.0, 50.0],
    )

    controller = Mock()
    controller.state = state
    controller.X0 = 0.0
    controller.Y0 = 0.0
    controller.Z0 = 0.0

    def set_coord_pos(x, y, z):
        state.current_x = x
        state.current_y = y
        state.current_z = z

    def set_joint_pos(joints):
        state.current_joints = list(joints)

    controller.set_coord_pos.side_effect = set_coord_pos
    controller.set_joint_pos.side_effect = set_joint_pos
    controller.set_erosion = Mock()
    controller.set_water = Mock()
    controller.pump_control_one = Mock()
    controller.pump_control_two = Mock()
    controller.set_speed_w = Mock()
    return controller


def _find_group(widget, title):
    for group in widget.findChildren(QGroupBox):
        if group.title() == title:
            return group
    raise AssertionError(f"Group with title {title!r} not found")


@pytest.fixture
def shown_tab(qtbot, monkeypatch):
    require_x11_environment()
    monkeypatch.setattr(ServiceTab, "create_robot_chain", lambda self: None)

    controller = _make_controller()
    tab = ServiceTab(controller)
    qtbot.addWidget(tab)
    tab.resize(1400, 900)
    tab.show()
    tab.raise_()
    tab.activateWindow()
    qtbot.waitUntil(lambda: tab.isVisible())
    qtbot.wait(300)
    return tab, controller


def test_xyz_tab_buttons_are_clicked_physically(shown_tab, qtbot):
    tab, controller = shown_tab
    tabs = tab.findChild(QTabWidget)
    xyz_tab = open_tab_by_text(qtbot, tabs, "Управление по осям XYZ")

    expected_calls = 0
    for axis, current_value in (("X", 10.0), ("Y", 20.0), ("Z", 30.0)):
        group = _find_group(xyz_tab, f"Ось {axis}")
        spinbox = group.findChild(QDoubleSpinBox)
        buttons = group.findChildren(QPushButton)
        set_button = next(button for button in buttons if button.text() == "Установить XYZ")
        step_buttons = [button for button in buttons if button.text() != "Установить XYZ"]

        spinbox.setValue(current_value + 5.0)
        physical_click(qtbot, set_button)
        expected_calls += 1

        for button in step_buttons:
            physical_click(qtbot, button)
            expected_calls += 1

    physical_click(qtbot, find_button(xyz_tab, "Вернуться в нулевое положение"))
    expected_calls += 1
    physical_click(qtbot, find_button(xyz_tab, "Обновить визуализацию"))

    assert controller.set_coord_pos.call_count == expected_calls
    assert controller.set_coord_pos.call_args_list[-1].args == (0.0, 0.0, 0.0)


def test_joints_tab_buttons_are_clicked_physically(shown_tab, qtbot):
    tab, controller = shown_tab
    tabs = tab.findChild(QTabWidget)
    joints_tab = open_tab_by_text(qtbot, tabs, "Управление по суставам")

    expected_calls = 0
    for index in range(6):
        group = _find_group(joints_tab, f"Сустав J{index}")
        spinbox = group.findChild(QDoubleSpinBox)
        buttons = group.findChildren(QPushButton)
        set_button = next(button for button in buttons if button.text() == "Установить")
        move_buttons = [button for button in buttons if button.text() != "Установить"]

        spinbox.setValue(index * 10 + 1.5)
        physical_click(qtbot, set_button)
        expected_calls += 1

        for button in move_buttons:
            physical_click(qtbot, button)
            expected_calls += 1

    physical_click(qtbot, find_button(joints_tab, "Вернуться в нулевое положение"))
    expected_calls += 1
    physical_click(qtbot, find_button(joints_tab, "Обновить визуализацию"))

    assert controller.set_joint_pos.call_count == expected_calls
    assert controller.set_joint_pos.call_args_list[-1].args[0] == [0, 0, 0, 0, 0, 0]


def test_erosion_controls_buttons_are_clicked_physically(shown_tab, qtbot):
    tab, controller = shown_tab
    tabs = tab.findChild(QTabWidget)
    controls_tab = open_tab_by_text(qtbot, tabs, "Управление эрозией и водой")

    physical_click(qtbot, find_button(controls_tab, "Включить эрозию"))
    physical_click(qtbot, find_button(controls_tab, "Выключить эрозию"))
    physical_click(qtbot, find_button(controls_tab, "Включение циркуляции воды"))
    physical_click(qtbot, find_button(controls_tab, "Отключение циркуляции воды"))
    physical_click(qtbot, find_button(controls_tab, "Включить/выключить накачивание воды"))
    physical_click(qtbot, find_button(controls_tab, "Включить/выключить откачивание воды"))
    physical_click(qtbot, find_button(controls_tab, "Обновить статус"))

    controller.set_erosion.assert_any_call(True)
    controller.set_erosion.assert_any_call(False)
    controller.set_water.assert_any_call(True)
    controller.set_water.assert_any_call(False)
    controller.pump_control_one.assert_called_once()
    controller.pump_control_two.assert_called_once()
    assert "Текущий статус системы" in tab.status_text.toPlainText()


def test_xyz_trajectory_buttons_are_clicked_physically(shown_tab, qtbot, monkeypatch):
    tab, controller = shown_tab
    tabs = tab.findChild(QTabWidget)
    trajectory_tab = open_tab_by_text(qtbot, tabs, "Траектория по XYZ")
    critical = Mock()
    monkeypatch.setattr(QMessageBox, "critical", critical)

    tab.new_x.setValue(12.0)
    tab.new_y.setValue(22.0)
    tab.new_z.setValue(32.0)
    initial_count = tab.xyz_listbox.count()

    physical_click(qtbot, find_button(trajectory_tab, "Добавить точку"))
    qtbot.waitUntil(lambda: tab.xyz_listbox.count() == initial_count + 1)

    tab.xyz_listbox.setCurrentRow(tab.xyz_listbox.count() - 1)
    physical_click(qtbot, find_button(trajectory_tab, "Удалить точку"))
    qtbot.waitUntil(lambda: tab.xyz_listbox.count() == initial_count)

    physical_click(qtbot, find_button(trajectory_tab, "Вернуться в ноль"))
    assert controller.set_coord_pos.call_args_list[-1].args == (0.0, 0.0, 0.0)

    physical_click(qtbot, find_button(trajectory_tab, "Очистить все"))
    qtbot.waitUntil(lambda: tab.xyz_listbox.count() == 0)

    physical_click(qtbot, find_button(trajectory_tab, "Выполнить траекторию"))
    qtbot.waitUntil(lambda: critical.called)
    assert critical.call_args.args[1:] == ("Ошибка", "Траектория не задана")


def test_joints_trajectory_buttons_are_clicked_physically(shown_tab, qtbot, monkeypatch):
    tab, controller = shown_tab
    tabs = tab.findChild(QTabWidget)
    trajectory_tab = open_tab_by_text(qtbot, tabs, "Траектория по суставам")
    critical = Mock()
    monkeypatch.setattr(QMessageBox, "critical", critical)

    for index in range(6):
        tab.new_joints[f"J{index}"].setValue(index + 0.5)

    physical_click(qtbot, find_button(trajectory_tab, "Добавить позицию"))
    qtbot.waitUntil(lambda: tab.joints_listbox.count() == 1)

    tab.joints_listbox.setCurrentRow(0)
    physical_click(qtbot, find_button(trajectory_tab, "Удалить позицию"))
    qtbot.waitUntil(lambda: tab.joints_listbox.count() == 0)

    physical_click(qtbot, find_button(trajectory_tab, "Вернуться в ноль"))
    assert controller.set_joint_pos.call_args_list[-1].args[0] == [0, 0, 0, 0, 0, 0]

    physical_click(qtbot, find_button(trajectory_tab, "Очистить все"))
    assert tab.joints_listbox.count() == 0

    physical_click(qtbot, find_button(trajectory_tab, "Выполнить траекторию"))
    qtbot.waitUntil(lambda: critical.called)
    assert critical.call_args.args[1:] == ("Ошибка", "Траектория не задана")


def test_robot_settings_button_is_clicked_physically(shown_tab, qtbot):
    tab, controller = shown_tab
    tabs = tab.findChild(QTabWidget)
    settings_tab = open_tab_by_text(qtbot, tabs, "Параметры робота")

    tab.speed_input.setValue(42.0)
    physical_click(qtbot, find_button(settings_tab, "Задать"))

    controller.set_speed_w.assert_called_once_with(42.0)
    assert tab.current_speed_label.text() == "42.0 %"
