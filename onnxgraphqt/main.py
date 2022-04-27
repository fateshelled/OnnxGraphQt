
import signal
from PySide2 import QtCore, QtWidgets
from main_window import MainWindow

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])

    main_window = MainWindow()
    main_window.show()

    app.exec_()
