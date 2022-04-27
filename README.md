# [WIP]OnnxGraphQt

ONNX model visualizer with NodeGraphQt.

## Requirements
- [NodeGraphQt](https://github.com/jchanvfx/NodeGraphQt)
- PySide2
- NetworkX
- Numpy
- onnx
- onnx_graphsurgeon


## Install
```bash
git clone https://github.com/fateshelled/OnnxGraphQt
cd OnnxGraphQt
python3 -m pip install -r requirements.txt
```

## Usage
```bash
cd OnnxGraphQt
python3 onnxgraphqt/main.py
```

## ToDo
- [x] Visualize Model
- [ ] Export Model
- [ ] Add and Remove Operator
- [ ] Edit Operator Parameter
- [ ] Change Opset
- [ ] NCHW and NHWC conversion

## References
- https://github.com/jchanvfx/NodeGraphQt
- https://github.com/PINTO0309/simple-onnx-processing-tools
- https://fdwr.github.io/LostOnnxDocs/OperatorFormulas.html
- https://github.com/onnx/onnx/blob/main/docs/Operators.md


