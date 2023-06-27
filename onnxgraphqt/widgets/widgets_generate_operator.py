from collections import namedtuple
from typing import List, Dict
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from ast import literal_eval
import numpy as np

from onnxgraphqt.utils.opset import DEFAULT_OPSET
from onnxgraphqt.utils.operators import onnx_opsets, opnames, OperatorVersion, latest_opset
from onnxgraphqt.utils.widgets import set_font, BASE_FONT_SIZE, LARGE_FONT_SIZE
from onnxgraphqt.widgets.widgets_message_box import MessageBox


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
    _MAX_ATTRIBUTES_COUNT = 10

    def __init__(self, opset=DEFAULT_OPSET, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("generate operator")
        self.initUI(opset)

    def initUI(self, opset:int):
        # self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)
        set_font(self, font_size=BASE_FONT_SIZE)

        base_layout = QtWidgets.QVBoxLayout()
        base_layout.setSizeConstraint(base_layout.SizeConstraint.SetFixedSize)

        # Form layout
        layout = QtWidgets.QFormLayout()
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        self.cmb_optype = QtWidgets.QComboBox()
        self.cmb_optype.setEditable(True)
        lbl_op_type = QtWidgets.QLabel("op_type")
        set_font(lbl_op_type, font_size=LARGE_FONT_SIZE, bold=True)
        layout.addRow(lbl_op_type, self.cmb_optype)

        self.cmb_opset = QtWidgets.QComboBox()
        self.cmb_opset.setEditable(True)
        for i in range(1,latest_opset + 1):
            self.cmb_opset.addItem(str(i), i)
        lbl_opset = QtWidgets.QLabel("opset")
        set_font(lbl_opset, font_size=LARGE_FONT_SIZE, bold=True)
        layout.addRow(lbl_opset, self.cmb_opset)

        self.tb_opname = QtWidgets.QLineEdit()
        self.tb_opname.setText("")
        lbl_op_name = QtWidgets.QLabel("op_name")
        set_font(lbl_op_name, font_size=LARGE_FONT_SIZE, bold=True)
        layout.addRow(lbl_op_name, self.tb_opname)

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
        lbl_inp_val = QtWidgets.QLabel("input valiables [optional]")
        set_font(lbl_inp_val, font_size=LARGE_FONT_SIZE, bold=True)
        self.layout_valiables.addWidget(lbl_inp_val)
        for key, widgets in self.add_input_valiables.items():
            self.layout_valiables.addWidget(widgets["base"])
        layout_btn_input = QtWidgets.QHBoxLayout()
        layout_btn_input.addWidget(self.btn_add_input_valiables)
        layout_btn_input.addWidget(self.btn_del_input_valiables)
        self.layout_valiables.addLayout(layout_btn_input)

        self.layout_valiables.addItem(QtWidgets.QSpacerItem(self._DEFAULT_WINDOW_WIDTH, 20))
        lbl_out_val = QtWidgets.QLabel("output valiables [optional]")
        set_font(lbl_out_val, font_size=LARGE_FONT_SIZE, bold=True)
        self.layout_valiables.addWidget(lbl_out_val)
        for key, widgets in self.add_output_valiables.items():
            self.layout_valiables.addWidget(widgets["base"])
        layout_btn_output = QtWidgets.QHBoxLayout()
        layout_btn_output.addWidget(self.btn_add_output_valiables)
        layout_btn_output.addWidget(self.btn_del_output_valiables)
        self.layout_valiables.addLayout(layout_btn_output)

        # add_attributes
        self.layout_attributes = QtWidgets.QVBoxLayout()
        self.layout_attributes.addItem(QtWidgets.QSpacerItem(self._DEFAULT_WINDOW_WIDTH, 20))
        lbl_atrributes = QtWidgets.QLabel("atrributes [optional]")
        set_font(lbl_atrributes, font_size=LARGE_FONT_SIZE, bold=True)
        self.layout_attributes.addWidget(lbl_atrributes)
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
        base_layout.addWidget(btn)

        self.setLayout(base_layout)

        self.cmb_optype.currentIndexChanged.connect(self.cmb_optype_currentIndexChanged)
        self.cmb_opset.currentIndexChanged.connect(self.cmb_opset_currentIndexChanged)
        self.cmb_opset.setCurrentIndex(opset-1)

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
        if self.visible_input_valiables_count == 0:
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
        if self.visible_output_valiables_count == 0:
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
        if self.visible_attributes_count == 0:
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

    def cmb_optype_currentIndexChanged(self, selected_index:int):
        selected_operator: OperatorVersion = self.cmb_optype.currentData()
        if selected_operator:
            self.visible_input_valiables_count = selected_operator.inputs
            self.visible_output_valiables_count = selected_operator.outputs
            self.visible_attributes_count = min(max(0, len(selected_operator.attrs)), self._MAX_ATTRIBUTES_COUNT)

            for i, att in enumerate(selected_operator.attrs):
                self.attributes[i]["name"].setText(att.name)
                self.attributes[i]["value"].setText(att.default_value)
            for j in range(len(selected_operator.attrs), self._MAX_ATTRIBUTES_COUNT):
                self.attributes[j]["name"].setText("")
                self.attributes[j]["value"].setText("")
        self.set_visible_input_valiables()
        self.set_visible_output_valiables()
        self.set_visible_add_op_attributes()

    def cmb_opset_currentIndexChanged(self, selected_index:int):
        current_opset:int = self.cmb_opset.currentData()
        current_optype = self.cmb_optype.currentText()
        current_optype_index = 0
        self.cmb_optype.clear()
        for i, op in enumerate(onnx_opsets):
            for v in op.versions:
                if v.since_opset <= current_opset:
                    if op.name == current_optype:
                        current_optype_index = self.cmb_optype.count()
                    self.cmb_optype.addItem(op.name, v)
                    break
        self.cmb_optype.setCurrentIndex(current_optype_index)

    def get_properties(self)->GenerateOperatorProperties:

        op_type = self.cmb_optype.currentText()
        opset = self.cmb_opset.currentText()
        if opset:
            opset = literal_eval(opset)
        if not isinstance(opset, int):
            opset = ""
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
        err_msgs = []
        if not props.op_type in opnames:
            err_msgs.append("- op_type is invalid.")
            invalid = True
        if not isinstance(props.opset, int):
            err_msgs.append("- opset must be unsigned integer.")
            invalid = True
        if not props.op_name:
            err_msgs.append("- op_name is not set.")
            invalid = True
        if invalid:
            for m in err_msgs:
                print(m)
            MessageBox.error(err_msgs, "generate operator", parent=self)
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