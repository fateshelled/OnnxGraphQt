from PySide2 import QtCore, QtWidgets, QtGui

def setFont(label: QtWidgets.QLabel, font_size:int=None, bold=False):
    f = label.font()
    if font_size:
        f.setPixelSize(font_size)
    f.setBold(bold)
    label.setFont(f)
