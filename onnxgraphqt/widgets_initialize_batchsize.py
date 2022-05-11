from collections import namedtuple
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from utils.opset import DEFAULT_OPSET

InitializeBatchsizeProperties = namedtuple("InitializeBatchsizeProperties",
    [
        "initialization_character_string",
    ])

class InitializeBatchsizeWidget(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 300

    def __init__(self, current_batchsize="-1", parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("initialize batchsize")
        self.initUI()
        self.updateUI(current_batchsize)

    def initUI(self):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)

        base_layout = QtWidgets.QVBoxLayout()

        # layout
        layout = QtWidgets.QVBoxLayout()
        self.lbl_name = QtWidgets.QLabel("Input string to initialize batch size.")
        self.ledit_character = QtWidgets.QLineEdit()
        self.ledit_character.setText("-1")
        self.ledit_character.setPlaceholderText("initialization_character_string")
        layout.addWidget(self.lbl_name)
        layout.addWidget(self.ledit_character)

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

    def updateUI(self, current_batchsize):
        self.ledit_character.setText(str(current_batchsize))

    def get_properties(self)->InitializeBatchsizeProperties:
        character = self.ledit_character.text().strip()
        return InitializeBatchsizeProperties(
            initialization_character_string=character
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        if props.initialization_character_string == "":
            print("ERROR: initialization_character_string")
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
    window = InitializeBatchsizeWidget()
    window.show()

    app.exec_()