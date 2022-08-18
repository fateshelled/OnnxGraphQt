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
- onnx
- onnx-simplifier
- onnx_graphsurgeon
- [simple-onnx-processing-tools](https://github.com/PINTO0309/simple-onnx-processing-tools)
- Node.js

## Install
```bash
sudo apt install python3-pyside2*
sudo apt install nodejs

git clone https://github.com/fateshelled/OnnxGraphQt
cd OnnxGraphQt
python3 -m pip install -U nvidia-pyindex
python3 -m pip install -U Qt.py
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

![mobilenetv7-7.onnx](https://user-images.githubusercontent.com/53618876/173088722-a6ba22d4-d49a-4663-b2c2-a9a28e69c75a.png)


### Open Onnx Model
Open file dialog from menubar(File - Open) or drag and drop from file manager to main window.

Sample model is available at `ONNXGraphQt/onnxgraphqt/data/mobilenetv2-7.onnx`

![file open](https://user-images.githubusercontent.com/53618876/173079093-5cb8b80a-7b2e-46cf-a0c2-ff96f824486b.png)


### Export
Export to ONNX file or Json file.

### Node detail
Double click on Node for more information.

![node information](https://user-images.githubusercontent.com/53618876/173081692-da179f1d-bdc2-4122-9d1f-89461410afc4.png)

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
- Delete Node [[snd4onnx](https://github.com/PINTO0309/snd4onnx)]


## ToDo
- [ ] Add Simple Shape Inference tool [[ssi4onnx](https://github.com/PINTO0309/ssi4onnx)]
- [ ] Add Simple Inference Test[[sit4onnx](https://github.com/PINTO0309/sit4onnx)]
- [ ] Add Simple Structure Checker[[ssc4onnx](https://github.com/PINTO0309/ssc4onnx)]


## References
- https://github.com/jchanvfx/NodeGraphQt
- https://github.com/lutzroeder/netron
- https://github.com/PINTO0309/simple-onnx-processing-tools
- https://fdwr.github.io/LostOnnxDocs/OperatorFormulas.html
- https://github.com/onnx/onnx/blob/main/docs/Operators.md


