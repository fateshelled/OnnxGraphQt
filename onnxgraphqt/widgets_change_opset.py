from collections import namedtuple
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from utils.opset import DEFAULT_OPSET

ChangeOpsetProperties = namedtuple("ChangeOpsetProperties",
    [
        "opset",
    ])

class ChangeOpsetWidget(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 300

    def __init__(self, current_opset, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("change opset")
        self.current_opset = current_opset
        self.initUI()

    def initUI(self):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)

        base_layout = QtWidgets.QVBoxLayout()
        base_layout.setSizeConstraint(base_layout.SizeConstraint.SetFixedSize)

        # Form layout
        layout = QtWidgets.QFormLayout()
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        self.ledit_opset = QtWidgets.QLineEdit()
        self.ledit_opset.setText(str(self.current_opset))
        self.ledit_opset.setPlaceholderText("opset")

        layout.addRow("opset number to be changed", self.ledit_opset)

        # add layout
        base_layout.addLayout(layout)

        # Dialog button
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        # layout.addWidget(btn)
        base_layout.addWidget(btn)

        self.setLayout(base_layout)

    def get_properties(self)->ChangeOpsetProperties:
        return ChangeOpsetProperties(
            opset=self.ledit_opset.text()
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        if not str(props.opset).isdecimal():
            print("ERROR: opset")
            invalid = True
        if invalid:
            return
        return super().accept()


if __name__ == "__main__":
    import signal
    import os
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])
    window = ChangeOpsetWidget(current_opset=DEFAULT_OPSET)
    window.show()

    app.exec_()