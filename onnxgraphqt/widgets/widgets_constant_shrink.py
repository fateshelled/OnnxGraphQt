from collections import namedtuple
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from ast import literal_eval

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.widgets import set_font, BASE_FONT_SIZE, LARGE_FONT_SIZE
from widgets.widgets_message_box import MessageBox


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
        self.setModal(False)
        self.setWindowTitle("constant shrink")
        self.initUI()

    def initUI(self):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)
        set_font(self, font_size=BASE_FONT_SIZE)

        base_layout = QtWidgets.QVBoxLayout()

        # Form layout
        layout = QtWidgets.QFormLayout()
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        lbl_mode = QtWidgets.QLabel("mode")
        set_font(lbl_mode, font_size=LARGE_FONT_SIZE, bold=True)
        self.cmb_mode = QtWidgets.QComboBox()
        for m in MODE:
            self.cmb_mode.addItem(m)

        lbl_forced_extraction_op_names = QtWidgets.QLabel("forced_extraction_op_names")
        set_font(lbl_forced_extraction_op_names, font_size=LARGE_FONT_SIZE, bold=True)
        self.tb_forced_extraction_op_names = QtWidgets.QLineEdit()
        self.tb_forced_extraction_op_names.setPlaceholderText("e.g. ['aaa','bbb','ccc']")

        lbl_forced_extraction_constant_names = QtWidgets.QLabel("forced_extraction_constant_names")
        set_font(lbl_forced_extraction_constant_names, font_size=LARGE_FONT_SIZE, bold=True)
        self.tb_forced_extraction_constant_names = QtWidgets.QLineEdit()
        self.tb_forced_extraction_constant_names.setPlaceholderText("e.g. ['aaa','bbb','ccc']")

        layout.addRow(lbl_mode, self.cmb_mode)
        layout.addRow(lbl_forced_extraction_op_names, self.tb_forced_extraction_op_names)
        layout.addRow(lbl_forced_extraction_constant_names, self.tb_forced_extraction_constant_names)

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
            err_msgs = []
        except Exception as e:
            print(e)
            return
        if not props.mode in MODE:
            err_msgs.append(f"- mode is select from {'or'.join(MODE)}")
            invalid = True
        if invalid:
            for m in err_msgs:
                print(m)
            MessageBox.error(err_msgs, "constant shrink", parent=self)
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