from collections import namedtuple
from typing import List, Dict
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from ast import literal_eval
import numpy as np
from sam4onnx.onnx_attr_const_modify import (
    ATTRIBUTE_DTYPES_TO_NUMPY_TYPES,
    CONSTANT_DTYPES_TO_NUMPY_TYPES
)

from onnxgraphqt.graph.onnx_node_graph import OnnxGraph
from onnxgraphqt.widgets.widgets_message_box import MessageBox
from onnxgraphqt.utils.widgets import set_font, BASE_FONT_SIZE, LARGE_FONT_SIZE


ModifyAttrsProperties = namedtuple("ModifyAttrsProperties",
    [
        "op_name",
        "attributes",
        "input_constants",
        "delete_attributes",
    ])


def get_dtype_str(list_or_scalar)->str:
    v0 = None
    if isinstance(list_or_scalar, list):
        v0 = np.ravel(list_or_scalar)[0].tolist()
    else:
        v0 = list_or_scalar

    if isinstance(v0, int):
        dtype = "int32"
    elif isinstance(v0, float):
        dtype = "float32"
    elif isinstance(v0, complex):
        dtype = "complex64"
    elif isinstance(v0, bool):
        dtype = "bool"
    elif v0 is None:
        dtype = ""
    else:
        dtype = "str"
    return dtype


class ModifyAttrsWidgets(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 500
    _MAX_ATTRIBUTES_COUNT = 5
    _MAX_DELETE_ATTRIBUTES_COUNT = 5
    _MAX_CONST_COUNT = 4

    def __init__(self, graph: OnnxGraph=None, selected_node: str="", parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("modify attributes")
        self.graph = graph
        self.initUI()
        self.updateUI(self.graph, selected_node)

    def initUI(self):
        # self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)
        set_font(self, font_size=BASE_FONT_SIZE)

        base_layout = QtWidgets.QVBoxLayout()
        base_layout.setSizeConstraint(base_layout.SizeConstraint.SetFixedSize)

        # Form layout
        layout = QtWidgets.QFormLayout()
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        self.cmb_opname = QtWidgets.QComboBox()
        self.cmb_opname.setEditable(True)
        lbl_opname = QtWidgets.QLabel("opname")
        set_font(lbl_opname, font_size=LARGE_FONT_SIZE, bold=True)
        layout.addRow(lbl_opname, self.cmb_opname)

        # attributes
        self.layout_attributes = QtWidgets.QVBoxLayout()
        lbl_attributes = QtWidgets.QLabel("attributes")
        set_font(lbl_attributes, font_size=LARGE_FONT_SIZE, bold=True)
        self.layout_attributes.addWidget(lbl_attributes)
        self.visible_attributes_count = 3
        self.edit_attributes = {}
        for index in range(self._MAX_ATTRIBUTES_COUNT):
            self.edit_attributes[index] = {}
            self.edit_attributes[index]["base"] = QtWidgets.QWidget()
            self.edit_attributes[index]["layout"] = QtWidgets.QHBoxLayout(self.edit_attributes[index]["base"])
            self.edit_attributes[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.edit_attributes[index]["name"] = QtWidgets.QComboBox()
            self.edit_attributes[index]["name"].setEditable(True)
            self.edit_attributes[index]["name"].setFixedWidth(200)
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
        layout_btn_attributes = QtWidgets.QHBoxLayout()
        layout_btn_attributes.addWidget(self.btn_add_attributes)
        layout_btn_attributes.addWidget(self.btn_del_attributes)
        self.layout_attributes.addLayout(layout_btn_attributes)

        # input_const
        self.layout_const = QtWidgets.QVBoxLayout()
        lbl_input_constants = QtWidgets.QLabel("input_constants")
        set_font(lbl_input_constants, font_size=LARGE_FONT_SIZE, bold=True)
        self.layout_const.addWidget(lbl_input_constants)
        self.visible_const_count = 3
        self.edit_const = {}
        for index in range(self._MAX_CONST_COUNT):
            self.edit_const[index] = {}
            self.edit_const[index]["base"] = QtWidgets.QWidget()
            self.edit_const[index]["layout"] = QtWidgets.QHBoxLayout(self.edit_const[index]["base"])
            self.edit_const[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.edit_const[index]["name"] = QtWidgets.QComboBox()
            self.edit_const[index]["name"].setEditable(True)
            self.edit_const[index]["name"].setFixedWidth(200)
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
        layout_btn_const = QtWidgets.QHBoxLayout()
        layout_btn_const.addWidget(self.btn_add_const)
        layout_btn_const.addWidget(self.btn_del_const)
        self.layout_const.addLayout(layout_btn_const)

        # delete_attributes
        self.layout_delete_attributes = QtWidgets.QVBoxLayout()
        lbl_delete_attributes = QtWidgets.QLabel("delete_attributes")
        set_font(lbl_delete_attributes, font_size=LARGE_FONT_SIZE, bold=True)
        self.layout_delete_attributes.addWidget(lbl_delete_attributes)
        self.visible_delete_attributes_count = 3
        self.delete_attributes = {}
        for index in range(self._MAX_DELETE_ATTRIBUTES_COUNT):
            self.delete_attributes[index] = {}
            self.delete_attributes[index]["base"] = QtWidgets.QWidget()
            self.delete_attributes[index]["layout"] = QtWidgets.QHBoxLayout(self.delete_attributes[index]["base"])
            self.delete_attributes[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.delete_attributes[index]["name"] = QtWidgets.QComboBox()
            self.delete_attributes[index]["name"].setPlaceholderText("name")
            self.delete_attributes[index]["name"].setEditable(True)
            self.delete_attributes[index]["layout"].addWidget(self.delete_attributes[index]["name"])
            self.layout_delete_attributes.addWidget(self.delete_attributes[index]["base"])
        self.btn_add_delete_attributes = QtWidgets.QPushButton("+")
        self.btn_del_delete_attributes = QtWidgets.QPushButton("-")
        self.btn_add_delete_attributes.clicked.connect(self.btn_add_delete_attributes_clicked)
        self.btn_del_delete_attributes.clicked.connect(self.btn_del_delete_attributes_clicked)
        layout_btn_delete_attributes = QtWidgets.QHBoxLayout()
        layout_btn_delete_attributes.addWidget(self.btn_add_delete_attributes)
        layout_btn_delete_attributes.addWidget(self.btn_del_delete_attributes)
        self.layout_delete_attributes.addLayout(layout_btn_delete_attributes)

        # Dialog button
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)

        # add layout
        base_layout.addLayout(layout)
        base_layout.addSpacing(10)
        base_layout.addLayout(self.layout_attributes)
        base_layout.addSpacing(10)
        base_layout.addLayout(self.layout_const)
        base_layout.addSpacing(10)
        base_layout.addLayout(self.layout_delete_attributes)
        base_layout.addSpacing(10)
        base_layout.addWidget(btn)

        self.set_visible_attributes()
        self.set_visible_const()
        self.set_visible_delete_attributes()
        self.setLayout(base_layout)

    def updateUI(self, graph: OnnxGraph, selected_node: str=""):

        self.cmb_opname.clear()
        if self.graph:
            for op_name in self.graph.nodes.keys():
                self.cmb_opname.addItem(op_name)
        self.cmb_opname.setEditable(True)
        self.cmb_opname.setCurrentIndex(-1)

        if self.graph:
            def edit_attributes_name_currentIndexChanged(attr_index, current_index):
                op_name = self.cmb_opname.currentText()
                attr_name = self.edit_attributes[attr_index]["name"].currentText()
                attrs = self.graph.nodes[op_name].attrs
                if attr_name:
                    value = attrs[attr_name]
                    self.edit_attributes[attr_index]["value"].setText(str(value))
                    dtype = get_dtype_str(value)
                    self.edit_attributes[attr_index]["dtype"].setCurrentText(dtype)

            def edit_const_name_currentIndexChanged(attr_index, current_index):
                # op_name = self.cmb_opname.currentText()
                input_name = self.edit_const[attr_index]["name"].currentText()
                node_input = self.graph.node_inputs.get(input_name)
                if node_input:
                    self.edit_const[attr_index]["value"].setText(str(node_input.values))
                    dtype = get_dtype_str(node_input.values)
                    self.edit_const[attr_index]["dtype"].setCurrentText(dtype)

            def cmb_opname_currentIndexChanged(current_index):
                op_name = self.cmb_opname.currentText()

                for index in range(self._MAX_ATTRIBUTES_COUNT):
                    self.edit_attributes[index]["name"].clear()
                    for attr_name in self.graph.nodes[op_name].attrs.keys():
                        self.edit_attributes[index]["name"].addItem(attr_name)
                    self.edit_attributes[index]["name"].setCurrentIndex(-1)
                    def on_change(edit_attr_index):
                        def func(selected_index):
                            return edit_attributes_name_currentIndexChanged(edit_attr_index, selected_index)
                        return func
                    self.edit_attributes[index]["name"].currentIndexChanged.connect(on_change(index))
                    self.edit_attributes[index]["value"].setText("")

                for index in range(self._MAX_DELETE_ATTRIBUTES_COUNT):
                    self.delete_attributes[index]["name"].clear()
                    for attr_name in self.graph.nodes[op_name].attrs.keys():
                        self.delete_attributes[index]["name"].addItem(attr_name)
                    self.delete_attributes[index]["name"].setCurrentIndex(-1)

            for index in range(self._MAX_CONST_COUNT):
                self.edit_const[index]["name"].clear()
                for name, val in self.graph.node_inputs.items():
                    self.edit_const[index]["name"].addItem(name)
                self.edit_const[index]["name"].setCurrentIndex(-1)
                def on_change(edit_const_index):
                    def func(selected_index):
                        return edit_const_name_currentIndexChanged(edit_const_index, selected_index)
                    return func
                self.edit_const[index]["name"].currentIndexChanged.connect(on_change(index))
                self.edit_const[index]["value"].setText("")
            self.cmb_opname.currentIndexChanged.connect(cmb_opname_currentIndexChanged)

        if selected_node:
            if selected_node in self.graph.nodes.keys():
                self.cmb_opname.setCurrentText(selected_node)

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

    def set_visible_delete_attributes(self):
        for key, widgets in self.delete_attributes.items():
            widgets["base"].setVisible(key < self.visible_delete_attributes_count)
        if self.visible_delete_attributes_count == 1:
            self.btn_add_delete_attributes.setEnabled(True)
            self.btn_del_delete_attributes.setEnabled(False)
        elif self.visible_delete_attributes_count >= self._MAX_DELETE_ATTRIBUTES_COUNT:
            self.btn_add_delete_attributes.setEnabled(False)
            self.btn_del_delete_attributes.setEnabled(True)
        else:
            self.btn_add_delete_attributes.setEnabled(True)
            self.btn_del_delete_attributes.setEnabled(True)

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

    def btn_add_delete_attributes_clicked(self, e):
        self.visible_delete_attributes_count = min(max(0, self.visible_delete_attributes_count + 1), self._MAX_DELETE_ATTRIBUTES_COUNT)
        self.set_visible_delete_attributes()

    def btn_del_delete_attributes_clicked(self, e):
        self.visible_delete_attributes_count = min(max(0, self.visible_delete_attributes_count - 1), self._MAX_DELETE_ATTRIBUTES_COUNT)
        self.set_visible_delete_attributes()

    def get_properties(self)->ModifyAttrsProperties:
        opname = self.cmb_opname.currentText()

        attributes = {}
        for i in range(self.visible_attributes_count):
            name = self.edit_attributes[i]["name"].currentText()
            value = self.edit_attributes[i]["value"].text()
            dtype = self.edit_attributes[i]["dtype"].currentData()
            if name and value:
                if dtype == np.str_:
                    attributes[name] = value
                else:
                    value = literal_eval(value)
                    if isinstance(value, list):
                        attributes[name] = np.asarray(value, dtype=dtype)
                    else:
                        attributes[name] = value

        delete_attributes = []
        for i in range(self.visible_delete_attributes_count):
            name = self.delete_attributes[i]["name"].currentText()
            if name:
                delete_attributes.append(name)

        input_constants = {}
        for i in range(self.visible_const_count):
            name = self.edit_const[i]["name"].currentText()
            value = self.edit_const[i]["value"].text()
            dtype = self.edit_const[i]["dtype"].currentData()
            if name and value:
                value = literal_eval(value)
                input_constants[name] = np.asarray(value, dtype=dtype)

        return ModifyAttrsProperties(
            op_name=opname,
            attributes=attributes,
            input_constants=input_constants,
            delete_attributes=delete_attributes,
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        err_msgs = []
        edit_attr = len(props.attributes) > 0
        edit_const = len(props.input_constants) > 0
        delete_attr = len(props.delete_attributes) > 0
        if (not props.op_name and edit_attr) or (not props.op_name and delete_attr):
            err_msgs.append("- op_name and attributes must always be specified at the same time.")
            invalid = True
        if invalid:
            for m in err_msgs:
                print(m)
            MessageBox.error(err_msgs, "modify attrs", parent=self)
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