import sys, os

# from Qt import QtCore, QtWidgets, QtGui
# from PyQt5 import QtCore, QtWidgets, QtGui
from PySide2 import QtCore, QtWidgets, QtGui
from NodeGraphQt import NodesTreeWidget, PropertiesBinWidget
from NodeGraphQt.widgets.node_graph import NodeGraphWidget

import onnx
import onnx_graphsurgeon as gs


from snc4onnx import combine as onnx_tools_combine
from sne4onnx import extraction as onnx_tools_extraction
from snd4onnx import remove as onnx_tools_deletion
from scs4onnx import shrinking as onnx_tools_shrinking
from sog4onnx import generate as onnx_tools_generate
from sam4onnx import modify as onnx_tools_modify
from soc4onnx import change as onnx_tools_op_change
from scc4onnx import order_conversion as onnx_tools_order_conversion
from sna4onnx import add as onnx_tools_add


from menubar_widgets import MenuBarWidget
from add_node_widgets import AddNodeWidgets
from change_opset_widgets import ChangeOpsetWidget
from change_channel_widgets import ChangeChannelWidgets
from onnx_graph import ONNXNodeGraph, ONNXtoNodeGraph
# from utils.color import *
from utils.opset import DEFAULT_OPSET


class MainWindow(QtWidgets.QMainWindow):
    _default_window_width = 1200
    _default_window_height = 800
    _sidemenu_width = 400

    def __init__(self, onnx_model_path="", parent=None):
        super(MainWindow, self).__init__(parent)

        self.graph = self.load_graph(onnx_model_path=onnx_model_path)
        self.graph_widget = self.graph.widget
        # self.nodes_tree: NodesTreeWidget = None
        self.properties_bin: PropertiesBinWidget = None

        self.init_ui()

        if onnx_model_path:
            self.btnImportONNX.setEnabled(True)
            self.btnExportONNX.setEnabled(True)

    def init_ui(self):
        # Window size
        self.setGeometry(0, 0, self._default_window_width, self._default_window_height)

        # visible only clone button.
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowCloseButtonHint)

        # MenuBar
        self.menu_bar = MenuBarWidget()
        self.menu_bar.file_exit_clicked = self.exit
        self.setMenuBar(self.menu_bar)

        # Main Layout
        # Fixed side menu size.
        self.layout_graph = QtWidgets.QStackedLayout()
        self.layout_base = QtWidgets.QHBoxLayout()

        self.widget_sidemenu = QtWidgets.QWidget()
        self.widget_sidemenu.setFixedWidth(self._sidemenu_width)
        self.layout_sidemenu = QtWidgets.QVBoxLayout(self.widget_sidemenu)
        self.layout_main_properties = QtWidgets.QVBoxLayout()
        self.layout_node_properties = QtWidgets.QVBoxLayout()
        self.layout_sidemenu.addLayout(self.layout_main_properties)
        self.layout_sidemenu.addSpacerItem(QtWidgets.QSpacerItem(self._sidemenu_width, 10))
        self.layout_sidemenu.addLayout(self.layout_node_properties)

        self.layout_base.addLayout(self.layout_graph)
        self.layout_base.addWidget(self.widget_sidemenu)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(self.layout_base)
        self.setCentralWidget(central_widget)

        # Label
        layout_lbl = QtWidgets.QVBoxLayout()

        self.lbl_graph_opset = QtWidgets.QLabel()
        self.lbl_graph_opset.setText(f"opset: {self.graph.opset}")

        self.lbl_graph_name = QtWidgets.QLabel()
        self.lbl_graph_name.setText(f"name: {self.graph.name}")

        self.lbl_graph_doc_string = QtWidgets.QLabel()
        self.lbl_graph_doc_string.setText(f"doc_string: {self.graph.doc_string}")

        layout_lbl.addWidget(self.lbl_graph_name)
        layout_lbl.addWidget(self.lbl_graph_opset)
        layout_lbl.addWidget(self.lbl_graph_doc_string)
        self.layout_main_properties.addLayout(layout_lbl)

        # File Button
        layout_file_btn = QtWidgets.QHBoxLayout()
        self.btnOpenONNX = QtWidgets.QPushButton("open")
        self.btnOpenONNX.clicked.connect(self.btnOpenONNX_clicked)

        self.btnImportONNX = QtWidgets.QPushButton("import")
        self.btnImportONNX.setEnabled(False)
        self.btnImportONNX.clicked.connect(self.btnImportONNX_clicked)

        self.btnExportONNX = QtWidgets.QPushButton("export")
        self.btnExportONNX.setEnabled(False)
        self.btnExportONNX.clicked.connect(self.btnExportONNX_clicked)

        layout_file_btn.addWidget(self.btnOpenONNX)
        layout_file_btn.addWidget(self.btnImportONNX)
        layout_file_btn.addWidget(self.btnExportONNX)
        self.layout_main_properties.addLayout(layout_file_btn)

        # Operator Button
        layout_operator_btn = QtWidgets.QVBoxLayout()


        self.btnChangeOpset = QtWidgets.QPushButton("Change Opset (soc4onnx)")
        self.btnChangeOpset.setEnabled(True)
        self.btnChangeOpset.clicked.connect(self.btnChangeOpset_clicked)

        self.btnAddNode = QtWidgets.QPushButton("Add Node (sna4onnx)")
        self.btnAddNode.setEnabled(True)
        self.btnAddNode.clicked.connect(self.btnAddNode_clicked)

        self.btnGenerateOperator = QtWidgets.QPushButton("Generate Operator (sog4onnx)")
        self.btnGenerateOperator.setEnabled(True)
        self.btnGenerateOperator.clicked.connect(self.btnGenerateOperator_clicked)

        self.btnDelNode = QtWidgets.QPushButton("Delete Node (snd4onnx)")
        self.btnDelNode.setEnabled(True)
        self.btnDelNode.clicked.connect(self.btnDelNode_clicked)

        self.btnConstShrink = QtWidgets.QPushButton("Const Shrink (scs4onnx)")
        self.btnConstShrink.setEnabled(True)
        self.btnConstShrink.clicked.connect(self.btnConstShrink_clicked)

        self.btnChannelConvert = QtWidgets.QPushButton("Channel Convert (scc4onnx)")
        self.btnChannelConvert.setEnabled(True)
        self.btnChannelConvert.clicked.connect(self.btnChannelConvert_clicked)

        layout_operator_btn.addWidget(self.btnChangeOpset)
        layout_operator_btn.addWidget(self.btnAddNode)
        layout_operator_btn.addWidget(self.btnGenerateOperator)
        layout_operator_btn.addWidget(self.btnDelNode)
        layout_operator_btn.addWidget(self.btnConstShrink)
        layout_operator_btn.addWidget(self.btnChannelConvert)
        self.layout_main_properties.addSpacerItem(QtWidgets.QSpacerItem(self._sidemenu_width, 10))
        self.layout_main_properties.addLayout(layout_operator_btn)

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

        self.lbl_graph_opset.setText(f"opset: {self.graph.opset}")
        self.lbl_graph_name.setText(f"name: {self.graph.name}")
        self.lbl_graph_doc_string.setText(f"doc_string: {self.graph.doc_string}")

        # if self.nodes_tree is not None:
        #     self.nodes_tree.hide()
        #     self.layout_node_properties.removeWidget(self.nodes_tree)
        #     del self.nodes_tree
        # self.nodes_tree = self.create_nodes_tree(self.graph)
        # self.layout_node_properties.addWidget(self.nodes_tree)

        if self.properties_bin is not None:
            self.properties_bin.hide()
            self.layout_node_properties.removeWidget(self.properties_bin)
            del self.properties_bin
        self.properties_bin = self.create_properties_bin(self.graph)
        self.layout_node_properties.addWidget(self.properties_bin)

        cursor.setShape(QtCore.Qt.ArrowCursor)
        self.setCursor(cursor)


    def load_graph(self, onnx_model:onnx.ModelProto=None, onnx_model_path:str=None, graph:ONNXNodeGraph=None)->ONNXNodeGraph:

        cursor = self.cursor()
        cur_cursor = cursor.shape()
        cursor.setShape(QtCore.Qt.BusyCursor)
        self.setCursor(cursor)

        if not onnx_model and not onnx_model_path:
            node_graph = ONNXNodeGraph(name="onnx_graph_qt",
                                       opset=DEFAULT_OPSET,
                                       doc_string=None,
                                       import_domains=None)
            return node_graph

        onnx_graph = None
        if onnx_model:
            onnx_graph = gs.import_onnx(onnx_model)
        elif onnx_model_path:
            self.setWindowTitle(os.path.basename(onnx_model_path))
            onnx_graph = gs.import_onnx(onnx.load(onnx_model_path))

        # create graph controller.
        if graph is None:
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
        graph = self.load_graph(onnx_model_path=file_name)
        self.update_graph(graph)

        self.btnImportONNX.setEnabled(True)
        self.btnExportONNX.setEnabled(True)

    def btnImportONNX_clicked(self, e: bool):
        file_name, exp = QtWidgets.QFileDialog.getOpenFileName(
                            self,
                            caption="Open ONNX Model File",
                            directory=os.path.abspath(os.curdir),
                            filter="*.onnx")
        if not file_name:
            return
        print(f"Import: {file_name}")
        graph = self.load_graph(onnx_model_path=file_name, graph=self.graph)
        self.update_graph(graph)

    def btnExportONNX_clicked(self, e:bool):
        file_name, exp = QtWidgets.QFileDialog.getSaveFileName(
                            self,
                            caption="Export ONNX Model File",
                            directory=os.path.abspath(os.curdir),
                            filter="*.onnx")
        if not file_name:
            return
        print(f"Export: {file_name}.")

    def btnAddNode_clicked(self, e:bool):
        w = AddNodeWidgets(self)
        if w.exec_():
            props = w.get_properties()
            onnx_model:onnx.ModelProto = onnx_tools_add(
                onnx_graph=self.graph.to_onnx(non_verbose=False), **props._asdict())

            graph = self.load_graph(onnx_model=onnx_model, graph=self.graph)
            self.update_graph(graph)

    def btnGenerateOperator_clicked(self, e:bool):
        print(sys._getframe().f_code.co_name)

    def btnDelNode_clicked(self, e:bool):
        print(sys._getframe().f_code.co_name)

    def btnConstShrink_clicked(self, e:bool):
        print(sys._getframe().f_code.co_name)

    def btnChangeOpset_clicked(self, e:bool):
        w = ChangeOpsetWidget(parent=self, current_opset=self.graph.opset)
        if w.exec_():
            props = w.get_properties()
            onnx_model:onnx.ModelProto = onnx_tools_op_change(
                opset=int(props.opset),
                onnx_graph=self.graph.to_onnx(non_verbose=False)
            )
            graph = self.load_graph(onnx_model=onnx_model)
            self.update_graph(graph)
        print(sys._getframe().f_code.co_name)

    def btnChannelConvert_clicked(self, e:bool):
        w = ChangeChannelWidgets(parent=self)
        if w.exec_():
            props = w.get_properties()
            onnx_model:onnx.ModelProto = onnx_tools_order_conversion(
                onnx_graph=self.graph.to_onnx(non_verbose=False),
                **props._asdict()
            )
            graph = self.load_graph(onnx_model=onnx_model)
            self.update_graph(graph)
        print(sys._getframe().f_code.co_name)

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
    onnx_file = "/media/ubuntu/my_passport/workspace/onnx_graph_qt/sample_nodegraphqt/mobilenetv2-7.onnx"

    main_window = MainWindow(onnx_model_path=onnx_file)
    main_window.show()

    app.exec_()