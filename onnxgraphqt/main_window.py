from distutils.sysconfig import customize_compiler
import sys, os

# from Qt import QtCore, QtWidgets, QtGui
# from PyQt5 import QtCore, QtWidgets, QtGui
from PySide2 import QtCore, QtWidgets, QtGui
from NodeGraphQt import NodesTreeWidget, PropertiesBinWidget
from NodeGraphQt.widgets.node_graph import NodeGraphWidget

import onnx
import onnx_graphsurgeon as gs
from torch import swapdims

from menubar import MenuBar
from onnx_graph import ONNXNodeGraph, ONNXtoNodeGraph
from utils.color import *
from utils.opset import DEFAULT_OPSET


class MainWindow(QtWidgets.QMainWindow):
    _default_window_width = 1200
    _default_window_height = 800
    _graph_size_ratio = 3
    _sidemenu_size_ratio = 1
    _ENABLE_EXPORT_BUTTON = False

    def __init__(self, onnx_model_path="", parent=None):
        super(MainWindow, self).__init__(parent)

        self.graph = self.load_graph(onnx_model_path)
        self.graph_widget = self.graph.widget
        # self.nodes_tree: NodesTreeWidget = None
        self.properties_bin: PropertiesBinWidget = None

        self.init_ui()

    def init_ui(self):
        # Window size
        self.setGeometry(0, 0, self._default_window_width, self._default_window_height)

        # visible only clone button.
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowCloseButtonHint)

        # MenuBar
        self.menu_bar = MenuBar()
        self.menu_bar.file_exit_clicked = self.exit
        # self.menu_bar.file_open_clicked = self.btnOpenONNX_clicked
        # self.menu_bar.file_export_onnx_clicked = self.btnExportONNX_clicked
        # self.menu_bar.actions["export"].setEnabled(self._ENABLE_EXPORT_BUTTON)
        self.setMenuBar(self.menu_bar)

        # Main Layout
        self.layout_base = QtWidgets.QHBoxLayout()
        self.layout_graph = QtWidgets.QStackedLayout()
        self.layout_sidemenu = QtWidgets.QVBoxLayout()
        self.layout_base.addLayout(self.layout_graph, stretch=self._graph_size_ratio)
        self.layout_base.addLayout(self.layout_sidemenu, stretch=self._sidemenu_size_ratio)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(self.layout_base)
        self.setCentralWidget(central_widget)

        # Label
        layout_lbl = QtWidgets.QVBoxLayout()
        layout_lbl.setAlignment(QtCore.Qt.AlignTop)

        lbl_graph_opset = QtWidgets.QLabel()
        lbl_graph_opset.setText(f"opset: {self.graph.opset}")

        lbl_graph_name = QtWidgets.QLabel()
        lbl_graph_name.setText(f"name: {self.graph.name}")

        lbl_graph_doc_string = QtWidgets.QLabel()
        lbl_graph_doc_string.setText(f"doc_string: {self.graph.doc_string}")

        layout_lbl.addWidget(lbl_graph_name)
        layout_lbl.addWidget(lbl_graph_opset)
        layout_lbl.addWidget(lbl_graph_doc_string)
        self.layout_sidemenu.addLayout(layout_lbl)


        # Button
        layout_btn = QtWidgets.QHBoxLayout()
        self.btnOpenONNX = QtWidgets.QPushButton("open")
        # self.btnOpenONNX.setEnabled(False)
        self.btnOpenONNX.clicked.connect(self.btnOpenONNX_clicked)

        self.btnImportONNX = QtWidgets.QPushButton("import")
        self.btnImportONNX.setEnabled(False)
        self.btnImportONNX.clicked.connect(self.btnImportONNX_clicked)

        self.btnExportONNX = QtWidgets.QPushButton("export")
        self.btnExportONNX.setEnabled(self._ENABLE_EXPORT_BUTTON)
        self.btnExportONNX.clicked.connect(self.btnExportONNX_clicked)

        layout_btn.addWidget(self.btnOpenONNX)
        layout_btn.addWidget(self.btnImportONNX)
        layout_btn.addWidget(self.btnExportONNX)
        self.layout_sidemenu.addLayout(layout_btn)

        # ONNXNodeGraph
        self.update_graph(self.graph)


    def update_graph(self, graph: ONNXNodeGraph):

        cursor = self.cursor()
        cursor.setShape(QtCore.Qt.BusyCursor)
        self.setCursor(cursor)

        self.graph_widget.hide()
        self.layout_graph.removeWidget(self.graph_widget)
        del self.graph_widget
        del self.graph

        self.graph = graph
        self.graph_widget = graph.widget
        self.layout_graph.addWidget(graph.widget)
        self.graph.auto_layout()
        self.graph.fit_to_selection()

        # if self.nodes_tree is not None:
        #     self.nodes_tree.hide()
        #     self.layout_sidemenu.removeWidget(self.nodes_tree)
        #     del self.nodes_tree
        # self.nodes_tree = self.create_nodes_tree(self.graph)
        # self.layout_sidemenu.addWidget(self.nodes_tree)

        if self.properties_bin is not None:
            self.properties_bin.hide()
            self.layout_sidemenu.removeWidget(self.properties_bin)
            del self.properties_bin
        self.properties_bin = self.create_properties_bin(self.graph)
        self.layout_sidemenu.addWidget(self.properties_bin)

        cursor.setShape(QtCore.Qt.ArrowCursor)
        self.setCursor(cursor)


    def load_graph(self, onnx_model_path:str, graph:ONNXNodeGraph=None)->ONNXNodeGraph:

        cursor = self.cursor()
        cur_cursor = cursor.shape()
        cursor.setShape(QtCore.Qt.BusyCursor)
        self.setCursor(cursor)

        if onnx_model_path == "" or onnx_model_path is None:
            node_graph = ONNXNodeGraph(name="onnx_graph_qt",
                                       opset=DEFAULT_OPSET,
                                       doc_string=None,
                                       import_domains=None)
            return node_graph

        onnx_graph = gs.import_onnx(onnx.load(onnx_model_path))
        # create graph controller.
        if graph is None:
            self.setWindowTitle(os.path.basename(onnx_model_path))
            node_graph = ONNXNodeGraph(name=onnx_graph.name,
                                       opset=onnx_graph.opset,
                                       doc_string=onnx_graph.doc_string,
                                       import_domains=onnx_graph.import_domains)
        else:
            node_graph = graph

        ONNXtoNodeGraph(onnx_graph, node_graph)

        cursor.setShape(cur_cursor)
        self.setCursor(cursor)
        return node_graph

    def create_properties_bin(self, graph: ONNXNodeGraph):
        properties_bin = PropertiesBinWidget(node_graph=graph)
        properties_bin.set_limit(1)
        return properties_bin

    # def create_nodes_tree(self, graph: ONNXNodeGraph):
    #     nodes_tree = NodesTreeWidget(node_graph=graph)
    #     nodes_tree.set_category_label('nodes.node', 'Nodes')
    #     return nodes_tree

    def btnOpenONNX_clicked(self, e:bool):
        # self.dialog_open_file.show()
        file_name, exp = QtWidgets.QFileDialog.getOpenFileName(
                            self,
                            caption="Open ONNX Model File",
                            directory=os.path.abspath(os.curdir),
                            filter="*.onnx")
        if not file_name:
            return
        print(f"Open: {file_name}")
        graph = self.load_graph(file_name, None)
        self.update_graph(graph)

        self.btnImportONNX.setEnabled(True)
        # self.btnExportONNX.setEnabled(True)

    def btnImportONNX_clicked(self, e: bool):
        file_name, exp = QtWidgets.QFileDialog.getOpenFileName(
                            self,
                            caption="Open ONNX Model File",
                            directory=os.path.abspath(os.curdir),
                            filter="*.onnx")
        if not file_name:
            return
        print(f"Import: {file_name}")
        graph = self.load_graph(file_name, self.graph)
        self.update_graph(graph)

    def btnExportONNX_clicked(self, e:bool):
        # Export Dialog

        file_name, exp = QtWidgets.QFileDialog.getSaveFileName(
                            self,
                            caption="Export ONNX Model File",
                            directory=os.path.abspath(os.curdir),
                            filter="*.onnx")
        if not file_name:
            return
        print(f"Export: {file_name}.")

    def exit(self):
        self.close()


if __name__ == "__main__":
    import signal
    import os
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])

    base_dir = os.path.dirname(__file__)
    onnx_file = os.path.join(base_dir, "data", "mobilenetv2-12-int8.onnx")

    main_window = MainWindow(onnx_model_path=onnx_file)
    main_window.show()

    app.exec_()