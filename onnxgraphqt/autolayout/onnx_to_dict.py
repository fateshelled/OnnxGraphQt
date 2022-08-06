from dataclasses import dataclass, asdict
from typing import Any, List, Dict, Tuple, Union
import onnx
import onnx_graphsurgeon as gs


@dataclass
class OnnxInput:
    name: str
    dtype: str
    shape: List[Union[int, str]]
    output_names: List[str]


@dataclass
class OnnxOutput:
    name: str
    dtype: str
    shape: List[Union[int, str]]
    input_names: List[str]


@dataclass
class OnnxNode:
    name: str
    op: str
    input_names: List[str]
    output_names: List[str]
    attrs: Dict[str, Any]


@dataclass
class OnnxGraph:
    inputs: List[OnnxInput]
    outputs: List[OnnxOutput]
    nodes: List[OnnxNode]
    edges: List[Tuple[str, str]]


def onnx_to_dataclass(onnx_graph: gs.Graph, reverse=False, load_weights=True) -> OnnxGraph:
    inputs = []
    outputs = []
    nodes = []
    edges = []

    # add inputs
    for input in onnx_graph.inputs:
        n = OnnxInput(name=input.name,
                      dtype=str(input.dtype),
                      shape=input.shape,
                      output_names=[out.name for out in input.outputs])
        inputs.append(n)

    # add nodes
    for onnx_node in onnx_graph.nodes:
        attrs = {}
        if load_weights:
            for input in onnx_node.inputs:
                if isinstance(input, gs.Constant):
                    attrs["inputs"] = [input.name, str(input.values.dtype), input.shape, input.values.tolist()]
                elif isinstance(input, gs.Tensor):
                    attrs["inputs"] = [input.name, str(input.dtype), input.shape]
                elif isinstance(input, gs.Variable):
                    if input.dtype is None:
                        attrs["inputs"] = [input.name]
                    else:
                        attrs["inputs"] = [input.name, str(input.dtype), input.shape.name]
                else:
                    attrs["inputs"] = [input.name]
            for output in onnx_node.outputs:
                if isinstance(output, gs.Constant):
                    attrs["outputs"] = [output.name, str(output.values.dtype), output.shape, output.values.tolist()]
                elif isinstance(output, gs.Tensor):
                    attrs["outputs"] = [output.name, str(output.dtype), output.shape]
                elif isinstance(output, gs.Variable):
                    if input.dtype is None:
                        attrs["outputs"] = [output.name]
                    else:
                        attrs["outputs"] = [output.name, str(input.dtype), output.shape]
                else:
                    attrs["outputs"] = [output.name]

        if onnx_node.op == "Constant":
            attrs["dtype"] = str(onnx_node.attrs["value"].values.dtype),
            attrs["values"] = onnx_node.attrs["value"].values.tolist()
        else:
            for key, val in onnx_node.attrs.items():
                attrs[key] = val

        n = OnnxNode(name=onnx_node.name,
                     op=onnx_node.op,
                     input_names=[input.name for input in onnx_node.inputs],
                     output_names=[out.name for out in onnx_node.outputs],
                     attrs=attrs)
        nodes.append(n)

    # add outputs
    for output in onnx_graph.outputs:
        n = OnnxOutput(name=output.name,
                       dtype=str(output.dtype),
                       shape=output.shape,
                       input_names=[input.name for input in output.inputs])
        outputs.append(n)

    # add edge
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
                if reverse:
                    edges.append((inp, key))
                else:
                    edges.append((key, inp))
        if key in output_names:
            for out in node_outputs:
                if reverse:
                    edges.append((key, out))
                else:
                    edges.append((out, key))
        for inp in node_inputs:
            for out in node_outputs:
                if reverse:
                    edges.append((inp, out))
                else:
                    edges.append((out, inp))

    return OnnxGraph(inputs=inputs, outputs=outputs, nodes=nodes, edges=edges)


def onnx_to_dict(onnx_graph: gs.Graph, reverse=False, load_weight=True) -> dict:
    return asdict(onnx_to_dataclass(onnx_graph, reverse, load_weight))


if __name__ == "__main__":
    import os
    import time
    import json
    import matplotlib.pyplot as plt

    base_dir = os.path.dirname(__file__)
    onnx_file = os.path.join(base_dir, "../data/mobilenetv2-7.onnx")
    onnx_model = onnx.load(onnx_file)
    onnx_graph = gs.import_onnx(onnx_model)

    t = time.time()
    data = onnx_to_dataclass(onnx_graph, reverse=True, load_weights=False)
    dt = time.time() - t
    print(f"onnx_to_dataclass load: {dt} sec")
    print()
    json_path = os.path.splitext(os.path.basename(onnx_file))[0] + ".json"
    with open(json_path, mode="w") as f:
        json.dump(asdict(data), f)

