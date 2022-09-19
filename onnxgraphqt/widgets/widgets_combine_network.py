from collections import namedtuple
from typing import List, Dict
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from ast import literal_eval

import sys, os

from ..graph.onnx_node_graph import OnnxGraph
from ..utils.widgets import BASE_FONT_SIZE, LARGE_FONT_SIZE, set_font
from .widgets_message_box import MessageBox

CombineNetworkProperties = namedtuple("CombineNetworkProperties",
    [
        "combine_with_current_graph",
        "srcop_destop",
        "op_prefixes_after_merging",
        "input_onnx_file_paths",
        "output_of_onnx_file_in_the_process_of_fusion",
    ])


class CombineNetworkWidgets(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 560
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
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)
        set_font(self, font_size=BASE_FONT_SIZE)

        base_layout = QtWidgets.QVBoxLayout()

        # src dst
        layout_src_dst = QtWidgets.QFormLayout()
        lbl_src_dst = QtWidgets.QLabel("srcop_destop")
        set_font(lbl_src_dst, font_size=LARGE_FONT_SIZE, bold=True)
        self.src_op_dst_op = QtWidgets.QTextEdit()
        self.src_op_dst_op.setMinimumHeight(20*7)
        self.src_op_dst_op.setPlaceholderText(
            'e.g. '+ '\n' + \
            '    [' + '\n' + \
            '        [' + '\n' + \
            '            "model1_out1_opname","model2_in1_opname",' + '\n' + \
            '            "model1_out2_opname","model2_in2_opname",' + '\n' + \
            '        ],' + '\n' + \
            '    ]'
        )
        layout_src_dst.addRow(lbl_src_dst, self.src_op_dst_op)

        # input_onnx_file_paths
        layout_inputs_file_paths = QtWidgets.QVBoxLayout()
        lbl_inputs = QtWidgets.QLabel("input_onnx_file_paths")
        set_font(lbl_inputs, font_size=LARGE_FONT_SIZE, bold=True)
        layout_inputs_file_paths.addWidget(lbl_inputs)

        self.inputs_file_paths = {}
        for index in range(self._MAX_INPUTS_FILE):
            self.inputs_file_paths[index] = {}
            self.inputs_file_paths[index]["base"] = QtWidgets.QWidget()
            self.inputs_file_paths[index]["layout"] = QtWidgets.QHBoxLayout(self.inputs_file_paths[index]["base"])
            self.inputs_file_paths[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.inputs_file_paths[index]["label"] = QtWidgets.QLabel(f"file{index+1}")
            self.inputs_file_paths[index]["value"] = QtWidgets.QLineEdit()
            self.inputs_file_paths[index]["button"] = QtWidgets.QPushButton("select")
            self.inputs_file_paths[index]["button"].setObjectName(f"button{index}")

            def clicked(index):
                def func(e:bool):
                    return self.btn_inputs_file_path_clicked(index, e)
                return func

            self.inputs_file_paths[index]["button"].clicked.connect(clicked(index))

            self.inputs_file_paths[index]["layout"].addWidget(self.inputs_file_paths[index]["label"])
            self.inputs_file_paths[index]["layout"].addWidget(self.inputs_file_paths[index]["value"])
            self.inputs_file_paths[index]["layout"].addWidget(self.inputs_file_paths[index]["button"])
            layout_inputs_file_paths.addWidget(self.inputs_file_paths[index]["base"])

        self.combine_with_current_graph = QtWidgets.QCheckBox("combine_with_current_graph")
        if self.graph is not None and len(self.graph.nodes) > 0:
            self.combine_with_current_graph.setChecked(True)
        else:
            self.combine_with_current_graph.setChecked(False)
            self.combine_with_current_graph.setEnabled(False)
        self.combine_with_current_graph.clicked.connect(self.combine_with_current_graph_clicked)
        layout_inputs_file_paths.addWidget(self.combine_with_current_graph)
        layout_inputs_file_paths.setAlignment(self.combine_with_current_graph, QtCore.Qt.AlignRight)

        #
        layout_op_prefixes_base = QtWidgets.QVBoxLayout()
        lbl_op_prefixes = QtWidgets.QLabel("op_prefixes_after_merging")
        set_font(lbl_op_prefixes, font_size=LARGE_FONT_SIZE, bold=True)
        layout_op_prefixes_base.addWidget(lbl_op_prefixes)

        layout_op_prefixes = QtWidgets.QFormLayout()
        self.op_prefixes = {}
        for index in range(self._MAX_OP_PREFIXES):
            self.op_prefixes[index] = {}
            label = f"file{index}" if index > 0 else "current graph"
            self.op_prefixes[index]["label"] = QtWidgets.QLabel(label)
            self.op_prefixes[index]["value"] = QtWidgets.QLineEdit()
            layout_op_prefixes.addRow(self.op_prefixes[index]["label"], self.op_prefixes[index]["value"])
        if self.graph is not None and len(self.graph.nodes) == 0:
            self.op_prefixes[0]["label"].setVisible(False)
            self.op_prefixes[0]["value"].setVisible(False)
        layout_op_prefixes_base.addLayout(layout_op_prefixes)


        #
        layout_output_in_process = QtWidgets.QVBoxLayout()
        self.output_in_process = QtWidgets.QCheckBox("output_of_onnx_file_in_the_process_of_fusion")
        self.output_in_process.setChecked(False)
        layout_output_in_process.addWidget(self.output_in_process)
        layout_output_in_process.setAlignment(self.output_in_process, QtCore.Qt.AlignRight)

        # add layout
        base_layout.addLayout(layout_src_dst)
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

    def btn_inputs_file_path_clicked(self, index:int, e:bool):

        file_name, filter = QtWidgets.QFileDialog.getOpenFileName(
                            self,
                            caption=f"Open ONNX Model File({index+1})",
                            # directory=os.path.abspath(os.curdir),
                            filter="*.onnx *.json")
        if not file_name:
            return
        self.inputs_file_paths[index]["value"].setText(file_name)
        print(file_name)

    def combine_with_current_graph_clicked(self, e:bool):
        checked = self.combine_with_current_graph.isChecked()
        self.op_prefixes[0]["label"].setVisible(checked)
        self.op_prefixes[0]["value"].setVisible(checked)

    def get_properties(self)->CombineNetworkProperties:
        combine_with_current_graph=self.combine_with_current_graph.isChecked()
        output_of_onnx_file_in_the_process_of_fusion=self.output_in_process.isChecked()

        srcop_destop = []
        srt_op = self.src_op_dst_op.toPlainText()
        if srt_op:
            srcop_destop = literal_eval(srt_op)

        input_files = []
        for index, widgets in self.inputs_file_paths.items():
            file = widgets["value"].text().strip()
            if file:
                input_files.append(file)

        op_prefix = []
        for index, widgets in self.op_prefixes.items():
            if combine_with_current_graph is False and index == 0:
                continue
            prefix = widgets["value"].text().strip()
            if prefix:
                op_prefix.append(prefix)
        if len(op_prefix) == 0:
            op_prefix = None

        return CombineNetworkProperties(
            combine_with_current_graph=combine_with_current_graph,
            srcop_destop=srcop_destop,
            op_prefixes_after_merging=op_prefix,
            input_onnx_file_paths=input_files,
            output_of_onnx_file_in_the_process_of_fusion=output_of_onnx_file_in_the_process_of_fusion,
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        err_msgs = []
        if len(props.input_onnx_file_paths) == 0:
            err_msgs.append("- input_onnx_file_paths must be specified")
            invalid = True
        if props.combine_with_current_graph:
            if len(props.srcop_destop) != len(props.input_onnx_file_paths):
                err_msgs.append("- The number of srcop_destops must be (number of input_onnx_file_paths + 1).")
                invalid = True
            if props.op_prefixes_after_merging:
                if len(props.input_onnx_file_paths) + 1 != len(props.op_prefixes_after_merging):
                    err_msgs.append("- The number of op_prefixes_after_merging must match (number of input_onnx_file_paths + 1).")
                    invalid = True
        else:
            if len(props.srcop_destop) != len(props.input_onnx_file_paths)-1:
                err_msgs.append("- The number of srcop_destop must match the number of input_onnx_file_paths.")
                invalid = True
            if props.op_prefixes_after_merging:
                if len(props.input_onnx_file_paths) != len(props.op_prefixes_after_merging):
                    err_msgs.append("- The number of op_prefixes_after_merging must match number of input_onnx_file_paths.")
                    invalid = True

        if invalid:
            for m in err_msgs:
                print(m)
            MessageBox.error(err_msgs, "combine network", parent=self)
            return
        return super().accept()



if __name__ == "__main__":
    import signal
    import os
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])
    window = CombineNetworkWidgets()
    window.show()

    app.exec_()
