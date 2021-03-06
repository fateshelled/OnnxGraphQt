import os
import math
from dataclasses import dataclass
from typing import List, Dict
from json import JSONDecoder

@dataclass
class OperatorAttribute:
    name: str
    value_type: type
    default_value: str

@dataclass
class OperatorVersion:
    since_opset: int
    inputs: int
    outputs: int
    attrs: List[OperatorAttribute]

@dataclass
class Operator:
    name: str
    versions: List[OperatorVersion]

_DEFAULT_ONNX_OPSETS_JSON_PATH = os.path.join(os.path.dirname(__file__),
                                             '..',
                                            'data', 'onnx_opsets.json')
def _load_json(json_path=_DEFAULT_ONNX_OPSETS_JSON_PATH)->List[Operator]:
    json_str = ''
    with open(json_path, mode='r') as f:
        json_str = f.read()
    dec = JSONDecoder()
    json_dict:Dict = dec.decode(json_str)

    ret = []
    for op_name, v1 in json_dict.items():
        versions = []
        for since_opset, v2 in v1.items():
            since_opset = int(since_opset)
            inputs = v2["inputs"]
            outputs = v2["outputs"]
            attrs = []
            if inputs == 'inf':
                inputs = math.inf
            else:
                inputs = int(inputs)
            if outputs == 'inf':
                outputs = math.inf
            else:
                outputs = int(outputs)

            for attr_name, (attr_value_type, defalut_value) in v2["attrs"].items():
                attrs.append(
                    OperatorAttribute(name=attr_name,
                                      value_type=attr_value_type,
                                      default_value=defalut_value)
                )
            versions.append(
                OperatorVersion(
                    since_opset=since_opset,
                    inputs=inputs, outputs=outputs, attrs=attrs)
            )

        ret.append(
            Operator(
                name=op_name,
                versions=versions)
        )
    return ret

def _get_latest_opset_version(opsets:List[Operator])->int:
    opset = 1
    for op in opsets:
        for v in op.versions:
            if opset < v.since_opset:
                opset = v.since_opset
    return opset

onnx_opsets = _load_json()
opnames = [op.name for op in onnx_opsets]
latest_opset = _get_latest_opset_version(onnx_opsets)

if __name__ == "__main__":
    print(_DEFAULT_ONNX_OPSETS_JSON_PATH)
    for op in onnx_opsets:
        print(op.name)
        for v in op.versions:
            print(v)
        print()