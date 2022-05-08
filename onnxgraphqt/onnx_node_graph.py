from dataclasses import dataclass
from typing import (
    Dict, List, Any, Optional, Union
)
from collections import OrderedDict
import copy

import numpy as np
import onnx
import onnx_graphsurgeon as gs
# import networkx as nx
import igraph

from PySide2 import QtCore, QtWidgets
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
from NodeGraphQt.base.factory import NodeFactory
from NodeGraphQt.base.model import NodeGraphModel
from NodeGraphQt.widgets.viewer import NodeViewer

from utils.color import (
    COLOR_BG,
    COLOR_FONT,
    COLOR_GRID,
    COLOR_WHITE,
    COLOR_GRAY,
    INPUT_NODE_COLOR,
    OUTPUT_NODE_COLOR,
    get_node_color,
    PrintColor,
)
from utils.dtype import (
    DTYPES_TO_NUMPY_TYPES,
)
from utils.style import set_context_menu_style
from onnx_node import (
    ONNXInput,
    ONNXOutput,
    ONNXNode,
    OnnxNodeIO
)

NAME = str
@dataclass
class OnnxGraph:
    inputs: Dict[NAME, ONNXInput]
    outputs: Dict[NAME, ONNXOutput]
    nodes: Dict[NAME, ONNXNode]
    node_inputs: Dict[NAME, OnnxNodeIO]

class ONNXNodeGraph(NodeGraph):
    def __super__init__(self, parent=None, **kwargs):
        """
        Args:
            parent (object): object parent.
            **kwargs (dict): Used for overriding internal objects at init time.
        """
        super(NodeGraph, self).__init__(parent)
        self.setObjectName('NodeGraph')
        self._model = (
            kwargs.get('model') or NodeGraphModel())
        self._node_factory = (
            kwargs.get('node_factory') or NodeFactory())

        self._undo_view = None
        self._undo_stack = (
            kwargs.get('undo_stack') or QtWidgets.QUndoStack(self))

        self._widget = None

        self._sub_graphs = {}

        self._viewer = (
            kwargs.get('viewer') or NodeViewer(undo_stack=self._undo_stack))

        # self._build_context_menu()
        # self._register_builtin_nodes()
        self._wire_signals()

    def __init__(self, name:str, opset:int, doc_string:str, parent=None, **kwargs):
        self.__super__init__(parent, **kwargs)
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
        set_context_menu_style(self, text_color=COLOR_FONT, bg_color=COLOR_WHITE, selected_color=COLOR_GRAY)
        # # Disable right click menu
        # self.disable_context_menu(True)

    def get_node_by_name(self, name)->List[Union[ONNXInput, ONNXOutput, ONNXNode]]:
        """
        Returns node that matches the name.

        Args:
            name (str): name of the node.
        Returns:
            NodeGraphQt.NodeObject: node object.
        """
        ret = []
        for node_id, node in self._model.nodes.items():
            if isinstance(node, ONNXNode):
                if node.node_name == name:
                    ret.append(node)
            if node.name() == name:
                ret.append(node)
        return ret

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

    def node_count(self)->int:
        return len(self.all_nodes())

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
        onnx_inputs:List[OnnxNodeIO] = []
        for inp in onnx_node.inputs:
            t = type(inp)
            if t is gs.Tensor:
                onnx_inputs += [OnnxNodeIO(inp.name, str(inp.dtype), inp.shape, None)]
            elif t is gs.Constant:
                onnx_inputs += [OnnxNodeIO(inp.name, str(inp.values.dtype), inp.shape, inp.values.tolist())]
            elif t is gs.Variable:
                if inp.dtype is None:
                    onnx_inputs += [OnnxNodeIO(inp.name, None, None, None)]
                else:
                    onnx_inputs += [OnnxNodeIO(inp.name, str(inp.dtype), inp.shape, None)]
            else:
                onnx_inputs += [OnnxNodeIO(inp.name, None, None, None)]
        onnx_outputs = []
        for out in onnx_node.outputs:
            t = type(out)
            if t is gs.Tensor:
                onnx_outputs += [OnnxNodeIO(out.name, str(out._values.dtype), out.shape, None)]
            elif t is gs.Constant:
                onnx_outputs += [OnnxNodeIO(out.name, str(out.values.dtype), out.shape, out.values.tolist())]
            elif t is gs.Variable:
                if out.dtype is None:
                    onnx_outputs += [OnnxNodeIO(out.name, None, None, None)]
                else:
                    onnx_outputs += [OnnxNodeIO(out.name, str(out.dtype), out.shape, None)]
            else:
                onnx_outputs += [OnnxNodeIO(out.name, None, None, None)]
        n.set_node_name(node_name)
        n.set_op(onnx_node.op) # str
        if len(onnx_inputs) > 0:
            n.set_onnx_inputs(onnx_inputs)
        if len(onnx_outputs) > 0:
            n.set_onnx_outputs(onnx_outputs)
        if n.op in ['Constant', 'ConstantOfShape']:
            d = {
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

    def load_onnx_graph(self, onnx_graph):
        ONNXtoNodeGraph(onnx_graph, self)

    # def to_networkx(self)->nx.DiGraph:
    #     return NodeGraphToNetworkX(self)

    def to_onnx_gs(self)->gs.Graph:
        return NodeGraphtoONNX(self)

    def to_onnx(self, non_verbose=True)->onnx.ModelProto:
        graph = self.to_onnx_gs()
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

    def to_data(self)->OnnxGraph:
        inputs = {}
        outputs = {}
        nodes = {}
        node_inputs = {}
        for n in self.all_nodes():
            if isinstance(n, ONNXNode):
                nodes[n.name()] = n
                for inp in n.onnx_inputs:
                    node_inputs[inp.name] = inp
            elif isinstance(n, ONNXInput):
                inputs[n.name()] = n
            elif isinstance(n, ONNXOutput):
                outputs[n.name()] = n
        return OnnxGraph(inputs=inputs, outputs=outputs, nodes=nodes, node_inputs=node_inputs)


    def export(self, file_path:str):
        try:
            onnx.save(self.to_onnx(), file_path)
            # from onnx_graphsurgeon.exporters.onnx_exporter import OnnxExporter
            # og = OnnxExporter.export_graph(self.to_onnx_gs(), do_type_check=True)
            # opset_imports = [onnx.helper.make_opsetid("", self.opset)]
            # single_op_graph = make_model(og, opset_imports=opset_imports)
        except Exception as e:
            raise e

    def auto_layout(self):
        auto_layout_nodes(self)


# def NodeGraphToNetworkX(graph:ONNXNodeGraph)->nx.DiGraph:
#     nx_g = nx.DiGraph()
#     for n in graph.all_nodes():
#         nx_g.add_node(n.name())
#     for n in graph.all_nodes():
#         for input_nodes in n.connected_input_nodes().values():
#             for inp in input_nodes:
#                 nx_g.add_edge(inp.name(), n.name())
#     return nx_g

def NodeGraphToEdges(graph:ONNXNodeGraph)->List:
    ret = []
    node_names = [n.name() for n in graph.all_nodes()]
    for i, n in enumerate(graph.all_nodes()):
        for input_nodes in n.connected_input_nodes().values():
            for inp in input_nodes:
                input_index = node_names.index(inp.name())
                ret.append([input_index, i])
    return ret


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

        for inp in n.onnx_inputs:
            name, dtype, shape, val = inp.name, inp.dtype, inp.shape, inp.values
            if name in input_names:
                for inp_v in input_variables:
                    if name == inp_v.name:
                        input_gs_variables.append(inp_v)
            elif dtype is None:
                input_gs_variables.append(gs.Variable(name=name, dtype=None, shape=None))
            elif val == -1 or val is None:
                input_gs_variables.append(gs.Variable(name=name, dtype=dtype, shape=shape))
            else:
                input_gs_variables.append(gs.Constant(name=name, values=np.array(val, dtype=dtype).reshape(shape)))

        for out in n.onnx_outputs:
            name, dtype, shape, val = out.name, out.dtype, out.shape, out.values
            if name in output_names:
                for out_v in output_variables:
                    if name == out_v.name:
                        output_gs_variables.append(out_v)
            elif dtype is None:
                output_gs_variables.append(gs.Variable(name=name, dtype=None, shape=None))
            elif val == -1 or val is None:
                output_gs_variables.append(gs.Variable(name=name, dtype=dtype, shape=shape))
            else:
                output_gs_variables.append(gs.Constant(name=name, values=np.array(val, dtype=dtype).reshape(shape)))

        node = None
        if n.op not in ['Constant', 'ConstantOfShape']:
            # for not Constant
            node = gs.Node(
                name=n.node_name,
                op=n.op,
                attrs=n.attrs,
                inputs=input_gs_variables,
                outputs=output_gs_variables,
            )
            nodes.append(node)
        else:
            # for Constant
            values = np.array(n.attrs["values"], dtype=DTYPES_TO_NUMPY_TYPES[n.attrs["dtype"]])
            # if len(n.attrs["shape"])>0:
            #     values = values.reshape(n.attrs["shape"])
            attrs = OrderedDict(
                value=gs.Constant(
                        n.node_name,
                        values=values,
                    )
            )
            node = gs.Node(
                name=n.node_name,
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
    # start_nodes = [
    #     n for n in filtered_nodes
    #     if not any(n.connected_output_nodes().values())
    # ]
    start_nodes = [
        i for i, n in enumerate(filtered_nodes)
        if not any(n.connected_output_nodes().values())
    ]
    if not start_nodes:
        return

    # nx_graph = NodeGraphToNetworkX(graph)
    # pos = nx.nx_pydot.pydot_layout(nx_graph, root=None, prog="dot")
    # for name, (x, y) in pos.items():
    #     node = graph.get_node_by_name(name)
    #     node.set_pos(x*3, -y*1.5)

    edges = NodeGraphToEdges(graph)
    ig_graph = igraph.Graph(edges=edges)
    layout = ig_graph.layout_reingold_tilford(root=start_nodes)
    for i, node in enumerate(graph.all_nodes()):
        x, y = layout.coords[i]
        node.set_pos(x*240, y*120)

    graph.end_undo()


def ONNXtoNodeGraph(onnx_graph: gs.Graph, node_graph:ONNXNodeGraph):
    qt_io_nodes = {}
    qt_io_edge = {}
    qt_nodes = {}
    qt_edge = {}

    # Create Input/Output Node
    for inp in onnx_graph.inputs:
        qt_n = node_graph.create_qtinput(inp)
        qt_io_nodes[inp.name] = qt_n

    for out in onnx_graph.outputs:
        qt_n = node_graph.create_qtoutput(out)
        qt_io_nodes[out.name] = qt_n

    # Create Node
    for onnx_node in onnx_graph.nodes:
        qt_n = node_graph.create_qtnode(onnx_node)
        qt_nodes[onnx_node.name] = qt_n

    for onnx_node in onnx_graph.nodes:
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
                qt_io_nodes[key].set_output(0, qt_nodes[inp].input(0))
        if key in output_names:
            for out in node_outputs:
                qt_nodes[out].set_output(0, qt_io_nodes[key].input(0))
        for inp in node_inputs:
            for out in node_outputs:
                qt_nodes[out].set_output(0, qt_nodes[inp].input(0))
    # Lock Node and Port
    for n in node_graph.all_nodes():
        for ip in n.input_ports():
            ip.set_locked(state=True, connected_ports=True, push_undo=False)
        for op in n.output_ports():
            op.set_locked(state=True, connected_ports=True, push_undo=False)

