from collections import namedtuple
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from utils.op_names import OP_NAMES
from ast import literal_eval
import numpy as np

from sam4onnx.onnx_attr_const_modify import (
    ATTRIBUTE_DTYPES_TO_NUMPY_TYPES,
    CONSTANT_DTYPES_TO_NUMPY_TYPES
)

ModifyAttrsProperties = namedtuple("ModifyAttrsProperties",
    [
        "op_name",
        "attributes",
        "input_constants",
    ])

class ModifyAttrsWidgets(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 500
    _MAX_ATTRIBUTES_COUNT = 5
    _MAX_CONST_COUNT = 4

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("modify attributes")
        self.initUI()

    def initUI(self):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)

        base_layout = QtWidgets.QVBoxLayout()

        # Form layout
        layout = QtWidgets.QFormLayout()
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        self.tb_opname = QtWidgets.QLineEdit()
        layout.addRow("opname", self.tb_opname)

        # attributes
        self.layout_attributes = QtWidgets.QVBoxLayout()
        self.layout_attributes.addWidget(QtWidgets.QLabel("attributes"))
        self.visible_attributes_count = 3
        self.edit_attributes = {}
        for index in range(self._MAX_ATTRIBUTES_COUNT):
            self.edit_attributes[index] = {}
            self.edit_attributes[index]["base"] = QtWidgets.QWidget()
            self.edit_attributes[index]["layout"] = QtWidgets.QHBoxLayout(self.edit_attributes[index]["base"])
            self.edit_attributes[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.edit_attributes[index]["name"] = QtWidgets.QLineEdit()
            self.edit_attributes[index]["name"].setPlaceholderText("name")
            self.edit_attributes[index]["value"] = QtWidgets.QLineEdit()
            self.edit_attributes[index]["value"].setPlaceholderText("value")
            self.edit_attributes[index]["dtype"] = QtWidgets.QComboBox()
            for key, dtype in ATTRIBUTE_DTYPES_TO_NUMPY_TYPES.items():
                self.edit_attributes[index]["dtype"].addItem(key, dtype)
            self.edit_attributes[index]["layout"].addWidget(self.edit_attributes[index]["name"])
            self.edit_attributes[index]["layout"].addWidget(self.edit_attributes[index]["value"])
            self.edit_attributes[index]["layout"].addWidget(self.edit_attributes[index]["dtype"])
            self.layout_attributes.addWidget(self.edit_attributes[index]["base"])
        self.btn_add_attributes = QtWidgets.QPushButton("+")
        self.btn_del_attributes = QtWidgets.QPushButton("-")
        self.btn_add_attributes.clicked.connect(self.btn_add_attributes_clicked)
        self.btn_del_attributes.clicked.connect(self.btn_del_attributes_clicked)
        self.set_visible_attributes()
        layout_btn_attributes = QtWidgets.QHBoxLayout()
        layout_btn_attributes.addWidget(self.btn_add_attributes)
        layout_btn_attributes.addWidget(self.btn_del_attributes)
        self.layout_attributes.addLayout(layout_btn_attributes)

        # input_const
        self.layout_const = QtWidgets.QVBoxLayout()
        self.layout_const.addItem(QtWidgets.QSpacerItem(self._DEFAULT_WINDOW_WIDTH, 20))
        self.layout_const.addWidget(QtWidgets.QLabel("input_constants"))
        self.visible_const_count = 3
        self.edit_const = {}
        for index in range(self._MAX_CONST_COUNT):
            self.edit_const[index] = {}
            self.edit_const[index]["base"] = QtWidgets.QWidget()
            self.edit_const[index]["layout"] = QtWidgets.QHBoxLayout(self.edit_const[index]["base"])
            self.edit_const[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.edit_const[index]["name"] = QtWidgets.QLineEdit()
            self.edit_const[index]["name"].setPlaceholderText("name")
            self.edit_const[index]["value"] = QtWidgets.QLineEdit()
            self.edit_const[index]["value"].setPlaceholderText("value")
            self.edit_const[index]["dtype"] = QtWidgets.QComboBox()
            for key, dtype in CONSTANT_DTYPES_TO_NUMPY_TYPES.items():
                self.edit_const[index]["dtype"].addItem(key, dtype)
            self.edit_const[index]["layout"].addWidget(self.edit_const[index]["name"])
            self.edit_const[index]["layout"].addWidget(self.edit_const[index]["value"])
            self.edit_const[index]["layout"].addWidget(self.edit_const[index]["dtype"])
            self.layout_const.addWidget(self.edit_const[index]["base"])
        self.btn_add_const = QtWidgets.QPushButton("+")
        self.btn_del_const = QtWidgets.QPushButton("-")
        self.btn_add_const.clicked.connect(self.btn_add_const_clicked)
        self.btn_del_const.clicked.connect(self.btn_del_const_clicked)
        self.set_visible_const()
        layout_btn_const = QtWidgets.QHBoxLayout()
        layout_btn_const.addWidget(self.btn_add_const)
        layout_btn_const.addWidget(self.btn_del_const)
        self.layout_const.addLayout(layout_btn_const)

        # add layout
        base_layout.addLayout(layout)
        base_layout.addLayout(self.layout_attributes)
        base_layout.addLayout(self.layout_const)

        # Dialog button
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        # layout.addWidget(btn)
        base_layout.addWidget(btn)

        self.setLayout(base_layout)

    def set_visible_attributes(self):
        for key, widgets in self.edit_attributes.items():
            widgets["base"].setVisible(key < self.visible_attributes_count)
        if self.visible_attributes_count == 1:
            self.btn_add_attributes.setEnabled(True)
            self.btn_del_attributes.setEnabled(False)
        elif self.visible_attributes_count >= self._MAX_ATTRIBUTES_COUNT:
            self.btn_add_attributes.setEnabled(False)
            self.btn_del_attributes.setEnabled(True)
        else:
            self.btn_add_attributes.setEnabled(True)
            self.btn_del_attributes.setEnabled(True)

    def set_visible_const(self):
        for key, widgets in self.edit_const.items():
            widgets["base"].setVisible(key < self.visible_const_count)
        if self.visible_const_count == 1:
            self.btn_add_const.setEnabled(True)
            self.btn_del_const.setEnabled(False)
        elif self.visible_const_count >= self._MAX_CONST_COUNT:
            self.btn_add_const.setEnabled(False)
            self.btn_del_const.setEnabled(True)
        else:
            self.btn_add_const.setEnabled(True)
            self.btn_del_const.setEnabled(True)

    def btn_add_attributes_clicked(self, e):
        self.visible_attributes_count = min(max(0, self.visible_attributes_count + 1), self._MAX_ATTRIBUTES_COUNT)
        self.set_visible_attributes()

    def btn_del_attributes_clicked(self, e):
        self.visible_attributes_count = min(max(0, self.visible_attributes_count - 1), self._MAX_ATTRIBUTES_COUNT)
        self.set_visible_attributes()

    def btn_add_const_clicked(self, e):
        self.visible_const_count = min(max(0, self.visible_const_count + 1), self._MAX_CONST_COUNT)
        self.set_visible_const()

    def btn_del_const_clicked(self, e):
        self.visible_const_count = min(max(0, self.visible_const_count - 1), self._MAX_CONST_COUNT)
        self.set_visible_const()

    def get_properties(self)->ModifyAttrsProperties:
        opname = self.tb_opname.text()

        attributes = {}
        for i in range(self.visible_attributes_count):
            name = self.edit_attributes[i]["name"].text()
            value = self.edit_attributes[i]["value"].text()
            dtype = self.edit_attributes[i]["dtype"].currentData()
            if name and value:
                value = literal_eval(value)
                if isinstance(value, list):
                    attributes[name] = np.asarray(value, dtype=dtype)
                else:
                    attributes[name] = value
        if len(attributes) == 0:
            attributes = None

        input_constants = {}
        for i in range(self.visible_const_count):
            name = self.edit_const[i]["name"].text()
            value = self.edit_const[i]["value"].text()
            dtype = self.edit_const[i]["dtype"].currentData()
            if name and value:
                value = literal_eval(value)
                if isinstance(value, list):
                    input_constants[name] = np.asarray(value, dtype=dtype)
                else:
                    input_constants[name] = value
        if len(input_constants) == 0:
            input_constants = None
        return ModifyAttrsProperties(
            op_name=opname,
            attributes=attributes,
            input_constants=input_constants
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        edit_attr = (props.op_name) and (len(props.attributes) > 0)
        edit_const = True
        if props.input_constants is None:
            edit_const = False
        else:
            edit_const = len(props.input_constants) > 0
        if edit_attr and edit_const:
            print("ERROR: Specify only one of attributes or input_constants.")
            invalid = True
        if not edit_attr and not edit_const:
            print("ERROR: Specify attributes or input_constants")
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
    window = ModifyAttrsWidgets()
    window.show()

    app.exec_()