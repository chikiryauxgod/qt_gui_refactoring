GLOBAL_QT_STYLE = """
QPushButton {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 8px 16px;
    font-size: 14px;
    margin: 4px 2px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #45a049;
}
QPushButton:pressed {
    background-color: #3d8b40;
}
QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
}
QProgressBar {
    border: 2px solid grey;
    border-radius: 5px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #4CAF50;
    width: 20px;
}
QTextEdit,
QLineEdit,
QDoubleSpinBox {
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px;
    background-color: white;
}
"""