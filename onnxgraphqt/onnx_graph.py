from typing import (
    Dict, List, Any, Optional
)
from collections import namedtuple, OrderedDict
import copy

import numpy as np
import onnx
import onnx_graphsurgeon as gs
import networkx as nx

from NodeGraphQt.constants import (
    NODE_LAYOUT_HORIZONTAL,
    NODE_LAYOUT_VERTICAL,
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

    VIEWER_GRID_NONE,
    VIEWER_GRID_DOTS,
    VIEWER_GRID_LINES,
)
from NodeGraphQt.base import node, graph
from NodeGraphQt.qgraphics import pipe
node.NODE_LAYOUT_DIRECTION = NODE_LAYOUT_VERTICAL
graph.NODE_LAYOUT_DIRECTION = NODE_LAYOUT_VERTICAL
pipe.NODE_LAYOUT_DIRECTION = NODE_LAYOUT_VERTICAL

from NodeGraphQt import NodeGraph, BaseNode
from NodeGraphQt.base.node import NodeObject

from utils.color import (
    COLOR_BG,
    COLOR_FONT,
    COLOR_GRID,
    INPUT_NODE_COLOR,
    OUTPUT_NODE_COLOR,
    get_node_color,
    PrintColor,
)
from utils.dtype import (
    DTYPES_TO_NUMPY_TYPES,
)

ONNX_IO = namedtuple("ONNX_IO", ["name", "dtype", "shape", "values"])

class ONNXNode(BaseNode):
    # unique node identifier.
    __identifier__ = 'nodes.node'
    # initial default node name.
    NODE_NAME = 'onnxnode'

    def __init__(self):
        super(ONNXNode, self).__init__()
        self.attrs = OrderedDict()
        self.op = ""
        self.onnx_inputs = []
        self.onnx_outputs = []

        # add property for visualize and serialize.
        self.create_property("op", self.op, widget_type=NODE_PROP_QLABEL)
        self.create_property("inputs_", self.onnx_inputs, widget_type=NODE_PROP_QLINEEDIT)
        self.create_property("outputs_", self.onnx_outputs, widget_type=NODE_PROP_QLINEEDIT)

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

    def set_op(self, op:str):
        self.op = op
        self.set_property("op", self.op)

    def set_onnx_inputs(self, onnx_inputs:List[ONNX_IO]):
        self.onnx_inputs = onnx_inputs
        self.set_property("inputs_", [[n, d, s, v] for n, d, s, v in self.onnx_inputs])
        # for i, (name, dtype, shape, values) in enumerate(self.onnx_inputs):
        #     prop_name = f"inputs_{i}"
        #     if self.has_property(prop_name):
        #         if dtype:
        #             self.set_property(prop_name, name)
        #         else:
        #             self.set_property(prop_name, name)
        #     else:
        #         self.create_property(prop_name, name, widget_type=NODE_PROP_QLABEL)

    def set_onnx_outputs(self, onnx_outputs:List[ONNX_IO]):
        self.onnx_outputs = onnx_outputs
        self.set_property("outputs_", [[n, d, s, v] for n, d, s, v in self.onnx_outputs])

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


class ONNXNodeGraph(NodeGraph):
    def __init__(self, name:str, opset:int, doc_string:str, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.name = name
        self.opset = opset
        self.doc_string = doc_string
        self.register_nodes([
            ONNXNode,
            ONNXInput,
            ONNXOutput,
        ])
        self.set_background_color(*COLOR_BG)
        self.set_grid_mode(VIEWER_GRID_DOTS)
        self.set_grid_color(*COLOR_GRID)

    def _serialize(self, nodes)->Dict[str, Any]:
        ret = super()._serialize(nodes)
        ret['graph']['name'] = self.name
        ret['graph']['opset'] = self.opset
        ret['graph']['doc_string'] = self.doc_string
        return ret

    def _deserialize(self, data, relative_pos=False, pos=None):
        ret = super()._deserialize(data, relative_pos, pos)
        self.name = data['graph']['name']
        self.opset = data['graph']['opset']
        self.doc_string = data['graph']['doc_string']
        return ret

    def create_qtinput(self, input: gs.Tensor)->ONNXInput:
        node_name = input.name
        n = self.create_node("nodes.node.ONNXInput", node_name)
        n.set_shape(copy.deepcopy(input.shape))
        n.set_dtype(input.dtype)
        n.set_output_names([o.name for o in input.outputs])
        n.set_color()
        return n

    def create_qtoutput(self, output: gs.Tensor)->ONNXOutput:
        node_name = output.name
        n = self.create_node("nodes.node.ONNXOutput", node_name)
        n.set_shape(copy.deepcopy(output.shape))
        n.set_dtype(output.dtype)
        n.set_input_names([i.name for i in output.inputs])
        n.set_color()
        return n

    def create_qtnode(self, onnx_node: gs.Node)->NodeObject:
        node_name = onnx_node.name # str
        n = self.create_node("nodes.node.ONNXNode", name=node_name)
        onnx_inputs:List[ONNX_IO] = []
        for inp in onnx_node.inputs:
            t = type(inp)
            if t is gs.Tensor:
                onnx_inputs += [ONNX_IO(inp.name, str(inp.dtype), inp.shape, None)]
            elif t is gs.Constant:
                onnx_inputs += [ONNX_IO(inp.name, str(inp.values.dtype), inp.shape, inp.values.tolist())]
            elif t is gs.Variable:
                if inp.dtype is None:
                    onnx_inputs += [ONNX_IO(inp.name, None, None, None)]
                else:
                    onnx_inputs += [ONNX_IO(inp.name, str(inp.dtype), inp.shape, None)]
            else:
                onnx_inputs += [ONNX_IO(inp.name, None, None, None)]
        onnx_outputs = []
        for out in onnx_node.outputs:
            t = type(out)
            if t is gs.Tensor:
                onnx_outputs += [ONNX_IO(out.name, str(out._values.dtype), out.shape, None)]
            elif t is gs.Constant:
                onnx_outputs += [ONNX_IO(out.name, str(out.values.dtype), out.shape, out.values.tolist())]
            elif t is gs.Variable:
                if out.dtype is None:
                    onnx_outputs += [ONNX_IO(out.name, None, None, None)]
                else:
                    onnx_outputs += [ONNX_IO(out.name, str(out.dtype), out.shape, None)]
            else:
                onnx_outputs += [ONNX_IO(out.name, None, None, None)]
        n.set_op(onnx_node.op) # str
        n.set_onnx_inputs(onnx_inputs)
        n.set_onnx_outputs(onnx_outputs)
        if n.op in ['Constant', 'ConstantOfShape']:
            d = {
                "inputs":onnx_node.attrs["value"].inputs,
                "name": onnx_node.attrs["value"].name,
                "outputs": onnx_node.attrs["value"].outputs,
                "shape": onnx_node.attrs["value"].shape,
                "dtype": str(onnx_node.attrs["value"].values.dtype),
                "values": onnx_node.attrs["value"].values.tolist()
            }
            n.set_attrs(d)
        else:
            n.set_attrs(copy.deepcopy(onnx_node.attrs)) # OrderedDict

        n.set_color()
        if n.op in ['Constant', 'ConstantOfShape']:
            n.set_port_deletion_allowed(True)
            n.delete_input(0)
            n.set_port_deletion_allowed(False)
        return n

    def to_networkx(self)->nx.DiGraph:
        return NodeGraphToNetworkX(self)

    def to_onnx_gs(self)->gs.Graph:
        return NodeGraphtoONNX(self)

    def to_onnx(self, non_verbose=True)->onnx.ModelProto:
        graph = NodeGraphtoONNX(self)
        ret = None
        try:
            ret = onnx.shape_inference.infer_shapes(gs.export_onnx(graph))
        except:
            ret = gs.export_onnx(graph)
            if not non_verbose:
                print(
                    f'{PrintColor.YELLOW}WARNING:{PrintColor.RESET} '+
                    'The input shape of the next OP does not match the output shape. '+
                    'Be sure to open the .onnx file to verify the certainty of the geometry.'
                )
        return ret

    def auto_layout(self):
        auto_layout_nodes(self)


def NodeGraphToNetworkX(graph:ONNXNodeGraph)->nx.DiGraph:
    nx_g = nx.DiGraph()
    for n in graph.all_nodes():
        nx_g.add_node(n.name())
    for n in graph.all_nodes():
        for input_nodes in n.connected_input_nodes().values():
            for inp in input_nodes:
                nx_g.add_edge(inp.name(), n.name())
    return nx_g


def NodeGraphtoONNX(graph:ONNXNodeGraph)->gs.Graph:
    nodes = []
    input_names = []
    output_names = []
    input_variables = []
    output_variables = []
    for n in graph.get_nodes_by_type("nodes.node.ONNXInput"):
        input_variables.append(gs.Variable(name=n.name(), dtype=n.dtype, shape=n.shape))
        input_names.append(n.name())
    for n in graph.get_nodes_by_type("nodes.node.ONNXOutput"):
        output_variables.append(gs.Variable(name=n.name(), dtype=n.dtype, shape=n.shape))
        output_names.append(n.name())

    for n in graph.get_nodes_by_type("nodes.node.ONNXNode"):
        input_gs_variables = []
        output_gs_variables = []

        for name, dtype, shape, val in n.onnx_inputs:
            if name in input_names:
                for inp_v in input_variables:
                    if name == inp_v.name:
                        input_gs_variables.append(inp_v)
            elif dtype is None:
                input_gs_variables.append(gs.Variable(name=name, dtype=None, shape=None))
            elif val == -1:
                input_gs_variables.append(gs.Variable(name=name, dtype=dtype, shape=shape))
            else:
                input_gs_variables.append(gs.Constant(name=name, values=np.array(val, dtype=dtype).reshape(shape)))

        for name, dtype, shape, val in n.onnx_outputs:
            if name in output_names:
                for out_v in output_variables:
                    if name == out_v.name:
                        output_gs_variables.append(out_v)
            elif dtype is None:
                output_gs_variables.append(gs.Variable(name=name, dtype=None, shape=None))
            elif val == -1:
                output_gs_variables.append(gs.Variable(name=name, dtype=dtype, shape=shape))
            else:
                output_gs_variables.append(gs.Constant(name=name, values=np.array(val, dtype=dtype).reshape(shape)))

        node = None
        if n.op not in ['Constant', 'ConstantOfShape']:
            # for not Constant
            node = gs.Node(
                name=n.name(),
                op=n.op,
                attrs=n.attrs,
                inputs=input_gs_variables,
                outputs=output_gs_variables,
            )
            nodes.append(node)
        else:
            # for Constant
            values = np.array(n.attrs["values"], dtype=DTYPES_TO_NUMPY_TYPES[n.attrs["dtype"]])
            if len(n.attrs["shape"])>0:
                values = values.reshape(n.attrs["shape"])
            attrs = OrderedDict(
                value=gs.Constant(
                        n.attrs["name"],
                        values=values,
                    )
            )
            node = gs.Node(
                name=n.name(),
                op=n.op,
                attrs=attrs,
                inputs=None,
                outputs=output_gs_variables,
            )
            nodes.append(node)

    onnx_graph = gs.Graph(
        nodes=nodes,
        name=graph.name,
        opset=graph.opset,
        inputs=input_variables,
        outputs=output_variables,
        doc_string=graph.doc_string,
    )
    return onnx_graph

def auto_layout_nodes(graph:ONNXNodeGraph):
    graph.begin_undo('Auto Layout Nodes')

    nodes = graph.all_nodes()
    filtered_nodes = [n for n in nodes if not isinstance(n, ONNXInput)]
    start_nodes = [
        n for n in filtered_nodes
        if not any(n.connected_output_nodes().values())
    ]
    if not start_nodes:
        return
    nx_graph = NodeGraphToNetworkX(graph)
    pos = nx.nx_pydot.pydot_layout(nx_graph, root=start_nodes[0], prog="dot")
    for name, (x, y) in pos.items():
        node = graph.get_node_by_name(name)
        node.set_pos(x*3, -y*1.5)

    graph.end_undo()


def ONNXtoNodeGraph(onnx_graph: gs.Graph, node_graph:ONNXNodeGraph):
    qt_nodes = {}
    qt_edge = {}

    # Create Input/Output Node
    for inp in onnx_graph.inputs:
        qt_n = node_graph.create_qtinput(inp)
        qt_nodes[inp.name] = qt_n
    for out in onnx_graph.outputs:
        qt_n = node_graph.create_qtoutput(out)
        qt_nodes[out.name] = qt_n

    # Create Node
    for onnx_node in onnx_graph.nodes:
        qt_n = node_graph.create_qtnode(onnx_node)
        qt_nodes[onnx_node.name] = qt_n
        for input in onnx_node.inputs:
            if input.name not in qt_edge.keys():
                qt_edge[input.name] = {
                    "inputs": [onnx_node.name],
                    "outputs": [],
                }
            else:
                qt_edge[input.name]["inputs"].append(onnx_node.name)
        for output in onnx_node.outputs:
            if output.name not in qt_edge.keys():
                qt_edge[output.name] = {
                    "inputs": [],
                    "outputs": [onnx_node.name],
                }
            else:
                qt_edge[output.name]["outputs"].append(onnx_node.name)

    input_names = [inp.name for inp in onnx_graph.inputs]
    output_names = [out.name for out in onnx_graph.outputs]
    # Connect Node
    for key, val in qt_edge.items():
        node_inputs = val["inputs"]
        node_outputs = val["outputs"]
        if key in input_names:
            for inp in node_inputs:
                qt_nodes[key].set_output(0, qt_nodes[inp].input(0))
        if key in output_names:
            for out in node_outputs:
                qt_nodes[out].set_output(0, qt_nodes[key].input(0))
        for inp in node_inputs:
            for out in node_outputs:
                qt_nodes[out].set_output(0, qt_nodes[inp].input(0))
