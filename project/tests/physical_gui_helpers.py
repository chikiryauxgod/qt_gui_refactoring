import os
import shutil
import subprocess

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QPushButton, QTabWidget, QWidget


def require_x11_environment():
    if shutil.which("xdotool") is None:
        pytest.skip("xdotool is not installed")
    display = os.environ.get("DISPLAY")
    if not display:
        pytest.skip("DISPLAY is not set")
    return {**os.environ, "DISPLAY": display}


def run_xdotool(*args):
    env = require_x11_environment()
    subprocess.run(
        ["xdotool", *map(str, args)],
        check=True,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def physical_click(qtbot, widget: QWidget):
    window_id = int(widget.window().winId())
    center = widget.rect().center()
    global_center: QPoint = widget.mapToGlobal(center)

    run_xdotool("windowactivate", "--sync", window_id)
    qtbot.wait(150)
    run_xdotool("mousemove", global_center.x(), global_center.y())
    qtbot.wait(100)
    run_xdotool("click", "1")
    qtbot.wait(200)
    QApplication.processEvents()


def find_button(widget: QWidget, text: str) -> QPushButton:
    for button in widget.findChildren(QPushButton):
        if button.text() == text:
            return button
    raise AssertionError(f"Button with text {text!r} not found")


def open_tab_by_text(qtbot, tab_widget: QTabWidget, label: str):
    for index in range(tab_widget.count()):
        if tab_widget.tabText(index) == label:
            tab_bar = tab_widget.tabBar()
            rect = tab_bar.tabRect(index)
            global_center = tab_bar.mapToGlobal(rect.center())
            run_xdotool("windowactivate", "--sync", int(tab_widget.window().winId()))
            qtbot.wait(150)
            run_xdotool("mousemove", global_center.x(), global_center.y())
            qtbot.wait(100)
            run_xdotool("click", "1")
            qtbot.waitUntil(lambda: tab_widget.currentIndex() == index)
            return tab_widget.widget(index)
    raise AssertionError(f"Tab with text {label!r} not found")
