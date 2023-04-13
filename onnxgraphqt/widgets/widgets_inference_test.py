import subprocess
from typing import List, Union
import tempfile
import signal
from PySide2 import QtCore, QtWidgets, QtGui
from ast import literal_eval
import onnx
import onnxruntime as ort

import os
from onnxgraphqt.utils.widgets import set_font, BASE_FONT_SIZE, LARGE_FONT_SIZE
from onnxgraphqt.utils.color import replace_PrintColor

ONNX_PROVIDER_TABLE = {
    "TensorrtExecutionProvider": ["tensorrt"],
    "CUDAExecutionProvider": ["cuda"],
    "OpenVINOExecutionProvider": ["openvino_cpu", "openvino_gpu"],
    "CPUExecutionProvider": ["cpu"]
}

class InferenceProcess(QtCore.QThread):
    signal = QtCore.Signal(str)
    btn_signal = QtCore.Signal(bool)
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.onnx_file_path: str = ""
        self.batch_size: int = 1
        self.fixes_shapes: List[int] = None
        self.test_loop_count: int = 1
        self.onnx_execution_provider: str = ""

    def set_properties(self,
                       onnx_file_path: str,
                       batch_size: int, fixes_shapes: Union[List[int], None],
                       test_loop_count: int, onnx_execution_provider: str):
        self.onnx_file_path = onnx_file_path
        self.batch_size = batch_size
        self.fixes_shapes = fixes_shapes
        self.test_loop_count = test_loop_count
        self.onnx_execution_provider = onnx_execution_provider

    def run(self):
        self.btn_signal.emit(False)
        cmd = f"sit4onnx "
        cmd += f" --input_onnx_file_path {self.onnx_file_path} "
        cmd += f" --batch_size {self.batch_size} "
        cmd += f" --test_loop_count {self.test_loop_count} "
        cmd += f" --onnx_execution_provider {self.onnx_execution_provider} "
        if self.fixes_shapes is not None:
            cmd += f" --fixes_shapes {self.fixes_shapes} "
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            line: bytes = proc.stdout.readline()
            if line:
                txt = line.decode("utf-8").replace("\n", "")
                print(txt)
                self.signal.emit(replace_PrintColor(txt))
            if not line and proc.poll() is not None:
                txt = "\n"
                print(txt)
                self.signal.emit(txt)
                break
        self.btn_signal.emit(True)

class InferenceTestWidgets(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 600

    def __init__(self, onnx_model: onnx.ModelProto=None, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("inference test")
        self.fp = tempfile.NamedTemporaryFile()
        self.tmp_filename = self.fp.name + ".onnx"
        try:
            onnx.save(onnx_model, self.tmp_filename)
        except BaseException as e:
            raise e
        self.initUI()

    def __del__(self) -> None:
        print(f"delete {self.tmp_filename}")
        try:
            os.remove(self.tmp_filename)
        except BaseException as e:
            raise e

    def initUI(self):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)
        set_font(self, font_size=BASE_FONT_SIZE)

        base_layout = QtWidgets.QVBoxLayout()
        # base_layout.setSizeConstraint(base_layout.SizeConstraint.SetFixedSize)

        # add layout
        footer_layout = QtWidgets.QVBoxLayout()
        main_layout = QtWidgets.QFormLayout()
        base_layout.addLayout(main_layout)
        base_layout.addLayout(footer_layout)

        # Form layout
        main_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        self.tb_batch_size = QtWidgets.QLineEdit()
        self.tb_batch_size.setText("1")
        self.tb_batch_size.setAlignment(QtCore.Qt.AlignRight)
        lbl_batch_size = QtWidgets.QLabel("Batch Size: ")
        set_font(lbl_batch_size, font_size=LARGE_FONT_SIZE, bold=True)
        main_layout.addRow(lbl_batch_size, self.tb_batch_size)

        self.tb_fixed_shapes = QtWidgets.QLineEdit()
        self.tb_fixed_shapes.setAlignment(QtCore.Qt.AlignRight)
        lbl_fixed_shapes = QtWidgets.QLabel("Fixed Shapes: ")
        set_font(lbl_fixed_shapes, font_size=LARGE_FONT_SIZE, bold=True)
        main_layout.addRow(lbl_fixed_shapes, self.tb_fixed_shapes)

        self.tb_test_loop_count = QtWidgets.QLineEdit()
        self.tb_test_loop_count.setText("10")
        self.tb_test_loop_count.setAlignment(QtCore.Qt.AlignRight)
        lbl_test_loop_count = QtWidgets.QLabel("Test Loop Count: ")
        set_font(lbl_test_loop_count, font_size=LARGE_FONT_SIZE, bold=True)
        main_layout.addRow(lbl_test_loop_count, self.tb_test_loop_count)

        self.cmb_onnx_execution_provider = QtWidgets.QComboBox()
        self.cmb_onnx_execution_provider.setEditable(False)
        for provider in ort.get_available_providers():
            if provider in ONNX_PROVIDER_TABLE.keys():
                providers = ONNX_PROVIDER_TABLE[provider]
                for p in providers:
                    self.cmb_onnx_execution_provider.addItem(f"{p}  ", p)
        lbl_onnx_execution_provider = QtWidgets.QLabel("Execution Provider: ")
        set_font(lbl_onnx_execution_provider, font_size=LARGE_FONT_SIZE, bold=True)
        main_layout.addRow(lbl_onnx_execution_provider, self.cmb_onnx_execution_provider)

        # textbox
        self.tb_console = QtWidgets.QTextBrowser()
        self.tb_console.setReadOnly(True)
        self.tb_console.setStyleSheet(f"font-size: {BASE_FONT_SIZE}px; color: #FFFFFF; background-color: #505050;")
        footer_layout.addWidget(self.tb_console)

        # Dialog button
        self.btn_infer = QtWidgets.QPushButton("inference")
        self.btn_infer.clicked.connect(self.btn_infer_clicked)
        footer_layout.addWidget(self.btn_infer)

        # inferenceProcess
        self.inference_process = InferenceProcess()
        self.inference_process.signal.connect(self.update_text)
        self.inference_process.btn_signal.connect(self.btn_infer.setEnabled)

        self.setLayout(base_layout)

    def update_text(self, txt: str):
        # self.tb_console.appendPlainText(txt)
        self.tb_console.append(txt)

    def btn_infer_clicked(self) -> None:
        batch_size = literal_eval(self.tb_batch_size.text())
        try:
            fixes_shapes = literal_eval(self.tb_fixed_shapes.text())
        except:
            fixes_shapes = None
        test_loop_count = literal_eval(self.tb_test_loop_count.text())
        onnx_execution_provider = self.cmb_onnx_execution_provider.currentData()
        self.inference_process.set_properties(self.tmp_filename,
                                              batch_size,
                                              fixes_shapes,
                                              test_loop_count,
                                              onnx_execution_provider)
        self.inference_process.start()


if __name__ == "__main__":
    import signal
    import os
    from utils.color import PrintColor
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])

    model_path = os.path.join(os.path.dirname(__file__), "../data/mobilenetv2-7.onnx")
    model = onnx.load_model(model_path)
    window = InferenceTestWidgets(model)
    window.show()

    window.update_text(f"{PrintColor.BLACK[1]}BLACK{PrintColor.RESET[1]}")
    window.update_text(f"{PrintColor.RED[1]}RED{PrintColor.RESET[1]}")
    window.update_text(f"{PrintColor.GREEN[1]}GREEN{PrintColor.RESET[1]}")
    window.update_text(f"{PrintColor.YELLOW[1]}YELLOW{PrintColor.RESET[1]}")
    window.update_text(f"{PrintColor.BLUE[1]}BLUE{PrintColor.RESET[1]}")
    window.update_text(f"{PrintColor.MAGENTA[1]}MAGENTA{PrintColor.RESET[1]}")
    window.update_text(f"{PrintColor.CYAN[1]}CYAN{PrintColor.RESET[1]}")
    window.update_text(f"{PrintColor.WHITE[1]}WHITE{PrintColor.RESET[1]}")

    app.exec_()
    del window
