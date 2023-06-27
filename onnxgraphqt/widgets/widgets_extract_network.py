from collections import namedtuple
import signal
from PySide2 import QtCore, QtWidgets, QtGui

from onnxgraphqt.utils.widgets import set_font, BASE_FONT_SIZE, LARGE_FONT_SIZE
from onnxgraphqt.graph.onnx_node_graph import OnnxGraph
from onnxgraphqt.widgets.widgets_message_box import MessageBox


ExtractNetworkProperties = namedtuple("ExtractNetworkProperties",
    [
        "input_op_names",
        "output_op_names",
    ])

class ExtractNetworkWidgets(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 400
    _MAX_INPUT_OP_NAMES_COUNT = 5
    _MAX_OUTPUT_OP_NAMES_COUNT = 5

    def __init__(self, graph: OnnxGraph=None, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("extract network")
        self.graph = graph
        self.initUI()
        self.updateUI(self.graph)

    def initUI(self):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)
        set_font(self, font_size=BASE_FONT_SIZE)

        base_layout = QtWidgets.QVBoxLayout()

        # inputs
        self.layout_inputs = QtWidgets.QVBoxLayout()

        lbl_input_op_names = QtWidgets.QLabel("input_op_names")
        set_font(lbl_input_op_names, font_size=LARGE_FONT_SIZE, bold=True)

        self.layout_inputs.addWidget(lbl_input_op_names)

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

        lbl_output_op_names = QtWidgets.QLabel("output_op_names")
        set_font(lbl_output_op_names, font_size=LARGE_FONT_SIZE, bold=True)
        self.layout_outputs.addWidget(lbl_output_op_names)

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

        # Dialog button
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)

        # add layout
        base_layout.addLayout(self.layout_inputs)
        base_layout.addSpacing(10)
        base_layout.addLayout(self.layout_outputs)
        base_layout.addSpacing(10)
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


    def get_properties(self)->ExtractNetworkProperties:

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

        return ExtractNetworkProperties(
            input_op_names=inputs_op_names,
            output_op_names=outputs_op_names
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        err_msgs = []
        if len(props.input_op_names) == 0:
            err_msgs.append("- input_op_names is not set")
            invalid = True
        if len(props.output_op_names) == 0:
            err_msgs.append("- output_op_names is not set")
            invalid = True

        if invalid:
            for m in err_msgs:
                print(m)
            MessageBox.error(err_msgs, "extract network", parent=self)
            return
        return super().accept()



if __name__ == "__main__":
    import signal
    import os
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])
    window = ExtractNetworkWidgets()
    window.show()

    app.exec_()