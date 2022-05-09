from collections import namedtuple
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from onnx_node_graph import OnnxGraph

ExtraNetworkProperties = namedtuple("ExtraNetworkProperties",
    [
        "input_op_names",
        "output_op_names",
    ])

class ExtraNetworkWidgets(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 400
    _MAX_INPUT_OP_NAMES_COUNT = 5
    _MAX_OUTPUT_OP_NAMES_COUNT = 5

    def __init__(self, graph: OnnxGraph=None, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("extra network")
        self.graph = graph
        self.initUI()
        self.updateUI(self.graph)

    def initUI(self):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)

        base_layout = QtWidgets.QVBoxLayout()

        # inputs
        self.layout_inputs = QtWidgets.QVBoxLayout()
        self.layout_inputs.addWidget(QtWidgets.QLabel("input_op_names"))
        self.visible_input_op_names_count = 1
        self.widgets_inputs = {}
        for index in range(self._MAX_INPUT_OP_NAMES_COUNT):
            self.widgets_inputs[index] = {}
            self.widgets_inputs[index]["base"] = QtWidgets.QWidget()
            self.widgets_inputs[index]["layout"] = QtWidgets.QHBoxLayout(self.widgets_inputs[index]["base"])
            self.widgets_inputs[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.widgets_inputs[index]["name"] = QtWidgets.QComboBox()
            self.widgets_inputs[index]["name"].setEditable(True)
            self.widgets_inputs[index]["layout"].addWidget(self.widgets_inputs[index]["name"])
            self.layout_inputs.addWidget(self.widgets_inputs[index]["base"])
        self.btn_add_inputs = QtWidgets.QPushButton("+")
        self.btn_del_inputs = QtWidgets.QPushButton("-")
        self.btn_add_inputs.clicked.connect(self.btn_add_inputs_clicked)
        self.btn_del_inputs.clicked.connect(self.btn_del_inputs_clicked)

        layout_btn_inputs = QtWidgets.QHBoxLayout()
        layout_btn_inputs.addWidget(self.btn_add_inputs)
        layout_btn_inputs.addWidget(self.btn_del_inputs)
        self.layout_inputs.addLayout(layout_btn_inputs)

        # outputs
        self.layout_outputs = QtWidgets.QVBoxLayout()
        self.layout_outputs.addWidget(QtWidgets.QLabel("input_op_names"))
        self.visible_output_op_names_count = 1
        self.widgets_outputs = {}
        for index in range(self._MAX_OUTPUT_OP_NAMES_COUNT):
            self.widgets_outputs[index] = {}
            self.widgets_outputs[index]["base"] = QtWidgets.QWidget()
            self.widgets_outputs[index]["layout"] = QtWidgets.QHBoxLayout(self.widgets_outputs[index]["base"])
            self.widgets_outputs[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.widgets_outputs[index]["name"] = QtWidgets.QComboBox()
            self.widgets_outputs[index]["name"].setEditable(True)
            self.widgets_outputs[index]["layout"].addWidget(self.widgets_outputs[index]["name"])
            self.layout_outputs.addWidget(self.widgets_outputs[index]["base"])
        self.btn_add_outputs = QtWidgets.QPushButton("+")
        self.btn_del_outputs = QtWidgets.QPushButton("-")
        self.btn_add_outputs.clicked.connect(self.btn_add_outputs_clicked)
        self.btn_del_outputs.clicked.connect(self.btn_del_outputs_clicked)

        layout_btn_outputs = QtWidgets.QHBoxLayout()
        layout_btn_outputs.addWidget(self.btn_add_outputs)
        layout_btn_outputs.addWidget(self.btn_del_outputs)
        self.layout_outputs.addLayout(layout_btn_outputs)

        # add layout
        base_layout.addLayout(self.layout_inputs)
        base_layout.addLayout(self.layout_outputs)

        # Dialog button
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        # layout.addWidget(btn)
        base_layout.addWidget(btn)

        self.setLayout(base_layout)

        self.set_btn_visible()

    def updateUI(self, graph: OnnxGraph=None):
        if graph:
            for index in range(self._MAX_INPUT_OP_NAMES_COUNT):
                self.widgets_inputs[index]["name"].clear()
                for name in graph.node_inputs.keys():
                    self.widgets_inputs[index]["name"].addItem(name)
                self.widgets_inputs[index]["name"].setCurrentIndex(-1)

            for index in range(self._MAX_OUTPUT_OP_NAMES_COUNT):
                self.widgets_outputs[index]["name"].clear()
                for name in graph.node_inputs.keys():
                    self.widgets_outputs[index]["name"].addItem(name)
                self.widgets_outputs[index]["name"].setCurrentIndex(-1)

    def set_btn_visible(self):
        for key, widgets in self.widgets_inputs.items():
            widgets["base"].setVisible(key < self.visible_input_op_names_count)
        for key, widgets in self.widgets_outputs.items():
            widgets["base"].setVisible(key < self.visible_output_op_names_count)

        if self.visible_input_op_names_count == 1:
            self.btn_add_inputs.setEnabled(True)
            self.btn_del_inputs.setEnabled(False)
        elif self.visible_input_op_names_count >= self._MAX_INPUT_OP_NAMES_COUNT:
            self.btn_add_inputs.setEnabled(False)
            self.btn_del_inputs.setEnabled(True)
        else:
            self.btn_add_inputs.setEnabled(True)
            self.btn_del_inputs.setEnabled(True)

        if self.visible_output_op_names_count == 1:
            self.btn_add_outputs.setEnabled(True)
            self.btn_del_outputs.setEnabled(False)
        elif self.visible_output_op_names_count >= self._MAX_OUTPUT_OP_NAMES_COUNT:
            self.btn_add_outputs.setEnabled(False)
            self.btn_del_outputs.setEnabled(True)
        else:
            self.btn_add_outputs.setEnabled(True)
            self.btn_del_outputs.setEnabled(True)

    def btn_add_inputs_clicked(self, e):
        self.visible_input_op_names_count = min(max(0, self.visible_input_op_names_count + 1), self._MAX_INPUT_OP_NAMES_COUNT)
        self.set_btn_visible()

    def btn_del_inputs_clicked(self, e):
        self.visible_input_op_names_count = min(max(0, self.visible_input_op_names_count - 1), self._MAX_INPUT_OP_NAMES_COUNT)
        self.set_btn_visible()

    def btn_add_outputs_clicked(self, e):
        self.visible_output_op_names_count = min(max(0, self.visible_output_op_names_count + 1), self._MAX_OUTPUT_OP_NAMES_COUNT)
        self.set_btn_visible()

    def btn_del_outputs_clicked(self, e):
        self.visible_output_op_names_count = min(max(0, self.visible_output_op_names_count - 1), self._MAX_OUTPUT_OP_NAMES_COUNT)
        self.set_btn_visible()


    def get_properties(self)->ExtraNetworkProperties:

        inputs_op_names = []
        for i in range(self.visible_input_op_names_count):
            name = self.widgets_inputs[i]["name"].currentText()
            if str.strip(name):
                inputs_op_names.append(name)

        outputs_op_names = []
        for i in range(self.visible_output_op_names_count):
            name = self.widgets_outputs[i]["name"].currentText()
            if str.strip(name):
                outputs_op_names.append(name)

        return ExtraNetworkProperties(
            input_op_names=inputs_op_names,
            output_op_names=outputs_op_names
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        if len(props.input_op_names) == 0:
            print("ERROR: input_op_names.")
            invalid = True
        if len(props.output_op_names) == 0:
            print("ERROR: output_op_names.")
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
    window = ExtraNetworkWidgets()
    window.show()

    app.exec_()