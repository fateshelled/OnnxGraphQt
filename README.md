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
python3 -m pip install -U -r requirements.txt
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
- [x] Visualize Model
- [x] Export Model
- [ ] Combine Network [1. [snc4onnx](https://github.com/PINTO0309/snc4onnx)]
- [x] Extract Network [2. [sne4onnx](https://github.com/PINTO0309/sne4onnx)]
- [x] Delete Node [3. [snd4onnx](https://github.com/PINTO0309/snd4onnx)]
- [x] Constant Value Shrink [4. [scs4onnx](https://github.com/PINTO0309/scs4onnx)]
- [x] Generate Operation [5. [sog4onnx](https://github.com/PINTO0309/sog4onnx)]
- [x] Modify Operator Parameter [6. [sam4onnx](https://github.com/PINTO0309/sam4onnx)]
- [x] Change Opset [7. [soc4onnx](https://github.com/PINTO0309/soc4onnx)]
- [x] NCHW and NHWC conversion [8. [scc4onnx](https://github.com/PINTO0309/scc4onnx)]
- [x] Add Node [9. [sna4onnx](https://github.com/PINTO0309/sna4onnx)]
- [x] Initialize Batchsize [10. [sbi4onnx](https://github.com/PINTO0309/sbi4onnx)]
- [x] Rename Operator [11. [sor4onnx](https://github.com/PINTO0309/sor4onnx)]
- [x] Export to JSON [12. [onnx2json](https://github.com/PINTO0309/onnx2json)]
- [x] Import from JSON [13. [json2onnx](https://github.com/PINTO0309/json2onnx)]
- [ ] Update auto layout algorithm

## References
- https://github.com/jchanvfx/NodeGraphQt
- https://github.com/PINTO0309/simple-onnx-processing-tools
- https://fdwr.github.io/LostOnnxDocs/OperatorFormulas.html
- https://github.com/onnx/onnx/blob/main/docs/Operators.md


