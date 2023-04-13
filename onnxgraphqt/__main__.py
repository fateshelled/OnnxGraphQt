import sys, os
import signal
import time
from PySide2 import QtCore, QtWidgets, QtGui
from onnxgraphqt.main_window import MainWindow
from onnxgraphqt.widgets.splash_screen import create_screen
import multiprocessing


def main():
    args = sys.argv
    onnx_model_path = args[1] if len(args)>1 else ""

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication([])

    splash = create_screen()
    splash.show()
    time.sleep(0.05)
    msg = ""
    msg_align = QtCore.Qt.AlignBottom
    msg_color = QtGui.QColor.fromRgb(255, 255, 255)
    if onnx_model_path:
        msg = f"loading [{os.path.basename(onnx_model_path)}]"
    else:
        msg = "loading..."
    splash.showMessage(msg, alignment=msg_align, color=msg_color)
    print(msg)
    if not onnx_model_path:
        time.sleep(1.0)

    app.processEvents()

    main_window = MainWindow(onnx_model_path=onnx_model_path)

    msg = "load complete."
    splash.showMessage(msg, alignment=msg_align, color=msg_color)
    print(msg)
    time.sleep(0.1)

    app.processEvents()

    splash.finish(main_window)
    main_window.show()

    app.exec_()

if __name__ == "__main__":
    proc0 = multiprocessing.Process(target=main, daemon=False)
    proc0.start()
    print(f"start GUI [{proc0.pid}]")

    proc0.join()
    proc0.close()
