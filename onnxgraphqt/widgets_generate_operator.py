from collections import namedtuple
from typing import List, Dict
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from ast import literal_eval
import numpy as np
from utils.opset import DEFAULT_OPSET
from utils.operators import onnx_opsets, opnames

AVAILABLE_DTYPES = [
    'float32',
    'float64',
    'int32',
    'int64',
    'str',
]

GenerateOperatorProperties = namedtuple("GenerateOperatorProperties",
    [
        "op_type",
        "opset",
        "op_name",
        "input_variables",
        "output_variables",
        "attributes",
    ])


class GenerateOperatorWidgets(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 500
    _MAX_INPUT_VARIABLES_COUNT = 5
    _MAX_OUTPUT_VARIABLES_COUNT = 5
    _MAX_ATTRIBUTES_COUNT = 5

    def __init__(self, opset=DEFAULT_OPSET, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("generate operator")
        self.initUI(opset)

    def initUI(self, opset):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)

        base_layout = QtWidgets.QVBoxLayout()

        # Form layout
        layout = QtWidgets.QFormLayout()
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        self.cmb_optype = QtWidgets.QComboBox()
        for op in onnx_opsets:
            self.cmb_optype.addItem(op.name)
        self.cmb_optype.setEditable(True)
        self.cmb_optype.setCurrentIndex(-1)
        layout.addRow("op_type", self.cmb_optype)

        self.tb_opset = QtWidgets.QLineEdit()
        self.tb_opset.setText(str(opset))
        layout.addRow("opset", self.tb_opset)

        self.tb_opname = QtWidgets.QLineEdit()
        self.tb_opname.setText("")
        layout.addRow("op_name", self.tb_opname)

        # variables
        self.layout_valiables = QtWidgets.QVBoxLayout()
        self.visible_input_valiables_count = 1
        self.visible_output_valiables_count = 1

        self.add_input_valiables = {}
        self.add_output_valiables = {}
        for i in range(self._MAX_INPUT_VARIABLES_COUNT):
            self.create_variables_widget(i, is_input=True)
        for i in range(self._MAX_OUTPUT_VARIABLES_COUNT):
            self.create_variables_widget(i, is_input=False)

        self.btn_add_input_valiables = QtWidgets.QPushButton("+")
        self.btn_del_input_valiables = QtWidgets.QPushButton("-")
        self.btn_add_input_valiables.clicked.connect(self.btn_add_input_valiables_clicked)
        self.btn_del_input_valiables.clicked.connect(self.btn_del_input_valiables_clicked)
        self.btn_add_output_valiables = QtWidgets.QPushButton("+")
        self.btn_del_output_valiables = QtWidgets.QPushButton("-")
        self.btn_add_output_valiables.clicked.connect(self.btn_add_output_valiables_clicked)
        self.btn_del_output_valiables.clicked.connect(self.btn_del_output_valiables_clicked)

        self.layout_valiables.addItem(QtWidgets.QSpacerItem(self._DEFAULT_WINDOW_WIDTH, 20))
        self.layout_valiables.addWidget(QtWidgets.QLabel("input valiables [optional]"))
        for key, widgets in self.add_input_valiables.items():
            self.layout_valiables.addWidget(widgets["base"])
        self.set_visible_input_valiables()
        layout_btn_input = QtWidgets.QHBoxLayout()
        layout_btn_input.addWidget(self.btn_add_input_valiables)
        layout_btn_input.addWidget(self.btn_del_input_valiables)
        self.layout_valiables.addLayout(layout_btn_input)

        self.layout_valiables.addItem(QtWidgets.QSpacerItem(self._DEFAULT_WINDOW_WIDTH, 20))
        self.layout_valiables.addWidget(QtWidgets.QLabel("output valiables [optional]"))
        for key, widgets in self.add_output_valiables.items():
            self.layout_valiables.addWidget(widgets["base"])
        self.set_visible_output_valiables()
        layout_btn_output = QtWidgets.QHBoxLayout()
        layout_btn_output.addWidget(self.btn_add_output_valiables)
        layout_btn_output.addWidget(self.btn_del_output_valiables)
        self.layout_valiables.addLayout(layout_btn_output)

        # add_attributes
        self.layout_attributes = QtWidgets.QVBoxLayout()
        self.layout_attributes.addItem(QtWidgets.QSpacerItem(self._DEFAULT_WINDOW_WIDTH, 20))
        self.layout_attributes.addWidget(QtWidgets.QLabel("atrributes [optional]"))
        self.visible_attributes_count = 3
        self.attributes = {}
        for index in range(self._MAX_ATTRIBUTES_COUNT):
            self.attributes[index] = {}
            self.attributes[index]["base"] = QtWidgets.QWidget()
            self.attributes[index]["layout"] = QtWidgets.QHBoxLayout(self.attributes[index]["base"])
            self.attributes[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.attributes[index]["name"] = QtWidgets.QLineEdit()
            self.attributes[index]["name"].setPlaceholderText("name")
            self.attributes[index]["value"] = QtWidgets.QLineEdit()
            self.attributes[index]["value"].setPlaceholderText("value")
            self.attributes[index]["layout"].addWidget(self.attributes[index]["name"])
            self.attributes[index]["layout"].addWidget(self.attributes[index]["value"])
            self.layout_attributes.addWidget(self.attributes[index]["base"])
        self.btn_add_attributes = QtWidgets.QPushButton("+")
        self.btn_del_attributes = QtWidgets.QPushButton("-")
        self.btn_add_attributes.clicked.connect(self.btn_add_attributes_clicked)
        self.btn_del_attributes.clicked.connect(self.btn_del_attributes_clicked)
        self.set_visible_add_op_attributes()
        layout_btn_attributes = QtWidgets.QHBoxLayout()
        layout_btn_attributes.addWidget(self.btn_add_attributes)
        layout_btn_attributes.addWidget(self.btn_del_attributes)
        self.layout_attributes.addLayout(layout_btn_attributes)

        # add layout
        base_layout.addLayout(layout)
        base_layout.addLayout(self.layout_valiables)
        base_layout.addLayout(self.layout_attributes)

        # Dialog button
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        # layout.addWidget(btn)
        base_layout.addWidget(btn)

        self.setLayout(base_layout)

    def create_variables_widget(self, index:int, is_input=True)->QtWidgets.QBoxLayout:
        if is_input:
            self.add_input_valiables[index] = {}
            self.add_input_valiables[index]["base"] = QtWidgets.QWidget()
            self.add_input_valiables[index]["layout"] = QtWidgets.QHBoxLayout(self.add_input_valiables[index]["base"])
            self.add_input_valiables[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.add_input_valiables[index]["name"] = QtWidgets.QLineEdit()
            self.add_input_valiables[index]["name"].setPlaceholderText("name")
            self.add_input_valiables[index]["dtype"] = QtWidgets.QComboBox()
            for dtype in AVAILABLE_DTYPES:
                self.add_input_valiables[index]["dtype"].addItem(dtype)
                self.add_input_valiables[index]["dtype"].setEditable(True)
            self.add_input_valiables[index]["dtype"].setFixedSize(100, 20)
            self.add_input_valiables[index]["shape"] = QtWidgets.QLineEdit()
            self.add_input_valiables[index]["shape"].setPlaceholderText("shape. e.g. `[1, 2, 3]`")
            self.add_input_valiables[index]["layout"].addWidget(self.add_input_valiables[index]["name"])
            self.add_input_valiables[index]["layout"].addWidget(self.add_input_valiables[index]["dtype"])
            self.add_input_valiables[index]["layout"].addWidget(self.add_input_valiables[index]["shape"])
        else:
            self.add_output_valiables[index] = {}
            self.add_output_valiables[index]["base"] = QtWidgets.QWidget()
            self.add_output_valiables[index]["layout"] = QtWidgets.QHBoxLayout(self.add_output_valiables[index]["base"])
            self.add_output_valiables[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.add_output_valiables[index]["name"] = QtWidgets.QLineEdit()
            self.add_output_valiables[index]["name"].setPlaceholderText("name")
            self.add_output_valiables[index]["dtype"] = QtWidgets.QComboBox()
            for dtype in AVAILABLE_DTYPES:
                self.add_output_valiables[index]["dtype"].addItem(dtype)
            self.add_output_valiables[index]["dtype"].setEditable(True)
            self.add_output_valiables[index]["dtype"].setFixedSize(100, 20)
            self.add_output_valiables[index]["dtype"].setPlaceholderText("dtype. e.g. `float32`")
            self.add_output_valiables[index]["shape"] = QtWidgets.QLineEdit()
            self.add_output_valiables[index]["shape"].setPlaceholderText("shape. e.g. `[1, 2, 3]`")
            self.add_output_valiables[index]["layout"].addWidget(self.add_output_valiables[index]["name"])
            self.add_output_valiables[index]["layout"].addWidget(self.add_output_valiables[index]["dtype"])
            self.add_output_valiables[index]["layout"].addWidget(self.add_output_valiables[index]["shape"])

    def set_visible_input_valiables(self):
        for key, widgets in self.add_input_valiables.items():
            widgets["base"].setVisible(key < self.visible_input_valiables_count)
        if self.visible_input_valiables_count == 1:
            self.btn_add_input_valiables.setEnabled(True)
            self.btn_del_input_valiables.setEnabled(False)
        elif self.visible_input_valiables_count >= self._MAX_INPUT_VARIABLES_COUNT:
            self.btn_add_input_valiables.setEnabled(False)
            self.btn_del_input_valiables.setEnabled(True)
        else:
            self.btn_add_input_valiables.setEnabled(True)
            self.btn_del_input_valiables.setEnabled(True)

    def set_visible_output_valiables(self):
        for key, widgets in self.add_output_valiables.items():
            widgets["base"].setVisible(key < self.visible_output_valiables_count)
        if self.visible_output_valiables_count == 1:
            self.btn_add_output_valiables.setEnabled(True)
            self.btn_del_output_valiables.setEnabled(False)
        elif self.visible_output_valiables_count >= self._MAX_OUTPUT_VARIABLES_COUNT:
            self.btn_add_output_valiables.setEnabled(False)
            self.btn_del_output_valiables.setEnabled(True)
        else:
            self.btn_add_output_valiables.setEnabled(True)
            self.btn_del_output_valiables.setEnabled(True)

    def set_visible_add_op_attributes(self):
        for key, widgets in self.attributes.items():
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

    def btn_add_input_valiables_clicked(self, e):
        self.visible_input_valiables_count = min(max(0, self.visible_input_valiables_count + 1), self._MAX_INPUT_VARIABLES_COUNT)
        self.set_visible_input_valiables()

    def btn_del_input_valiables_clicked(self, e):
        self.visible_input_valiables_count = min(max(0, self.visible_input_valiables_count - 1), self._MAX_INPUT_VARIABLES_COUNT)
        self.set_visible_input_valiables()

    def btn_add_output_valiables_clicked(self, e):
        self.visible_output_valiables_count = min(max(0, self.visible_output_valiables_count + 1), self._MAX_OUTPUT_VARIABLES_COUNT)
        self.set_visible_output_valiables()

    def btn_del_output_valiables_clicked(self, e):
        self.visible_output_valiables_count = min(max(0, self.visible_output_valiables_count - 1), self._MAX_OUTPUT_VARIABLES_COUNT)
        self.set_visible_output_valiables()

    def btn_add_attributes_clicked(self, e):
        self.visible_attributes_count = min(max(0, self.visible_attributes_count + 1), self._MAX_ATTRIBUTES_COUNT)
        self.set_visible_add_op_attributes()

    def btn_del_attributes_clicked(self, e):
        self.visible_attributes_count = min(max(0, self.visible_attributes_count - 1), self._MAX_ATTRIBUTES_COUNT)
        self.set_visible_add_op_attributes()

    def get_properties(self)->GenerateOperatorProperties:

        op_type = self.cmb_optype.currentText()
        opset = self.tb_opset.text()
        if opset:
            opset = literal_eval(opset)
        if not isinstance(opset, int):
            opset = DEFAULT_OPSET
        op_name = self.tb_opname.text()

        input_variables = {}
        output_variables = {}
        for i in range(self.visible_input_valiables_count):
            name = self.add_input_valiables[i]["name"].text()
            dtype = self.add_input_valiables[i]["dtype"].currentText()
            shape = self.add_input_valiables[i]["shape"].text()
            if name and dtype and shape:
                input_variables[name] = [dtype, literal_eval(shape)]
        for i in range(self.visible_output_valiables_count):
            name = self.add_output_valiables[i]["name"].text()
            dtype = self.add_output_valiables[i]["dtype"].currentText()
            shape = self.add_output_valiables[i]["shape"].text()
            if name and dtype and shape:
                output_variables[name] = [dtype, literal_eval(shape)]

        if len(input_variables) == 0:
            input_variables = None
        if len(output_variables) == 0:
            output_variables = None

        attributes = {}
        for i in range(self.visible_attributes_count):
            name = self.attributes[i]["name"].text()
            value = self.attributes[i]["value"].text()
            if name and value:
                attributes[name] = literal_eval(value)
        if len(attributes) == 0:
            attributes = None


        return GenerateOperatorProperties(
            op_type=op_type,
            opset=opset,
            op_name=op_name,
            input_variables=input_variables,
            output_variables=output_variables,
            attributes=attributes,
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        if not props.op_name:
            print("ERROR: op_name")
            invalid = True
        if not props.op_type:
            print("ERROR: op_type")
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
    window = GenerateOperatorWidgets()
    window.show()

    app.exec_()