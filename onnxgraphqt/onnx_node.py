from dataclasses import dataclass
from typing import (
    Dict, List, Any, Optional, Union
)
from collections import OrderedDict

from NodeGraphQt import BaseNode
from NodeGraphQt.constants import (
    NODE_PROP_QLABEL,
    NODE_PROP_QLINEEDIT,
    NODE_PROP_QTEXTEDIT,
    NODE_PROP_QCOMBO,
    NODE_PROP_QCHECKBOX,
    NODE_PROP_QSPINBOX,
    NODE_PROP_COLORPICKER,
    NODE_PROP_SLIDER,
    NODE_PROP_FILE,
    NODE_PROP_FILE_SAVE,
    NODE_PROP_VECTOR2,
    NODE_PROP_VECTOR3,
    NODE_PROP_VECTOR4,
    NODE_PROP_FLOAT,
    NODE_PROP_INT,
    NODE_PROP_BUTTON,
)

from utils.color import (
    COLOR_BG,
    COLOR_FONT,
    COLOR_GRID,
    INPUT_NODE_COLOR,
    OUTPUT_NODE_COLOR,
    get_node_color,
    PrintColor,
)


@dataclass
class OnnxNodeIO:
    name: str
    dtype: str
    shape: List[int]
    values: List


class ONNXNode(BaseNode):
    # unique node identifier.
    __identifier__ = 'nodes.node'
    # initial default node name.
    NODE_NAME = 'onnxnode'

    def __init__(self):
        super(ONNXNode, self).__init__()
        self.attrs = OrderedDict()
        self.node_name = ""
        self.op = ""
        self.onnx_inputs = []
        self.onnx_outputs = []

        # create node inputs.
        self.add_input('multi in', multi_input=True)
        # create node outputs.
        self.add_output('multi out', multi_output=True)

    def set_attrs(self, attrs:OrderedDict):
        self.attrs = attrs
        for key, val in self.attrs.items():
            if self.has_property(key + "_"):
                self.set_property(key + "_", val)
            else:
                self.create_property(key + "_", val, widget_type=NODE_PROP_QLINEEDIT)

    def get_attrs(self)->OrderedDict:
        d = [(key, self.get_property(key + "_")) for key in self.attrs.keys()]
        return OrderedDict(d)

    def set_node_name(self, node_name:str):
        self.node_name = node_name
        if not self.has_property("node_name"):
            self.create_property("node_name", self.node_name, widget_type=NODE_PROP_QLINEEDIT)
        else:
            self.set_property("node_name", self.node_name)

    def set_op(self, op:str):
        self.op = op
        if not self.has_property("op"):
            self.create_property("op", self.op, widget_type=NODE_PROP_QLINEEDIT)
        else:
            self.set_property("op", self.op)

    def set_onnx_inputs(self, onnx_inputs:List[OnnxNodeIO]):
        self.onnx_inputs = onnx_inputs
        value = [[inp.name, inp.dtype, inp.shape, inp.values] for inp in self.onnx_inputs]
        if not self.has_property("inputs_"):
            self.create_property("inputs_", value, widget_type=NODE_PROP_QLINEEDIT)
        else:
            self.set_property("inputs_", value)

    def set_onnx_outputs(self, onnx_outputs:List[OnnxNodeIO]):
        self.onnx_outputs = onnx_outputs
        value = [[out.name, out.dtype, out.shape, out.values] for out in self.onnx_outputs]
        if not self.has_property("outputs_"):
            self.create_property("outputs_",  value, widget_type=NODE_PROP_QLINEEDIT)
        else:
            self.set_property("outputs_", value)

    def set_color(self):
        self.view.text_color = COLOR_FONT + [255]
        color = get_node_color(self.op)
        return super().set_color(*color)


class ONNXInput(BaseNode):
    # unique node identifier.
    __identifier__ = 'nodes.node'
    # initial default node name.
    NODE_NAME = 'input'
    def __init__(self):
        super(ONNXInput, self).__init__()
        self.shape = []
        self.dtype = ""
        self.output_names = []
        self.create_property("shape", self.shape, widget_type=NODE_PROP_QLINEEDIT)
        self.create_property("dtype", self.dtype, widget_type=NODE_PROP_QLINEEDIT)
        self.create_property("output_names", self.output_names, widget_type=NODE_PROP_QTEXTEDIT)
        # create node outputs.
        self.add_output('multi out', multi_output=True)
        self.set_color()

    def set_shape(self, shape):
        self.shape = shape
        self.set_property("shape", self.shape)

    def set_dtype(self, dtype):
        self.dtype = str(dtype)
        self.set_property("dtype", self.dtype)

    def set_output_names(self, output_names):
        self.output_names = output_names
        self.set_property("output_names", self.output_names)

    def set_color(self):
        self.view.text_color = COLOR_FONT + [255]
        return super().set_color(*INPUT_NODE_COLOR)


class ONNXOutput(BaseNode):
    # unique node identifier.
    __identifier__ = 'nodes.node'
    # initial default node name.
    NODE_NAME = 'output'
    def __init__(self):
        super(ONNXOutput, self).__init__()
        self.shape = []
        self.dtype:str = ""
        self.input_names = []
        self.create_property("shape", self.shape, widget_type=NODE_PROP_QLINEEDIT)
        self.create_property("dtype", self.dtype, widget_type=NODE_PROP_QLINEEDIT)
        self.create_property("input_names", self.input_names, widget_type=NODE_PROP_QTEXTEDIT)
        # create node inputs.
        self.add_input('multi in', multi_input=True)
        self.set_color()

    def set_shape(self, shape):
        self.shape = shape
        self.set_property("shape", self.shape)

    def set_dtype(self, dtype):
        self.dtype = str(dtype)
        self.set_property("dtype", self.dtype)

    def set_input_names(self, input_names):
        self.input_names = input_names
        self.set_property("input_names", self.input_names)

    def set_color(self):
        self.view.text_color = COLOR_FONT + [255]
        return super().set_color(*INPUT_NODE_COLOR)
