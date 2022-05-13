from collections import namedtuple
from typing import List, Dict
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from ast import literal_eval

from onnx_node_graph import OnnxGraph
from utils.widgets import setFont

CombineGraphsProperties = namedtuple("CombineGraphsProperties",
    [
        "combine_with_current_graph",
        "srcop_destop",
        "op_prefixes_after_merging",
        "input_onnx_file_paths",
        "output_of_onnx_file_in_the_process_of_fusion",
    ])



class CombineGraphsWidgets(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 500
    _MAX_INPUTS_FILE = 3
    _MAX_OP_PREFIXES = _MAX_INPUTS_FILE + 1

    def __init__(self, graph: OnnxGraph=None, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("combine graphs")
        self.graph = graph
        self.initUI()
        # self.updateUI(self.graph)

    def initUI(self):
        self.resize(self.sizeHint())
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)

        base_layout = QtWidgets.QVBoxLayout()

        # src dst
        layout_srd_dst = QtWidgets.QFormLayout()
        lbl_src_dst = QtWidgets.QLabel("srcop_destop")
        setFont(lbl_src_dst, font_size=14, bold=True)
        self.src_op = QtWidgets.QTextEdit()
        self.src_op.setPlaceholderText(
            'e.g. ' + '["model1_out1_opname","model2_in1_opname"]'
        )
        self.dst_op = QtWidgets.QTextEdit()
        self.dst_op.setPlaceholderText(
            'e.g. ' + '["model1_out2_opname","model2_in2_opname"]'
        )
        layout_srd_dst.addRow("src_op", self.src_op)
        layout_srd_dst.addRow("dst_op", self.dst_op)

        # input_onnx_file_paths
        layout_inputs_file_paths = QtWidgets.QVBoxLayout()
        lbl_inputs = QtWidgets.QLabel("input_onnx_file_paths")
        setFont(lbl_inputs, font_size=14, bold=True)
        layout_inputs_file_paths.addWidget(lbl_inputs)

        self.tb_inputs_file_paths = {}
        for i in range(self._MAX_INPUTS_FILE):
            layout_inputs = QtWidgets.QHBoxLayout()
            lbl_inputs_file_path = QtWidgets.QLabel(f"file{i+1}")
            tb_inputs_file_path = QtWidgets.QLineEdit()
            btn_inputs_file_path = QtWidgets.QPushButton("select")
            # self.btn_inputs_file_path0.clicked.connect(self.btn_clicked)
            layout_inputs.addWidget(lbl_inputs_file_path)
            layout_inputs.addWidget(tb_inputs_file_path)
            layout_inputs.addWidget(btn_inputs_file_path)
            self.tb_inputs_file_paths[i] = tb_inputs_file_path
            layout_inputs_file_paths.addLayout(layout_inputs)
        self.combine_with_current_graph = QtWidgets.QCheckBox("combine_with_current_graph")
        self.combine_with_current_graph.setChecked(True)
        layout_inputs_file_paths.addWidget(self.combine_with_current_graph)
        layout_inputs_file_paths.setAlignment(self.combine_with_current_graph, QtCore.Qt.AlignRight)

        #
        layout_op_prefixes_base = QtWidgets.QVBoxLayout()
        lbl_op_prefixes = QtWidgets.QLabel("op_prefixes_after_merging")
        setFont(lbl_op_prefixes, font_size=14, bold=True)
        layout_op_prefixes_base.addWidget(lbl_op_prefixes)

        layout_op_prefixes = QtWidgets.QFormLayout()
        self.tb_op_prefixes = {}
        for i in range(self._MAX_OP_PREFIXES):
            if i == 0:
                label_op = QtWidgets.QLabel("current graph")
            else:
                label_op = QtWidgets.QLabel(f"file{i}")
            tb_op = QtWidgets.QLineEdit()
            self.tb_op_prefixes[i] = tb_op
            layout_op_prefixes.addRow(label_op, tb_op)
        layout_op_prefixes_base.addLayout(layout_op_prefixes)


        # 
        layout_output_in_process = QtWidgets.QVBoxLayout()
        self.output_in_process = QtWidgets.QCheckBox("output_of_onnx_file_in_the_process_of_fusion")
        self.output_in_process.setChecked(False)
        layout_output_in_process.addWidget(self.output_in_process)
        layout_output_in_process.setAlignment(self.output_in_process, QtCore.Qt.AlignRight)

        # add layout
        base_layout.addLayout(layout_srd_dst)
        base_layout.addLayout(layout_inputs_file_paths)
        base_layout.addLayout(layout_op_prefixes_base)
        base_layout.addLayout(layout_output_in_process)

        # Dialog button
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        # layout.addWidget(btn)
        base_layout.addWidget(btn)

        self.setLayout(base_layout)

    def updateUI(self, graph: OnnxGraph):

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

    def get_properties(self)->CombineGraphsProperties:
        combine_with_current_graph=self.combine_with_current_graph.isChecked()
        output_of_onnx_file_in_the_process_of_fusion=self.output_in_process.isChecked()

        src = self.src_op.toPlainText()
        dst = self.dst_op.toPlainText()
        src_dst = [
            literal_eval(src),
            literal_eval(dst),
        ]
        input_files = []
        for key, tb in self.tb_inputs_file_paths.items():
            file = tb.text().strip()
            if file:
                input_files.append(file)

        op_prefix = []
        for key, tb in self.tb_op_prefixes.items():
            prefix = tb.text().strip()
            if prefix:
                op_prefix.append(prefix)

        return CombineGraphsProperties(
            combine_with_current_graph=combine_with_current_graph,
            srcop_destop=src_dst,
            op_prefixes_after_merging=op_prefix,
            input_onnx_file_paths=input_files,
            output_of_onnx_file_in_the_process_of_fusion=output_of_onnx_file_in_the_process_of_fusion,
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        if len(props.srcop_destop) < 2:
            print("ERROR: Specify srcop_destop")
            invalid = True
        if len(props.input_onnx_file_paths) == 0:
            print("ERROR: Specify input_onnx_file_paths")
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
    window = CombineGraphsWidgets()
    window.show()

    app.exec_()