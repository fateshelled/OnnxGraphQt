import requests
import json
import onnx_graphsurgeon as gs
from .onnx_to_dict import onnx_to_dict
# from onnx_to_dict import onnx_to_dict

def request_layout(onnx_graph: gs.Graph) -> dict:
    data = onnx_to_dict(onnx_graph)

    try:
        res = requests.post("http://localhost:3000/layout", json=data)
        print(f"status: {res.status_code}")
        if res.status_code == 200:
            content = json.loads(res.content.decode('utf-8'))
            return content
    except BaseException as e:
        raise(e)

if __name__ == "__main__":
    import os
    import onnx
    import json

    base_dir = os.path.dirname(__file__)
    onnx_file = os.path.join(base_dir, "../data/mobilenetv2-7.onnx")

    onnx_model = onnx.load(onnx_file)
    onnx_graph = gs.import_onnx(onnx_model)

    try:
        ret = request_layout(onnx_graph)
        print("[inputs]")
        for key, val in ret["inputs"].items():
            print(f"    {key}: {val}")
        print("[nodes]")
        for key, val in ret["nodes"].items():
            print(f"    {key}: {val}")
        print("[outputs]")
        for key, val in ret["outputs"].items():
            print(f"    {key}: {val}")

    except BaseException as e:
        print(e)
