from collections import namedtuple
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from ast import literal_eval

from onnxgraphqt.graph.onnx_node_graph import OnnxGraph
from onnxgraphqt.widgets.widgets_message_box import MessageBox
from onnxgraphqt.utils.widgets import set_font, BASE_FONT_SIZE, LARGE_FONT_SIZE


ChangeChannelProperties = namedtuple("ChangeChannelProperties",
    [
        "input_op_names_and_order_dims",
        "channel_change_inputs",
    ])


class ChangeChannelWidgets(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 300
    _QLINE_EDIT_WIDTH = 170

    def __init__(self, graph: OnnxGraph=None, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("change channel")
        self.graph = graph

        if graph:
            self._MAX_CHANGE_ORDER_DIM_INPUTS_COUNT = len(self.graph.inputs)
            self._MAX_CHANNEL_CHANGE_INPUTS_COUNT = len(self.graph.inputs)
        else:
            self._MAX_CHANGE_ORDER_DIM_INPUTS_COUNT = 4
            self._MAX_CHANNEL_CHANGE_INPUTS_COUNT = 4
        self.initUI()
        self.updateUI(self.graph)

    def initUI(self):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)
        set_font(self, font_size=BASE_FONT_SIZE)

        base_layout = QtWidgets.QVBoxLayout()
        base_layout.setSizeConstraint(base_layout.SizeConstraint.SetFixedSize)

        self.layout_order_dims = QtWidgets.QVBoxLayout()
        self.layout_change_channel = QtWidgets.QVBoxLayout()
        self.visible_change_order_dim_inputs_count = self._MAX_CHANGE_ORDER_DIM_INPUTS_COUNT
        self.visible_channel_change_inputs_count = self._MAX_CHANNEL_CHANGE_INPUTS_COUNT

        self.input_op_names_and_order_dims = {} # transpose NCHW <-> NHWC
        self.channel_change_inputs = {}         # RGB <-> BGR
        self.create_order_dims_widgets()
        self.create_channel_change_widgets()

        lbl_channel_change = QtWidgets.QLabel("channel_change_inputs")
        lbl_channel_change.setToolTip('Change the channel order of RGB and BGR.' +
                                      'If the original model is RGB, it is transposed to BGR.' +
                                      'If the original model is BGR, it is transposed to RGB.' +
                                      'It can be selectively specified from among the OP names' +
                                      'specified in input_op_names_and_order_dims.' +
                                      'OP names not specified in input_op_names_and_order_dims are ignored.' +
                                      'Multiple times can be specified as many times as the number' +
                                      'of OP names specified in input_op_names_and_order_dims.' +
                                      'channel_change_inputs = {"op_name": dimension_number_representing_the_channel}' +
                                      'dimension_number_representing_the_channel must specify' +
                                      'the dimension position after the change in input_op_names_and_order_dims.' +
                                      'For example, dimension_number_representing_the_channel is 1 for NCHW and 3 for NHWC.')
        set_font(lbl_channel_change, font_size=LARGE_FONT_SIZE, bold=True)
        self.layout_change_channel.addWidget(lbl_channel_change)
        for i in range(self._MAX_CHANGE_ORDER_DIM_INPUTS_COUNT):
            self.layout_change_channel.addWidget(self.channel_change_inputs[i]["base"])

        lbl_order_dims = QtWidgets.QLabel("input_op_names_and_order_dims")
        lbl_order_dims.setToolTip("Specify the name of the input_op to be dimensionally changed and\n" + 
                                  "the order of the dimensions after the change.\n" + 
                                  "The name of the input_op to be dimensionally changed\n" +
                                  "can be specified multiple times.")
        set_font(lbl_order_dims, font_size=LARGE_FONT_SIZE, bold=True)
        self.layout_order_dims.addWidget(lbl_order_dims)
        for i in range(self._MAX_CHANNEL_CHANGE_INPUTS_COUNT):
            self.layout_order_dims.addWidget(self.input_op_names_and_order_dims[i]["base"])

        # add button
        self.btn_add_order_dims = QtWidgets.QPushButton("+")
        self.btn_del_order_dims = QtWidgets.QPushButton("-")
        self.btn_add_order_dims.clicked.connect(self.btn_add_order_dims_clicked)
        self.btn_del_order_dims.clicked.connect(self.btn_del_order_dims_clicked)
        self.layout_btn_order_dims = QtWidgets.QHBoxLayout()
        self.layout_btn_order_dims.addWidget(self.btn_add_order_dims)
        self.layout_btn_order_dims.addWidget(self.btn_del_order_dims)

        self.btn_add_channel_change = QtWidgets.QPushButton("+")
        self.btn_del_channel_change = QtWidgets.QPushButton("-")
        self.btn_add_channel_change.clicked.connect(self.btn_add_channel_change_clicked)
        self.btn_del_channel_change.clicked.connect(self.btn_del_channel_change_clicked)
        self.layout_btn_channel_change = QtWidgets.QHBoxLayout()
        self.layout_btn_channel_change.addWidget(self.btn_add_channel_change)
        self.layout_btn_channel_change.addWidget(self.btn_del_channel_change)

        self.layout_order_dims.addLayout(self.layout_btn_order_dims)
        self.layout_change_channel.addLayout(self.layout_btn_channel_change)

        # add layout
        base_layout.addLayout(self.layout_order_dims)
        base_layout.addSpacing(15)
        base_layout.addLayout(self.layout_change_channel)

        # Dialog button
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        # layout.addWidget(btn)
        base_layout.addWidget(btn)

        self.setLayout(base_layout)
        self.set_visible_order_dims()
        self.set_visible_channel_change()

    def updateUI(self, graph: OnnxGraph):
        if graph:
            for index in range(self._MAX_CHANGE_ORDER_DIM_INPUTS_COUNT):
                self.input_op_names_and_order_dims[index]["name"].clear()
                for name, input_node in graph.inputs.items():
                    self.input_op_names_and_order_dims[index]["name"].addItem(name)
                self.input_op_names_and_order_dims[index]["name"].setCurrentIndex(index)

            for index in range(self._MAX_CHANNEL_CHANGE_INPUTS_COUNT):
                self.channel_change_inputs[index]["name"].clear()
                for name, input_node in graph.inputs.items():
                    self.channel_change_inputs[index]["name"].addItem(name)
                self.channel_change_inputs[index]["name"].setCurrentIndex(index)
        self.set_visible_order_dims()
        self.set_visible_channel_change()

    def btn_add_order_dims_clicked(self, e):
        self.visible_change_order_dim_inputs_count = min(max(0, self.visible_change_order_dim_inputs_count + 1), self._MAX_CHANGE_ORDER_DIM_INPUTS_COUNT)
        self.set_visible_order_dims()

    def btn_del_order_dims_clicked(self, e):
        self.visible_change_order_dim_inputs_count = min(max(0, self.visible_change_order_dim_inputs_count - 1), self._MAX_CHANGE_ORDER_DIM_INPUTS_COUNT)
        self.set_visible_order_dims()

    def btn_add_channel_change_clicked(self, e):
        self.visible_channel_change_inputs_count = min(max(0, self.visible_channel_change_inputs_count + 1), self._MAX_CHANNEL_CHANGE_INPUTS_COUNT)
        self.set_visible_channel_change()

    def btn_del_channel_change_clicked(self, e):
        self.visible_channel_change_inputs_count = min(max(0, self.visible_channel_change_inputs_count - 1), self._MAX_CHANNEL_CHANGE_INPUTS_COUNT)
        self.set_visible_channel_change()

    def create_order_dims_widgets(self):
        for index in range(self._MAX_CHANGE_ORDER_DIM_INPUTS_COUNT):
            self.input_op_names_and_order_dims[index] = {}
            self.input_op_names_and_order_dims[index]["base"] = QtWidgets.QWidget()
            self.input_op_names_and_order_dims[index]["layout"] = QtWidgets.QHBoxLayout(self.input_op_names_and_order_dims[index]["base"])
            self.input_op_names_and_order_dims[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.input_op_names_and_order_dims[index]["name"] = QtWidgets.QComboBox()
            self.input_op_names_and_order_dims[index]["name"].setEditable(True)
            self.input_op_names_and_order_dims[index]["name"].setFixedWidth(self._QLINE_EDIT_WIDTH)
            self.input_op_names_and_order_dims[index]["value"] = QtWidgets.QLineEdit()
            self.input_op_names_and_order_dims[index]["value"].setPlaceholderText("List of dims.")
            self.input_op_names_and_order_dims[index]["layout"].addWidget(self.input_op_names_and_order_dims[index]["name"])
            self.input_op_names_and_order_dims[index]["layout"].addWidget(self.input_op_names_and_order_dims[index]["value"])

    def create_channel_change_widgets(self):
        for index in range(self._MAX_CHANNEL_CHANGE_INPUTS_COUNT):
            self.channel_change_inputs[index] = {}
            self.channel_change_inputs[index]["base"] = QtWidgets.QWidget()
            self.channel_change_inputs[index]["layout"] = QtWidgets.QHBoxLayout(self.channel_change_inputs[index]["base"])
            self.channel_change_inputs[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.channel_change_inputs[index]["name"] = QtWidgets.QComboBox()
            self.channel_change_inputs[index]["name"].setEditable(True)
            self.channel_change_inputs[index]["name"].setFixedWidth(self._QLINE_EDIT_WIDTH)
            self.channel_change_inputs[index]["value"] = QtWidgets.QLineEdit()
            self.channel_change_inputs[index]["value"].setPlaceholderText("dim")
            self.channel_change_inputs[index]["layout"].addWidget(self.channel_change_inputs[index]["name"])
            self.channel_change_inputs[index]["layout"].addWidget(self.channel_change_inputs[index]["value"])

    def set_visible_order_dims(self):
        for key, widgets in self.input_op_names_and_order_dims.items():
            widgets["base"].setVisible(key < self.visible_change_order_dim_inputs_count)
        if self._MAX_CHANGE_ORDER_DIM_INPUTS_COUNT == 1:
            self.btn_add_order_dims.setEnabled(False)
            self.btn_del_order_dims.setEnabled(False)
        elif self.visible_change_order_dim_inputs_count == 1:
            self.btn_add_order_dims.setEnabled(True)
            self.btn_del_order_dims.setEnabled(False)
        elif self.visible_change_order_dim_inputs_count >= self._MAX_CHANGE_ORDER_DIM_INPUTS_COUNT:
            self.btn_add_order_dims.setEnabled(False)
            self.btn_del_order_dims.setEnabled(True)
        else:
            self.btn_add_order_dims.setEnabled(True)
            self.btn_del_order_dims.setEnabled(True)

    def set_visible_channel_change(self):
        for key, widgets in self.channel_change_inputs.items():
            widgets["base"].setVisible(key < self.visible_channel_change_inputs_count)
        if self._MAX_CHANNEL_CHANGE_INPUTS_COUNT == 1:
            self.btn_add_channel_change.setEnabled(False)
            self.btn_del_channel_change.setEnabled(False)
        elif self.visible_channel_change_inputs_count == 1:
            self.btn_add_channel_change.setEnabled(True)
            self.btn_del_channel_change.setEnabled(False)
        elif self.visible_channel_change_inputs_count >= self._MAX_CHANNEL_CHANGE_INPUTS_COUNT:
            self.btn_add_channel_change.setEnabled(False)
            self.btn_del_channel_change.setEnabled(True)
        else:
            self.btn_add_channel_change.setEnabled(True)
            self.btn_del_channel_change.setEnabled(True)


    def get_properties(self)->ChangeChannelProperties:
        input_op_names_and_order_dims = {}
        for i in range(self.visible_change_order_dim_inputs_count):
            name = self.input_op_names_and_order_dims[i]["name"].currentText()
            value = self.input_op_names_and_order_dims[i]["value"].text()
            if name and value:
                input_op_names_and_order_dims[name] = literal_eval(value)
        channel_change_inputs = {}
        for i in range(self.visible_channel_change_inputs_count):
            name = self.channel_change_inputs[i]["name"].currentText()
            value = self.channel_change_inputs[i]["value"].text()
            if name and value:
                channel_change_inputs[name] = literal_eval(value)
        return ChangeChannelProperties(
            input_op_names_and_order_dims=input_op_names_and_order_dims,
            channel_change_inputs=channel_change_inputs,
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        err_msgs = []
        if len(props.channel_change_inputs) < 1 and len(props.input_op_names_and_order_dims) < 1:
            err_msgs.append("At least one of input_op_names_and_order_dims or channel_change_inputs must be specified.")
            invalid = True

        for key, val in props.channel_change_inputs.items():
            if type(val) is not int:
                err_msgs.append(f'channel_change_inputs value must be integer. {key}: {val}')
                invalid = True

        if invalid:
            for m in err_msgs:
                print(m)
            MessageBox.error(err_msgs, "change channel", parent=self)
            return
        return super().accept()



if __name__ == "__main__":
    import signal
    import os
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])
    window = ChangeChannelWidgets()
    window.show()

    app.exec_()