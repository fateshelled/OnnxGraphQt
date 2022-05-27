from collections import namedtuple
import signal
from PySide2 import QtCore, QtWidgets, QtGui

RenameOpProperties = namedtuple("RenameOpProperties",
    [
        "old_new",
    ])

class RenameOpWidget(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 350

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("rename op")
        self.initUI()

    def initUI(self):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)

        base_layout = QtWidgets.QVBoxLayout()
        base_layout.setSizeConstraint(base_layout.SizeConstraint.SetFixedSize)

        # layout
        layout = QtWidgets.QVBoxLayout()
        self.lbl_name = QtWidgets.QLabel("Replace substring 'old' in opname with 'new'.")
        layout.addWidget(self.lbl_name)

        layout_ledit = QtWidgets.QHBoxLayout()
        self.ledit_old = QtWidgets.QLineEdit()
        self.ledit_old.setPlaceholderText('old. e.g. "onnx::"')
        self.ledit_new = QtWidgets.QLineEdit()
        self.ledit_new.setPlaceholderText('new. e.g. "" ')
        layout_ledit.addWidget(self.ledit_old)
        layout_ledit.addWidget(self.ledit_new)

        # add layout
        base_layout.addLayout(layout)
        base_layout.addLayout(layout_ledit)

        # Dialog button
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        # layout.addWidget(btn)
        base_layout.addWidget(btn)

        self.setLayout(base_layout)

    def get_properties(self)->RenameOpProperties:
        old = self.ledit_old.text().strip()
        new = self.ledit_new.text().strip()
        return RenameOpProperties(
            old_new=[old, new]
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        if props.old_new[0] == "":
            print("ERROR: old")
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
    window = RenameOpWidget()
    window.show()

    app.exec_()