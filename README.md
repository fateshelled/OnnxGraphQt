# OnnxGraphQt

ONNX model visualizer. You can edit model structure with GUI!

![https://github.com/fateshelled/OnnxGraphQt/blob/main/LICENSE](https://img.shields.io/github/license/fateshelled/OnnxGraphQt)
![https://github.com/fateshelled/OnnxGraphQt/stargazers](https://img.shields.io/github/stars/fateshelled/OnnxGraphQt)

<p align="center">
  <img src="https://user-images.githubusercontent.com/53618876/173075283-3344ca39-adcc-4e73-a5ea-31148fa641bf.png" />
</p>


## Requirements
- [NodeGraphQt](https://github.com/jchanvfx/NodeGraphQt)
- PySide2
- Qt.py
- Numpy
- Pillow
- onnx
- onnx-simplifier
- onnx_graphsurgeon
- [simple-onnx-processing-tools](https://github.com/PINTO0309/simple-onnx-processing-tools)
- networkx
- grandalf

## Install
```bash
sudo apt install python3-pyside2*

git clone https://github.com/fateshelled/OnnxGraphQt
cd OnnxGraphQt
python3 -m pip install -U nvidia-pyindex
python3 -m pip install -U Qt.py
# If you want to use InferenceTest, install onnxruntime or onnxruntime-gpu
# python3 -m pip install -U onnxruntime
# python3 -m pip install -U onnxruntime-gpu
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
python3 onnxgraphqt

# Open with onnx model
python3 onnxgraphqt onnxgraphqt/data/mobilenetv2-7.onnx

```

![mobilenetv7-7.onnx](https://user-images.githubusercontent.com/53618876/193456965-07b0ccbe-5cfe-4cd8-a233-8dc897dd2446.png)


### Open Onnx Model
Open file dialog from menubar(File - Open) or drag and drop from file manager to main window.

Sample model is available at `ONNXGraphQt/onnxgraphqt/data/mobilenetv2-7.onnx`

![file open](https://user-images.githubusercontent.com/53618876/193456986-919c08b1-1382-426e-8b80-5dbe0e6e146d.png)


### Export
Export to ONNX file or Json file.

### Node detail
Double click on Node for more information.

![node information](https://user-images.githubusercontent.com/53618876/193457001-1738f4e0-948a-47f5-acdc-63bd4e4f09c8.png)

### Node Search
Node search window can be open from menubar(View - Search).
You can search node by name, type, input or output name.

![serach](https://user-images.githubusercontent.com/53618876/173082166-0cb05288-8033-451d-8fd0-23a2836d301f.png)

### [simple-onnx-processing-tools](https://github.com/PINTO0309/simple-onnx-processing-tools)

Please refer to each tool's Github repository for detailed usage.

- Generate Operator [[sog4onnx](https://github.com/PINTO0309/sog4onnx)]
- Add Node [[sna4onnx](https://github.com/PINTO0309/sna4onnx)]
- Combine Network [[snc4onnx](https://github.com/PINTO0309/snc4onnx)]
- Extract Network [[sne4onnx](https://github.com/PINTO0309/sne4onnx)]
- Rename Operator [[sor4onnx](https://github.com/PINTO0309/sor4onnx)]
- Modify Attributes and Constant [[sam4onnx](https://github.com/PINTO0309/sam4onnx)]
- Input Channel Conversion [[scc4onnx](https://github.com/PINTO0309/scc4onnx)]
- Initialize Batchsize [[sbi4onnx](https://github.com/PINTO0309/sbi4onnx)]
- Change Opset [[soc4onnx](https://github.com/PINTO0309/soc4onnx)]
- Constant Value Shrink [[scs4onnx](https://github.com/PINTO0309/scs4onnx)]
- Delete Node [[snd4onnx](https://github.com/PINTO0309/snd4onnx)])]
- Inference Test [[sit4onnx](https://github.com/PINTO0309/sit4onnx)]
- Change the INPUT and OUTPUT shape [[sio4onnx](https://github.com/PINTO0309/sio4onnx)]


## ToDo
- [ ] Add Simple Structure Checker[[ssc4onnx](https://github.com/PINTO0309/ssc4onnx)]


## References
- https://github.com/jchanvfx/NodeGraphQt
- https://github.com/lutzroeder/netron
- https://github.com/PINTO0309/simple-onnx-processing-tools
- https://fdwr.github.io/LostOnnxDocs/OperatorFormulas.html
- https://github.com/onnx/onnx/blob/main/docs/Operators.md


