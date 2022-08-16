from ast import Str, arguments
from dataclasses import dataclass, asdict
from typing import Any, List, Dict, Tuple, Union
import onnx
import onnx_graphsurgeon as gs


@dataclass
class InputArgument:
    name: str
    type: str
    shape: List[Union[int, str]]

@dataclass
class OutputArgument:
    name: str
    # op: str
    type: str
    shape: List[Union[int, str]]

@dataclass
class NodeArgument:
    name: str
    type: str
    shape: List[Union[int, str]]
    initializer: bool

@dataclass
class NodeIO:
    name: str
    arguments: List[NodeArgument]

@dataclass
class NodeType:
    name: str

@dataclass
class OnnxInput:
    name: str
    type: str
    shape: List[Union[int, str]]
    output_names: List[str]
    arguments: List[InputArgument]

@dataclass
class OnnxOutput:
    name: str
    type: str
    shape: List[Union[int, str]]
    input_names: List[str]
    arguments: List[OutputArgument]

@dataclass
class OnnxNode:
    name: str
    type: NodeType
    inputs: List[NodeIO]
    outputs: List[NodeIO]
    arguments: List[NodeArgument]


@dataclass
class OnnxGraph:
    inputs: List[OnnxInput]
    outputs: List[OnnxOutput]
    nodes: List[OnnxNode]


def onnx_to_dataclass(onnx_graph: gs.Graph) -> OnnxGraph:

    inputs = []
    outputs = []
    nodes = []
    visible_nodes = set()

    # edge
    input_names = [inp.name for inp in onnx_graph.inputs]
    output_names = [out.name for out in onnx_graph.outputs]
    edges_table = {}

    for onnx_node in onnx_graph.nodes:
        for input in onnx_node.inputs:
            if input.name not in edges_table.keys():
                edges_table[input.name] = {
                    "inputs": [onnx_node.name],
                    "outputs": [],
                }
            else:
                edges_table[input.name]["inputs"].append(onnx_node.name)
        for output in onnx_node.outputs:
            if output.name not in edges_table.keys():
                edges_table[output.name] = {
                    "inputs": [],
                    "outputs": [onnx_node.name],
                }
            else:
                edges_table[output.name]["outputs"].append(onnx_node.name)

    for key, val in edges_table.items():
        node_inputs = val["inputs"]
        node_outputs = val["outputs"]
        if key in input_names:
            for inp in node_inputs:
                visible_nodes.add(inp)
                visible_nodes.add(key)
        if key in output_names:
            for out in node_outputs:
                visible_nodes.add(key)
                visible_nodes.add(out)
        for inp in node_inputs:
            for out in node_outputs:
                visible_nodes.add(inp)
                visible_nodes.add(out)
    visible_nodes = list(visible_nodes)

    # add inputs
    for input in onnx_graph.inputs:
        n = OnnxInput(name=input.name,
                      type=str(input.dtype),
                      shape=input.shape,
                      output_names=[out.name for out in input.outputs],
                      arguments=[
                        InputArgument(
                            name=input.name,
                            type=str(input.dtype),
                            shape=input.shape,
                        )]
                     )
        inputs.append(n)

    # add nodes
    for onnx_node in onnx_graph.nodes:
        node_inputs = []
        node_outputs = []
        node_arguments = []
        for input in onnx_node.inputs:
            if input.name in visible_nodes:
                initializer = False
            else:
                initializer = hasattr(input, "values")
            node_inputs.append(
                NodeIO(
                    name=input.name,
                    arguments=[
                        NodeArgument(input.name, str(input.dtype), str(input.shape), initializer)
                    ]))
        for output in onnx_node.outputs:
            if output.name in visible_nodes:
                initializer = False
            else:
                initializer = hasattr(output, "values")
            node_outputs.append(
                NodeIO(name=output.name,
                       arguments=[
                        NodeArgument(output.name, str(output.dtype), str(output.shape), initializer)
                       ]))

        n = OnnxNode(name=onnx_node.name,
                     type=NodeType(onnx_node.op),
                     inputs=node_inputs,
                     outputs=node_outputs,
                     arguments=node_arguments,
                     )
        nodes.append(n)

    # add outputs
    for output in onnx_graph.outputs:
        n = OnnxOutput(name=output.name,
                       type=str(output.dtype),
                       shape=output.shape,
                       input_names=[input.name for input in output.inputs],
                       arguments=[
                        OutputArgument(
                            name=output.name,
                            type=str(output.dtype),
                            shape=output.shape,
                        )]
                       )
        outputs.append(n)


    return OnnxGraph(inputs=inputs, outputs=outputs, nodes=nodes)


def onnx_to_dict(onnx_graph: gs.Graph) -> dict:
    return asdict(onnx_to_dataclass(onnx_graph))


if __name__ == "__main__":
    import os
    import time
    import json

    base_dir = os.path.dirname(__file__)
    onnx_file = os.path.join(base_dir, "../data/mobilenetv2-7.onnx")
    onnx_model = onnx.load(onnx_file)
    onnx_graph = gs.import_onnx(onnx_model)

    t = time.time()
    data = onnx_to_dict(onnx_graph)
    dt = time.time() - t
    print(f"onnx_to_dataclass load: {dt} sec")
    print()
    json_path = os.path.splitext(os.path.basename(onnx_file))[0] + ".json"
    with open(json_path, mode="w") as f:
        json.dump(data, f)
