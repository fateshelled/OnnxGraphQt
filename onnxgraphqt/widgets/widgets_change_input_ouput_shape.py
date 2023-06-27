from collections import namedtuple
import signal
from PySide2 import QtCore, QtWidgets, QtGui
import os
from ast import literal_eval

from onnxgraphqt.graph.onnx_node_graph import OnnxGraph
from onnxgraphqt.utils.widgets import set_font, BASE_FONT_SIZE, LARGE_FONT_SIZE
from onnxgraphqt.widgets.widgets_message_box import MessageBox


ChangeInputOutputShapeProperties = namedtuple("ChangeInputOutputShapeProperties",
    [
        "input_names",
        "input_shapes",
        "output_names",
        "output_shapes",
    ])


class ChangeInputOutputShapeWidget(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 500

    def __init__(self, graph: OnnxGraph=None, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("change input output shape")
        self.graph = graph
        self.initUI(graph)

    def initUI(self, graph: OnnxGraph=None):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)
        set_font(self, font_size=BASE_FONT_SIZE)

        base_layout = QtWidgets.QVBoxLayout()

        # layout
        layout = QtWidgets.QVBoxLayout()

        label_input_header = QtWidgets.QLabel("Inputs")
        set_font(label_input_header, font_size=LARGE_FONT_SIZE, bold=True)
        self.cb_change_input_shape = QtWidgets.QCheckBox("change input shape")
        self.cb_change_input_shape.setChecked(True)
        self.cb_change_input_shape.stateChanged.connect(self.cb_change_input_shape_changed)
        layout.addWidget(label_input_header)
        layout.addWidget(self.cb_change_input_shape)

        self.input_widgets = {}
        for name in graph.inputs.keys():
            input = graph.inputs[name]
            shape = input.get_shape()

            self.input_widgets[name] = {}
            self.input_widgets[name]["label"] = QtWidgets.QLabel(name)
            self.input_widgets[name]["shape"] = QtWidgets.QLineEdit()
            self.input_widgets[name]["shape"].setText(str(shape))
            child_layout = QtWidgets.QHBoxLayout()
            child_layout.addWidget(self.input_widgets[name]["label"])
            child_layout.addWidget(QtWidgets.QLabel(f": "))
            child_layout.addWidget(self.input_widgets[name]["shape"])
            layout.addLayout(child_layout)

        layout.addSpacing(15)

        label_output_header = QtWidgets.QLabel("Outputs")
        set_font(label_output_header, font_size=LARGE_FONT_SIZE, bold=True)
        self.cb_change_output_shape = QtWidgets.QCheckBox("change output shape")
        self.cb_change_output_shape.setChecked(True)
        self.cb_change_output_shape.stateChanged.connect(self.cb_change_output_shape_changed)
        layout.addWidget(label_output_header)
        layout.addWidget(self.cb_change_output_shape)

        self.output_widgets = {}
        for name in graph.outputs.keys():
            output = graph.outputs[name]
            shape = output.get_shape()

            self.output_widgets[name] = {}
            self.output_widgets[name]["label"] = QtWidgets.QLabel(name)
            self.output_widgets[name]["shape"] = QtWidgets.QLineEdit()
            self.output_widgets[name]["shape"].setText(str(shape))
            child_layout = QtWidgets.QHBoxLayout()
            child_layout.addWidget(self.output_widgets[name]["label"])
            child_layout.addWidget(QtWidgets.QLabel(f": "))
            child_layout.addWidget(self.output_widgets[name]["shape"])
            layout.addLayout(child_layout)

        # add layout
        base_layout.addLayout(layout)

        # Dialog button
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        # layout.addWidget(btn)
        base_layout.addWidget(btn)

        self.setLayout(base_layout)

    def cb_change_input_shape_changed(self, e):
        change = self.cb_change_input_shape.isChecked()
        for widgets in self.input_widgets.values():
            widgets["shape"].setEnabled(change)

    def cb_change_output_shape_changed(self, e):
        change = self.cb_change_output_shape.isChecked()
        for widgets in self.output_widgets.values():
            widgets["shape"].setEnabled(change)

    def get_properties(self)->ChangeInputOutputShapeProperties:
        input_names = None
        input_shapes = None
        output_names = None
        output_shapes = None
        errors = []

        if self.cb_change_input_shape.isChecked():
            input_names = []
            input_shapes = []
            for widgets in self.input_widgets.values():
                name = widgets["label"].text()
                str_shape = widgets["shape"].text().strip()
                if str_shape == "":
                    errors.append(f"{name}: not entered")
                    continue
                try:
                    shape = literal_eval(str_shape)
                except BaseException as e:
                    print(e)
                    errors.append(f"{name}: {str(e)}")
                    continue
                input_names.append(name)
                input_shapes.append(shape)

        if self.cb_change_output_shape.isChecked():
            output_names = []
            output_shapes = []
            for widgets in self.output_widgets.values():
                name = widgets["label"].text()
                str_shape = widgets["shape"].text().strip()
                if str_shape == "":
                    errors.append(f"{name}: not entered")
                    continue
                try:
                    shape = literal_eval(str_shape)
                except BaseException as e:
                    print(e)
                    errors.append(f"{name}: {e}")
                    continue
                output_names.append(name)
                output_shapes.append(shape)

        return ChangeInputOutputShapeProperties(
            input_names=input_names,
            input_shapes=input_shapes,
            output_names=output_names,
            output_shapes=output_shapes,
        ), errors

    def accept(self) -> None:
        # value check
        invalid = False
        props, errors = self.get_properties()
        print(props)
        if len(errors) > 0:
            err_msgs = ["shape convert error"]
            err_msgs += errors
            invalid = True
        else:
            err_msgs = []
            if props.input_names is None and props.output_names is None:
                err_msgs.append("input shape or output shape must be change.")
                invalid = True
            if props.input_names is not None and len(props.input_names) != len(self.graph.inputs):
                err_msgs.append("input shape.")
                invalid = True
            if props.output_names is not None and len(props.output_names) != len(self.graph.outputs):
                err_msgs.append("input shape or output shape must be change.")
                invalid = True

        if invalid:
            for m in err_msgs:
                print(m)
            MessageBox.error(err_msgs, "change input output shape", parent=self)
            return
        return super().accept()


if __name__ == "__main__":
    import signal
    import os
    import onnx
    import onnx_graphsurgeon as gs
    from onnxgraphqt.graph.onnx_node_graph import ONNXNodeGraph
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])
    model_path = os.path.join(os.path.dirname(__file__), "../data/mobilenetv2-7.onnx")
    onnx_model = onnx.load(model_path)
    onnx_graph = gs.import_onnx(onnx_model)
    graph = ONNXNodeGraph(name=onnx_graph.name,
                          opset=onnx_graph.opset,
                          doc_string=onnx_graph.doc_string,
                          import_domains=onnx_graph.import_domains,
                          producer_name=onnx_model.producer_name,
                          producer_version=onnx_model.producer_version,
                          ir_version=onnx_model.ir_version,
                          model_version=onnx_model.model_version)
    graph.load_onnx_graph(onnx_graph,)
    window = ChangeInputOutputShapeWidget(graph.to_data())
    window.show()

    app.exec_()