from typing import List
from PySide2 import QtCore, QtWidgets, QtGui

BASE_FONT_SIZE = 16
LARGE_FONT_SIZE = 18
GRAPH_FONT_SIZE = 32

def set_font(widget: QtWidgets.QWidget, font_size:int=None, bold=False):
    f = widget.font()
    if font_size:
        f.setPixelSize(font_size)
    f.setBold(bold)
    widget.setFont(f)

def iconButton_paintEvent(button: QtWidgets.QPushButton, pixmap: QtGui.QPixmap, event: QtGui.QPaintEvent):
    QtWidgets.QPushButton.paintEvent(button, event)
    pos_x = 5 + int((30 - pixmap.width())*0.5 + 0.5)
    pos_y = (button.height() - pixmap.height()) / 2
    painter = QtGui.QPainter(button)
    painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
    painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
    painter.drawPixmap(pos_x, pos_y, pixmap)

def createIconButton(text:str, icon_path: str, icon_size:List[int]=[25, 25], font_size:int=None) -> QtWidgets.QPushButton:
    button = QtWidgets.QPushButton()
    button.setContentsMargins(QtCore.QMargins(5, 5, 5, 5))
    button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    pixmap = QtGui.QPixmap(icon_path).scaled(icon_size[0], icon_size[1], QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
    def paintEvent(button, pixmap):
        def func(event):
            return iconButton_paintEvent(button, pixmap, event)
        return func
    button.paintEvent = paintEvent(button, pixmap)
    button_layout = QtWidgets.QVBoxLayout()
    button_layout.setMargin(0)
    button.setLayout(button_layout)
    label = QtWidgets.QLabel(text=text)
    label.setMargin(0)
    label.setAlignment(QtCore.Qt.AlignRight)
    set_font(label, font_size=font_size)
    button_layout.addWidget(label)
    return button
