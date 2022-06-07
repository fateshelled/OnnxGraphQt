from collections import namedtuple
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from ast import literal_eval

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.operators import onnx_opsets, opnames, OperatorVersion

AVAILABLE_DTYPES = [
    'float32',
    'float64',
    'int32',
    'int64',
    'str',
]

AddNodeProperties = namedtuple("AddNodeProperties",
    [
        "connection_src_op_output_name",
        "connection_dest_op_input_name",
        "add_op_type",
        "add_op_name",
        "add_op_input_variables",
        "add_op_output_variables",
        "add_op_attributes",
    ])

class AddNodeWidgets(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 500
    _MAX_VARIABLES_COUNT = 5
    _MAX_ATTRIBUTES_COUNT = 10

    def __init__(self, current_opset:int, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("add node")
        self.current_opset = current_opset
        self.initUI()

    def initUI(self):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)

        base_layout = QtWidgets.QVBoxLayout()
        base_layout.setSizeConstraint(base_layout.SizeConstraint.SetFixedSize)

        # Form layout
        layout = QtWidgets.QFormLayout()
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        self.src_output_name = QtWidgets.QLineEdit()
        self.src_output_name.setPlaceholderText("List of op name. Separater is space ' '.")
        self.dst_input_name = QtWidgets.QLineEdit()
        self.dst_input_name.setPlaceholderText("e.g. `Sub_451 onnx::Pow_603 dummy_mul inp1`")
        self.add_op_type = QtWidgets.QComboBox()
        for op in onnx_opsets:
            for version in op.versions:
                if version.since_opset <= self.current_opset:
                    self.add_op_type.addItem(op.name, op.versions[0])
                    break
        self.add_op_type.setEditable(True)
        self.add_op_type.currentIndexChanged.connect(self.add_op_type_currentIndexChanged)
        self.add_op_name = QtWidgets.QLineEdit()
        self.add_op_name.setPlaceholderText("Name of op to be added")

        layout.addRow("src_output_name", self.src_output_name)
        layout.addRow("dst_input_name", self.dst_input_name)
        layout.addRow("add_op_name", self.add_op_name)
        layout.addRow("add_op_type", self.add_op_type)

        # variables
        self.layout_valiables = QtWidgets.QVBoxLayout()
        self.visible_input_valiables_count = 1
        self.visible_output_valiables_count = 1

        self.add_input_valiables = {}
        self.add_output_valiables = {}
        for i in range(self._MAX_VARIABLES_COUNT):
            self.create_variables_widget(i, is_input=True)
        for i in range(self._MAX_VARIABLES_COUNT):
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
        self.layout_valiables.addWidget(QtWidgets.QLabel("add op input valiables [optional]"))
        for key, widgets in self.add_input_valiables.items():
            self.layout_valiables.addWidget(widgets["base"])
        self.set_visible_input_valiables()
        layout_btn_input = QtWidgets.QHBoxLayout()
        layout_btn_input.addWidget(self.btn_add_input_valiables)
        layout_btn_input.addWidget(self.btn_del_input_valiables)
        self.layout_valiables.addLayout(layout_btn_input)

        self.layout_valiables.addItem(QtWidgets.QSpacerItem(self._DEFAULT_WINDOW_WIDTH, 20))
        self.layout_valiables.addWidget(QtWidgets.QLabel("add op output valiables [optional]"))
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
        self.layout_attributes.addWidget(QtWidgets.QLabel("add op atrributes [optional]"))
        self.visible_add_attributes_count = 3
        self.add_op_attributes = {}
        for index in range(self._MAX_ATTRIBUTES_COUNT):
            self.add_op_attributes[index] = {}
            self.add_op_attributes[index]["base"] = QtWidgets.QWidget()
            self.add_op_attributes[index]["layout"] = QtWidgets.QHBoxLayout(self.add_op_attributes[index]["base"])
            self.add_op_attributes[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.add_op_attributes[index]["name"] = QtWidgets.QLineEdit()
            self.add_op_attributes[index]["name"].setPlaceholderText("name")
            self.add_op_attributes[index]["value"] = QtWidgets.QLineEdit()
            self.add_op_attributes[index]["value"].setPlaceholderText("value")
            self.add_op_attributes[index]["layout"].addWidget(self.add_op_attributes[index]["name"])
            self.add_op_attributes[index]["layout"].addWidget(self.add_op_attributes[index]["value"])
            self.layout_attributes.addWidget(self.add_op_attributes[index]["base"])
        self.btn_add_op_attributes = QtWidgets.QPushButton("+")
        self.btn_del_op_attributes = QtWidgets.QPushButton("-")
        self.btn_add_op_attributes.clicked.connect(self.btn_add_op_attributes_clicked)
        self.btn_del_op_attributes.clicked.connect(self.btn_del_op_attributes_clicked)
        self.set_visible_add_op_attributes()
        layout_btn_attributes = QtWidgets.QHBoxLayout()
        layout_btn_attributes.addWidget(self.btn_add_op_attributes)
        layout_btn_attributes.addWidget(self.btn_del_op_attributes)
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
        self.add_op_type_currentIndexChanged(self.add_op_type.currentIndex())

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
        elif self.visible_input_valiables_count >= self._MAX_VARIABLES_COUNT:
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
        elif self.visible_output_valiables_count >= self._MAX_VARIABLES_COUNT:
            self.btn_add_output_valiables.setEnabled(False)
            self.btn_del_output_valiables.setEnabled(True)
        else:
            self.btn_add_output_valiables.setEnabled(True)
            self.btn_del_output_valiables.setEnabled(True)

    def set_visible_add_op_attributes(self):
        for key, widgets in self.add_op_attributes.items():
            widgets["base"].setVisible(key < self.visible_add_attributes_count)
        if self.visible_add_attributes_count == 0:
            self.btn_add_op_attributes.setEnabled(True)
            self.btn_del_op_attributes.setEnabled(False)
        elif self.visible_add_attributes_count >= self._MAX_ATTRIBUTES_COUNT:
            self.btn_add_op_attributes.setEnabled(False)
            self.btn_del_op_attributes.setEnabled(True)
        else:
            self.btn_add_op_attributes.setEnabled(True)
            self.btn_del_op_attributes.setEnabled(True)

    def btn_add_input_valiables_clicked(self, e):
        self.visible_input_valiables_count = min(max(0, self.visible_input_valiables_count + 1), self._MAX_VARIABLES_COUNT)
        self.set_visible_input_valiables()

    def btn_del_input_valiables_clicked(self, e):
        self.visible_input_valiables_count = min(max(0, self.visible_input_valiables_count - 1), self._MAX_VARIABLES_COUNT)
        self.set_visible_input_valiables()

    def btn_add_output_valiables_clicked(self, e):
        self.visible_output_valiables_count = min(max(0, self.visible_output_valiables_count + 1), self._MAX_VARIABLES_COUNT)
        self.set_visible_output_valiables()

    def btn_del_output_valiables_clicked(self, e):
        self.visible_output_valiables_count = min(max(0, self.visible_output_valiables_count - 1), self._MAX_VARIABLES_COUNT)
        self.set_visible_output_valiables()

    def btn_add_op_attributes_clicked(self, e):
        self.visible_add_attributes_count = min(max(0, self.visible_add_attributes_count + 1), self._MAX_ATTRIBUTES_COUNT)
        self.set_visible_add_op_attributes()

    def btn_del_op_attributes_clicked(self, e):
        self.visible_add_attributes_count = min(max(0, self.visible_add_attributes_count - 1), self._MAX_ATTRIBUTES_COUNT)
        self.set_visible_add_op_attributes()

    def add_op_type_currentIndexChanged(self, selected_index:int):
        selected_operator: OperatorVersion = self.add_op_type.currentData()
        self.visible_input_valiables_count = selected_operator.inputs
        self.visible_output_valiables_count = selected_operator.outputs
        self.visible_add_attributes_count = min(max(0, len(selected_operator.attrs)), self._MAX_ATTRIBUTES_COUNT)

        for i, att in enumerate(selected_operator.attrs):
            self.add_op_attributes[i]["name"].setText(att.name)
            self.add_op_attributes[i]["value"].setText(att.default_value)
        for j in range(len(selected_operator.attrs), self._MAX_ATTRIBUTES_COUNT):
            self.add_op_attributes[j]["name"].setText("")
            self.add_op_attributes[j]["value"].setText("")
        self.set_visible_input_valiables()
        self.set_visible_output_valiables()
        self.set_visible_add_op_attributes()

    def get_properties(self)->AddNodeProperties:
        add_op_input_variables = {}
        add_op_output_variables = {}
        for i in range(self.visible_input_valiables_count):
            name = self.add_input_valiables[i]["name"].text()
            dtype = self.add_input_valiables[i]["dtype"].currentText()
            shape = self.add_input_valiables[i]["shape"].text()
            if name and dtype and shape:
                add_op_input_variables[name] = [dtype, literal_eval(shape)]
        for i in range(self.visible_output_valiables_count):
            name = self.add_output_valiables[i]["name"].text()
            dtype = self.add_output_valiables[i]["dtype"].currentText()
            shape = self.add_output_valiables[i]["shape"].text()
            if name and dtype and shape:
                add_op_output_variables[name] = [dtype, literal_eval(shape)]

        if len(add_op_input_variables) == 0:
            add_op_input_variables = None
        if len(add_op_output_variables) == 0:
            add_op_output_variables = None

        add_op_attributes = {}
        for i in range(self.visible_add_attributes_count):
            name = self.add_op_attributes[i]["name"].text()
            value = self.add_op_attributes[i]["value"].text()
            if name and value:
                try:
                    # For literal
                    add_op_attributes[name] = literal_eval(value)
                except BaseException as e:
                    # For str
                    add_op_attributes[name] = value
        if len(add_op_attributes) == 0:
            add_op_attributes = None

        src_output_name = self.src_output_name.text().strip()
        if src_output_name:
            src_output_name = [n.strip() for n in src_output_name.split(" ")]
        else:
            src_output_name = []

        dst_input_name = self.dst_input_name.text().strip()
        if dst_input_name:
            dst_input_name = [n.strip() for n in dst_input_name.split(" ")]
        else:
            dst_input_name = []

        return AddNodeProperties(
            connection_src_op_output_name=src_output_name,
            connection_dest_op_input_name=dst_input_name,
            add_op_type=self.add_op_type.currentText(),
            add_op_name=self.add_op_name.text(),
            add_op_input_variables=add_op_input_variables,
            add_op_output_variables=add_op_output_variables,
            add_op_attributes=add_op_attributes,
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        if len(props.connection_src_op_output_name) < 1:
            print("ERROR: connection_src_op_output_name")
            invalid = True
        if len(props.connection_dest_op_input_name) < 1:
            print("ERROR: connection_dest_op_input_name")
            invalid = True
        if not props.add_op_name:
            print("ERROR: add_op_name")
            invalid = True
        if not props.add_op_type in opnames:
            print("ERROR: add_op_type")
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
    window = AddNodeWidgets(current_opset=16)
    window.show()

    app.exec_()