
import sys
import signal
from PySide2 import QtCore, QtWidgets
from yaml import parse
from main_window import MainWindow

if __name__ == "__main__":
    args = sys.argv
    onnx_model_path = args[1] if len(args)>1 else ""

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])

    main_window = MainWindow(onnx_model_path=onnx_model_path)
    main_window.show()

    app.exec_()
