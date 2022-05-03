from PySide2 import QtCore, QtWidgets, QtGui

class MessageBox(QtWidgets.QMessageBox):
    def __init__(self,
                 text:str,
                 title:str,
                 default_button=QtWidgets.QMessageBox.Ok,
                 icon=QtWidgets.QMessageBox.Icon.Information,
                 parent=None) -> int:
        super().__init__(parent)
        self.setText(text)
        self.setWindowTitle(title)
        self.setDefaultButton(default_button)
        self.setIcon(icon)
        self.exec_()
        return