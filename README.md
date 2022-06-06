# [WIP]OnnxGraphQt

ONNX model visualizer with NodeGraphQt.

## Requirements
- [NodeGraphQt](https://github.com/jchanvfx/NodeGraphQt)
- PySide2
- igraph
- Numpy
- onnx
- onnx_graphsurgeon
- [simple-onnx-processing-tools](https://github.com/PINTO0309/simple-onnx-processing-tools)

## Install
```bash
git clone https://github.com/fateshelled/OnnxGraphQt
cd OnnxGraphQt
python3 -m pip install nvidia-pyindex
python3 -m pip install -U -r requirements.txt
```

## Run with Docker
```bash
git clone https://github.com/fateshelled/OnnxGraphQt
cd OnnxGraphQt
# build docker image
./docker/build.bash
# run
./docker/run.bash
```

## Usage
```bash
cd OnnxGraphQt

# Open empty graph
python3 onnxgraphqt/main.py

# Open with onnx model
python3 onnxgraphqt/main.py onnxgraphqt/data/mobilenetv2-7.onnx

```

## ToDo
- [ ] Add Simple Shape Inference tool [[ssi4onnx](https://github.com/PINTO0309/ssi4onnx)]
- [ ] Add Simple Inference Test[[sit4onnx](https://github.com/PINTO0309/sit4onnx)]
- [ ] Add Simple Structure Checker[[ssc4onnx](https://github.com/PINTO0309/ssc4onnx)]
- [ ] Update auto layout algorithm

## References
- https://github.com/jchanvfx/NodeGraphQt
- https://github.com/PINTO0309/simple-onnx-processing-tools
- https://fdwr.github.io/LostOnnxDocs/OperatorFormulas.html
- https://github.com/onnx/onnx/blob/main/docs/Operators.md


