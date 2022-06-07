import os
import time
from PySide2 import QtCore, QtWidgets, QtGui

DEFAULT_SPLASH_IMAGE = os.path.join(os.path.dirname(__file__), "../data/splash.png")

def create_screen(image_path=DEFAULT_SPLASH_IMAGE):
    pixmap = QtGui.QPixmap(image_path)
    splash = QtWidgets.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
    splash.setEnabled(False)
    return splash

def create_screen_progressbar(image_path=DEFAULT_SPLASH_IMAGE):
    pixmap = QtGui.QPixmap(image_path)
    splash = QtWidgets.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
    splash.setEnabled(False)
    progressBar = QtWidgets.QProgressBar(splash)
    progressBar.setMaximum(10)
    progressBar.setGeometry(0, pixmap.height() - 50, pixmap.width(), 20)
    return splash, progressBar

if __name__ == "__main__":
    import signal
    import os
    import sys
    import time
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication(sys.argv)
    splash, progressBar = create_screen_progressbar()
    # splash = create_screen()
    splash.show()
    time.sleep(0.01)
    splash.showMessage("loading...", alignment=QtCore.Qt.AlignBottom, color=QtGui.QColor.fromRgb(255, 255, 255))
    for i in range(1, 11):
        progressBar.setValue(i)
        t = time.time()
        while time.time() < t + 0.1:
           app.processEvents()
    time.sleep(1)

    window = QtWidgets.QMainWindow()
    window.show()

    splash.finish(window)

    app.exec_()