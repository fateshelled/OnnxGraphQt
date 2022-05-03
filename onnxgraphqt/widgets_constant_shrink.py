from collections import namedtuple
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from utils.op_names import OP_NAMES
from ast import literal_eval

ConstantShrinkProperties = namedtuple("ConstantShrinkProperties",
    [
        "mode",
        "forced_extraction_op_names",
        "forced_extraction_constant_names",
        "disable_auto_downcast",
    ])

MODE = [
    "shrink",
    "npy"
]

class ConstantShrinkWidgets(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 500

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("add node")
        self.initUI()

    def initUI(self):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)

        base_layout = QtWidgets.QVBoxLayout()

        # Form layout
        layout = QtWidgets.QFormLayout()
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        self.lbl_mode = QtWidgets.QLabel("mode")
        self.cmb_mode = QtWidgets.QComboBox()
        for m in MODE:
            self.cmb_mode.addItem(m)

        self.tb_forced_extraction_op_names = QtWidgets.QLineEdit()
        self.tb_forced_extraction_constant_names = QtWidgets.QLineEdit()
        layout.addRow("mode", self.cmb_mode)
        layout.addRow("forced_extraction_op_names", self.tb_forced_extraction_op_names)
        layout.addRow("forced_extraction_constant_names", self.tb_forced_extraction_constant_names)

        layout2 = QtWidgets.QVBoxLayout()
        self.check_auto_downcast = QtWidgets.QCheckBox("auto_downcast")
        self.check_auto_downcast.setChecked(True)
        layout2.addWidget(self.check_auto_downcast)
        layout2.setAlignment(self.check_auto_downcast, QtCore.Qt.AlignRight)

        # add layout
        base_layout.addLayout(layout)
        base_layout.addLayout(layout2)

        # Dialog button
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        # layout.addWidget(btn)
        base_layout.addWidget(btn)

        self.setLayout(base_layout)

    def get_properties(self)->ConstantShrinkProperties:
        mode = self.cmb_mode.currentText()
        forced_extraction_op_names = []
        forced_extraction_constant_names = []
        disable_auto_downcast = not self.check_auto_downcast.isChecked()

        op_names = self.tb_forced_extraction_op_names.text()
        if op_names:
            try:
                forced_extraction_op_names = literal_eval(op_names)
            except Exception as e:
                raise e

        constant_names = self.tb_forced_extraction_constant_names.text()
        if constant_names:
            try:
                forced_extraction_constant_names = literal_eval(constant_names)
            except Exception as e:
                raise e

        return ConstantShrinkProperties(
            mode=mode,
            forced_extraction_op_names=forced_extraction_op_names,
            forced_extraction_constant_names=forced_extraction_constant_names,
            disable_auto_downcast=disable_auto_downcast
        )

    def accept(self) -> None:
        # value check
        invalid = False
        try:
            props = self.get_properties()
            print(props)
        except Exception as e:
            print(e)
            return
        if not props.mode in MODE:
            print("ERROR: mode")
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
    window = ConstantShrinkWidgets()
    window.show()

    app.exec_()