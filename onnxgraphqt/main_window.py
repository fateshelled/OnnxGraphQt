import sys, os, io
import time

from PySide2 import QtCore, QtWidgets, QtGui
from NodeGraphQt import NodeGraph, NodesTreeWidget, PropertiesBinWidget
from NodeGraphQt.widgets.node_graph import NodeGraphWidget

import onnx
import onnx_graphsurgeon as gs

from snc4onnx import combine as onnx_tools_combine       #
from sne4onnx import extraction as onnx_tools_extraction #
from snd4onnx import remove as onnx_tools_deletion       # done
from scs4onnx import shrinking as onnx_tools_shrinking   # done.
from sog4onnx import generate as onnx_tools_generate     # done.
from sam4onnx import modify as onnx_tools_modify         # done
from soc4onnx import change as onnx_tools_op_change      # done.
from scc4onnx import order_conversion as onnx_tools_order_conversion # done.
from sna4onnx import add as onnx_tools_add               # done.
from sbi4onnx import initialize as onnx_tools_batchsize_initialize #
from onnx2json.onnx2json import convert as onnx_tools_onnx2json    #
from json2onnx.json2onnx import convert as onnx_tools_json2onnx    #

from widgets_menubar import MenuBarWidget
from widgets_message_box import MessageBox
from widgets_extract_network import ExtractNetworkWidgets
from widgets_add_node import AddNodeWidgets
from widgets_change_opset import ChangeOpsetWidget
from widgets_change_channel import ChangeChannelWidgets
from widgets_constant_shrink import ConstantShrinkWidgets
from widgets_modify_attrs import ModifyAttrsWidgets
from widgets_delete_node import DeleteNodeWidgets
from widgets_generate_operator import GenerateOperatorWidgets

from onnx_node_graph import ONNXNodeGraph
from utils.opset import DEFAULT_OPSET


class MainWindow(QtWidgets.QMainWindow):
    _default_window_width = 1200
    _default_window_height = 800
    _sidemenu_width = 400

    def __init__(self, onnx_model_path="", parent=None):
        super(MainWindow, self).__init__(parent)

        self.graph = self.load_graph(onnx_model_path=onnx_model_path)
        self.graph_widget = self.graph.widget
        self.properties_bin: PropertiesBinWidget = None

        self.init_ui()

        if onnx_model_path:
            # self.btnImportONNX.setEnabled(True)
            self.btnExportONNX.setEnabled(True)

    def init_ui(self):
        # Window size
        self.setGeometry(0, 0, self._default_window_width, self._default_window_height)

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
        self.lbl_graph_name = QtWidgets.QLabel()
        self.lbl_graph_doc_string = QtWidgets.QLabel()

        layout_lbl.addWidget(self.lbl_graph_name)
        layout_lbl.addWidget(self.lbl_graph_opset)
        layout_lbl.addWidget(self.lbl_graph_doc_string)
        self.layout_main_properties.addLayout(layout_lbl)

        # File Button
        layout_file_btn = QtWidgets.QHBoxLayout()
        self.btnOpenONNX = QtWidgets.QPushButton("open")
        self.btnOpenONNX.clicked.connect(self.btnOpenONNX_clicked)

        # self.btnImportONNX = QtWidgets.QPushButton("import")
        # self.btnImportONNX.setEnabled(False)
        # self.btnImportONNX.clicked.connect(self.btnImportONNX_clicked)

        self.btnExportONNX = QtWidgets.QPushButton("export")
        self.btnExportONNX.setEnabled(False)
        self.btnExportONNX.clicked.connect(self.btnExportONNX_clicked)

        self.btnAutoLayout = QtWidgets.QPushButton("auto layout")
        self.btnAutoLayout.clicked.connect(self.btnAutoLayout_clicked)

        layout_file_btn.addWidget(self.btnOpenONNX)
        # layout_file_btn.addWidget(self.btnImportONNX)
        layout_file_btn.addWidget(self.btnExportONNX)
        layout_file_btn.addWidget(self.btnAutoLayout)
        self.layout_main_properties.addLayout(layout_file_btn)

        # Operator Button
        layout_operator_btn = QtWidgets.QVBoxLayout()

        self.btnCombineNetwork = QtWidgets.QPushButton("Combine Network (snc4onnx)")
        self.btnCombineNetwork.setEnabled(False)
        self.btnCombineNetwork.clicked.connect(self.btnCombineNetwork_clicked)

        self.btnExtractNetwork = QtWidgets.QPushButton("Extract Network (sne4onnx)")
        self.btnExtractNetwork.clicked.connect(self.btnExtractNetwork_clicked)

        self.btnDelNode = QtWidgets.QPushButton("Delete Node (snd4onnx)")
        self.btnDelNode.clicked.connect(self.btnDelNode_clicked)

        self.btnConstShrink = QtWidgets.QPushButton("Const Shrink (scs4onnx)")
        self.btnConstShrink.clicked.connect(self.btnConstShrink_clicked)

        self.btnGenerateOperator = QtWidgets.QPushButton("Generate Operator (sog4onnx)")
        self.btnGenerateOperator.clicked.connect(self.btnGenerateOperator_clicked)

        self.btnModifyAttrConst = QtWidgets.QPushButton("Modify Attribute and Constant (sam4onnx)")
        self.btnModifyAttrConst.clicked.connect(self.btnModifyAttrConst_clicked)

        self.btnChangeOpset = QtWidgets.QPushButton("Change Opset (soc4onnx)")
        self.btnChangeOpset.clicked.connect(self.btnChangeOpset_clicked)

        self.btnChannelConvert = QtWidgets.QPushButton("Channel Convert (scc4onnx)")
        self.btnChannelConvert.clicked.connect(self.btnChannelConvert_clicked)

        self.btnAddNode = QtWidgets.QPushButton("Add Node (sna4onnx)")
        self.btnAddNode.clicked.connect(self.btnAddNode_clicked)

        self.btnInitializeBatchSize = QtWidgets.QPushButton("Initialize Batchsize (sbi4onnx)")
        self.btnInitializeBatchSize.setEnabled(False)
        self.btnInitializeBatchSize.clicked.connect(self.btnInitializeBatchSize_clicked)

        layout_operator_btn.addWidget(self.btnCombineNetwork)
        layout_operator_btn.addWidget(self.btnExtractNetwork)
        layout_operator_btn.addWidget(self.btnDelNode)
        layout_operator_btn.addWidget(self.btnConstShrink)
        layout_operator_btn.addWidget(self.btnGenerateOperator)
        layout_operator_btn.addWidget(self.btnModifyAttrConst)
        layout_operator_btn.addWidget(self.btnChangeOpset)
        layout_operator_btn.addWidget(self.btnChannelConvert)
        layout_operator_btn.addWidget(self.btnAddNode)
        layout_operator_btn.addWidget(self.btnInitializeBatchSize)

        self.layout_main_properties.addSpacerItem(QtWidgets.QSpacerItem(self._sidemenu_width, 10))
        self.layout_main_properties.addLayout(layout_operator_btn)

        # ONNXNodeGraph
        self.update_graph(self.graph)


    def update_graph(self, graph: ONNXNodeGraph):

        t0 = time.time()
        self.set_cursor_busy()

        self.graph_widget.hide()
        self.layout_graph.removeWidget(self.graph_widget)
        del self.graph_widget
        del self.graph

        self.graph = graph
        self.graph_widget = graph.widget
        self.layout_graph.addWidget(graph.widget)
        self.graph.auto_layout(push_undo=False)
        self.graph.fit_to_selection()

        self.lbl_graph_opset.setText(f"opset: {self.graph.opset}")
        self.lbl_graph_name.setText(f"name: {self.graph.name}")
        self.lbl_graph_doc_string.setText(f"doc_string: {self.graph.doc_string}")

        if self.properties_bin is not None:
            self.properties_bin.hide()
            self.layout_node_properties.removeWidget(self.properties_bin)
            del self.properties_bin
        self.properties_bin = self.create_properties_bin(self.graph)
        self.layout_node_properties.addWidget(self.properties_bin)

        self.set_sidemenu_buttons_enabled(True)

        self.set_cursor_arrow()
        dt0 = time.time() - t0
        print(f"update graph: {dt0}s")

    def set_cursor_busy(self):
        cursor = self.cursor()
        cursor.setShape(QtCore.Qt.BusyCursor)
        self.setCursor(cursor)

    def set_cursor_arrow(self):
        cursor = self.cursor()
        cursor.setShape(QtCore.Qt.ArrowCursor)
        self.setCursor(cursor)

    def set_font_bold(self, button: QtWidgets.QPushButton, bold=True):
        f = button.font()
        f.setBold(bold)
        button.setFont(f)

    def set_sidemenu_buttons_enabled(self, enable=True, current_button: QtWidgets.QPushButton=None):

        if enable:
            self.btnOpenONNX.setEnabled(True)
            self.btnAutoLayout.setEnabled(True)

            if self.graph.node_count() > 0:
                self.btnExportONNX.setEnabled(True)

                # self.btnCombineNetwork.setEnabled(False)
                self.btnExtractNetwork.setEnabled(True)
                self.btnDelNode.setEnabled(True)
                self.btnConstShrink.setEnabled(True)
                self.btnModifyAttrConst.setEnabled(True)
                self.btnChangeOpset.setEnabled(True)
                self.btnChannelConvert.setEnabled(True)
                # self.btnInitializeBatchSize.setEnabled(False)

                self.btnGenerateOperator.setEnabled(True)
                self.btnAddNode.setEnabled(True)
            else:
                self.btnExportONNX.setEnabled(False)

                # self.btnCombineNetwork.setEnabled(False)
                self.btnExtractNetwork.setEnabled(False)
                self.btnDelNode.setEnabled(False)
                self.btnConstShrink.setEnabled(False)
                self.btnModifyAttrConst.setEnabled(False)
                self.btnChangeOpset.setEnabled(False)
                self.btnChannelConvert.setEnabled(False)
                # self.btnInitializeBatchSize.setEnabled(False)

                self.btnGenerateOperator.setEnabled(True)
                self.btnAddNode.setEnabled(True)
            self.properties_bin.setEnabled(True)
        else:
            self.btnOpenONNX.setEnabled(False)
            self.btnAutoLayout.setEnabled(False)
            self.btnExportONNX.setEnabled(False)
            self.btnCombineNetwork.setEnabled(False)
            self.btnExtractNetwork.setEnabled(False)
            self.btnDelNode.setEnabled(False)
            self.btnConstShrink.setEnabled(False)
            self.btnModifyAttrConst.setEnabled(False)
            self.btnChangeOpset.setEnabled(False)
            self.btnChannelConvert.setEnabled(False)
            self.btnInitializeBatchSize.setEnabled(False)
            self.btnGenerateOperator.setEnabled(False)
            self.btnAddNode.setEnabled(False)
            self.properties_bin.setEnabled(False)

        self.current_button = current_button
        if current_button:
            current_button.setEnabled(True)

    def set_current_process_button(self):
        pass

    def load_graph(self, onnx_model:onnx.ModelProto=None, onnx_model_path:str=None, graph:ONNXNodeGraph=None)->ONNXNodeGraph:

        t0 = time.time()
        self.set_cursor_busy()

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

        node_graph.load_onnx_graph(onnx_graph)

        self.set_cursor_arrow()
        dt0 = time.time() - t0
        print(f"load graph: {dt0}s")
        return node_graph

    def create_properties_bin(self, graph: ONNXNodeGraph):
        properties_bin = PropertiesBinWidget(node_graph=graph)
        properties_bin.set_limit(1)
        return properties_bin

    def btnOpenONNX_clicked(self, e:bool):
        self.set_font_bold(self.btnOpenONNX, True)
        file_name, exp = QtWidgets.QFileDialog.getOpenFileName(
                            self,
                            caption="Open ONNX Model File",
                            directory=os.path.abspath(os.curdir),
                            filter="*.onnx")
        if not file_name:
            self.set_font_bold(self.btnOpenONNX, False)
            return
        print(f"Open: {file_name}")
        time.sleep(0.01)
        graph = self.load_graph(onnx_model_path=file_name)
        self.update_graph(graph)

        # self.btnImportONNX.setEnabled(True)
        self.btnExportONNX.setEnabled(True)
        self.set_font_bold(self.btnOpenONNX, False)

    # def btnImportONNX_clicked(self, e: bool):
    #     file_name, exp = QtWidgets.QFileDialog.getOpenFileName(
    #                         self,
    #                         caption="Open ONNX Model File",
    #                         directory=os.path.abspath(os.curdir),
    #                         filter="*.onnx")
    #     if not file_name:
    #         return
    #     print(f"Import: {file_name}")
    #     graph = self.load_graph(onnx_model_path=file_name, graph=self.graph)
    #     self.update_graph(graph)

    def btnExportONNX_clicked(self, e:bool):
        self.set_font_bold(self.btnExportONNX, True)
        file_name, exp = QtWidgets.QFileDialog.getSaveFileName(
                            self,
                            caption="Export ONNX Model File",
                            directory=os.path.abspath(os.curdir),
                            filter="*.onnx")
        if not file_name:
            self.set_font_bold(self.btnExportONNX, False)
            return
        self.graph.export(file_name)
        print(f"Export: {file_name}.")
        MessageBox.info(
            ["Success.", f"Export to {file_name}."],
            "Export ONNX",
            parent=self)
        self.set_font_bold(self.btnExportONNX, False)

    def btnAutoLayout_clicked(self, e:bool):
        self.set_font_bold(self.btnAutoLayout, True)
        self.set_cursor_busy()
        self.set_sidemenu_buttons_enabled(False)

        self.graph.auto_layout(push_undo=True)

        self.set_sidemenu_buttons_enabled(True)
        self.set_cursor_arrow()
        self.set_font_bold(self.btnAutoLayout, False)

    def btnAddNode_clicked(self, e:bool):
        btn = self.btnAddNode
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)

        self.current_widgets = AddNodeWidgets(self)
        self.current_widgets.show()
        if self.current_widgets.exec_():
            try:
                props = self.current_widgets.get_properties()
                onnx_model:onnx.ModelProto = onnx_tools_add(
                    onnx_graph=self.graph.to_onnx(non_verbose=True),
                    non_verbose=False,
                    **props._asdict(),
                )

                graph = self.load_graph(onnx_model=onnx_model, graph=self.graph)
                self.update_graph(graph)
                MessageBox.info(
                    f"complete.",
                    "Add None",
                    parent=self)
            except BaseException as e:
                MessageBox.error(
                    str(e),
                    "Add None",
                    parent=self
                )
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def btnConstShrink_clicked(self, e:bool):
        btn = self.btnConstShrink
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)

        self.current_widgets = ConstantShrinkWidgets(parent=self)
        self.current_widgets.show()
        if self.current_widgets.exec_():
            try:
                props = self.current_widgets.get_properties()
                onnx_model:onnx.ModelProto = None
                onnx_model, _ = onnx_tools_shrinking(
                    onnx_graph=self.graph.to_onnx(non_verbose=True),
                    non_verbose=False,
                    **props._asdict()
                )
                graph = self.load_graph(onnx_model=onnx_model)
                self.update_graph(graph)
                MessageBox.info(
                    f"complete.",
                    "Const Shrink",
                    parent=self)
            except BaseException as e:
                MessageBox.error(
                    str(e),
                    "Const Shrink",
                    parent=self
                )
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def btnChangeOpset_clicked(self, e:bool):
        btn = self.btnChangeOpset
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)

        self.current_widgets = ChangeOpsetWidget(parent=self, current_opset=self.graph.opset)
        old_opset = self.graph.opset
        self.current_widgets.show()
        if self.current_widgets.exec_():
            try:
                props = self.current_widgets.get_properties()
                new_opset = int(props.opset)
                if old_opset == new_opset:
                    MessageBox.warn(
                        f"opset num is same. not change.",
                        "Change Opset",
                        parent=self)
                    self.set_sidemenu_buttons_enabled(True)
                    return
                onnx_model:onnx.ModelProto = onnx_tools_op_change(
                    opset=new_opset,
                    onnx_graph=self.graph.to_onnx(non_verbose=True),
                    non_verbose=False,
                )
                graph = self.load_graph(onnx_model=onnx_model)
                self.update_graph(graph)
                MessageBox.info(
                    f"Change opset {old_opset} to {new_opset}.",
                    "Change Opset",
                    parent=self)
            except BaseException as e:
                MessageBox.error(
                    str(e),
                    "Change Opset",
                    parent=self
                )
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def btnChannelConvert_clicked(self, e:bool):
        btn = self.btnChannelConvert
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)

        self.current_widgets = ChangeChannelWidgets(graph=self.graph.to_data(), parent=self)
        self.current_widgets.show()
        if self.current_widgets.exec_():
            try:
                props = self.current_widgets.get_properties()
                onnx_model:onnx.ModelProto = onnx_tools_order_conversion(
                    onnx_graph=self.graph.to_onnx(non_verbose=True),
                    non_verbose=False,
                    **props._asdict()
                )
                graph = self.load_graph(onnx_model=onnx_model)
                self.update_graph(graph)
                MessageBox.info(
                    f"complete.",
                    "Channel Convert",
                    parent=self)
            except BaseException as e:
                MessageBox.error(
                    str(e),
                    "Channel Convert",
                    parent=self
                )
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def btnCombineNetwork_clicked(self, e:bool):
        self.set_sidemenu_buttons_enabled(False)
        print(sys._getframe().f_code.co_name)
        self.set_sidemenu_buttons_enabled(True)

    def btnExtractNetwork_clicked(self, e:bool):
        btn = self.btnExtractNetwork
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)

        self.current_widgets = ExtractNetworkWidgets(graph=self.graph.to_data(), parent=self)
        self.current_widgets.show()
        if self.current_widgets.exec_():
            try:
                props = self.current_widgets.get_properties()
                onnx_graph=self.graph.to_onnx(non_verbose=True)
                print_msg = ""
                with io.StringIO() as f:
                    sys.stdout = f
                    onnx_model:onnx.ModelProto = onnx_tools_extraction(
                        onnx_graph=onnx_graph,
                        non_verbose=False,
                        **props._asdict(),
                    )
                    sys.stdout = sys.__stdout__
                    print_msg = f.getvalue()
                if print_msg:
                    MessageBox.warn(
                        print_msg,
                        "Extract Network",
                        parent=self)
                graph = self.load_graph(onnx_model=onnx_model)
                self.update_graph(graph)
                MessageBox.info(
                    f"complete.",
                    "Extract Network",
                    parent=self)
            except BaseException as e:
                MessageBox.error(
                    str(e),
                    "Extract Network",
                    parent=self
                )
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def btnGenerateOperator_clicked(self, e:bool):
        btn = self.btnGenerateOperator
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)

        self.current_widgets = GenerateOperatorWidgets(opset=self.graph.opset, parent=self)
        self.current_widgets.show()
        if self.current_widgets.exec_():
            try:
                props = self.current_widgets.get_properties()
                onnx_model:onnx.ModelProto = onnx_tools_generate(
                    non_verbose=False,
                    **props._asdict()
                )
                graph = self.load_graph(onnx_model=onnx_model, graph=self.graph)
                self.update_graph(graph)
                MessageBox.info(
                    f"complete.",
                    "Generate Operator",
                    parent=self)
            except BaseException as e:
                MessageBox.error(
                    str(e),
                    "Generate Operator",
                    parent=self
                )
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def btnDelNode_clicked(self, e:bool):
        btn = self.btnDelNode
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)

        self.current_widgets = DeleteNodeWidgets(parent=self, graph=self.graph.to_data())
        self.current_widgets.show()
        if self.current_widgets.exec_():
            try:
                props = self.current_widgets.get_properties()
                onnx_graph=self.graph.to_onnx(non_verbose=True)
                print_msg = ""
                with io.StringIO() as f:
                    sys.stdout = f
                    onnx_model:onnx.ModelProto = onnx_tools_deletion(
                        onnx_graph=onnx_graph,
                        **props._asdict(),
                    )
                    sys.stdout = sys.__stdout__
                    print_msg = f.getvalue()
                if print_msg:
                    MessageBox.warn(
                        print_msg,
                        "Delete Node",
                        parent=self)
                graph = self.load_graph(onnx_model=onnx_model)
                self.update_graph(graph)
                MessageBox.info(
                    f"complete.",
                    "Delete Node",
                    parent=self)
            except BaseException as e:
                MessageBox.error(
                    str(e),
                    "Delete Node",
                    parent=self
                )
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def btnModifyAttrConst_clicked(self, e:bool):
        btn = self.btnModifyAttrConst
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)

        self.current_widgets = ModifyAttrsWidgets(parent=self, graph=self.graph.to_data())
        self.current_widgets.show()
        if self.current_widgets.exec_():
            try:
                props = self.current_widgets.get_properties()
                onnx_graph=self.graph.to_onnx(non_verbose=True)
                onnx_model:onnx.ModelProto = onnx_tools_modify(
                    onnx_graph=onnx_graph,
                    non_verbose=False,
                    **props._asdict()
                )
                graph = self.load_graph(onnx_model=onnx_model)
                self.update_graph(graph)
                MessageBox.info(
                    f"complete.",
                    "Modify Attributes and Constants",
                    parent=self)
            except BaseException as e:
                MessageBox.error(
                    str(e),
                    "Modify Attributes and Constants",
                    parent=self
                )
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def btnInitializeBatchSize_clicked(self, e:bool):
        self.set_sidemenu_buttons_enabled(False)
        print(sys._getframe().f_code.co_name)
        self.set_sidemenu_buttons_enabled(True)

    def exit(self):
        self.close()
        sys.exit(0)


if __name__ == "__main__":
    import signal
    import os, time
    from splash_screen import create_screen, create_screen_progressbar
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])

    base_dir = os.path.dirname(__file__)
    # onnx_file = os.path.join(base_dir, "data", "mobilenetv2-12-int8.onnx")
    onnx_file = os.path.join(base_dir, "data", "mobilenetv2-7.onnx")

    USE_SPLASH_SCREEN = False
    if USE_SPLASH_SCREEN:
        splash = create_screen()
        splash.show()
        time.sleep(0.05)
        msg = ""
        msg_align = QtCore.Qt.AlignBottom
        msg_color = QtGui.QColor.fromRgb(255, 255, 255)
        if onnx_file:
            msg = f"loading [{os.path.basename(onnx_file)}]"
        else:
            msg = "loading..."
        splash.showMessage(msg, alignment=msg_align, color=msg_color)
        print(msg)

        app.processEvents()

    main_window = MainWindow(onnx_model_path=onnx_file)

    if USE_SPLASH_SCREEN:
        msg = "load complete."
        splash.showMessage(msg, alignment=msg_align, color=msg_color)
        print(msg)
        time.sleep(0.1)
        app.processEvents()
        splash.finish(main_window)

    main_window.show()

    app.exec_()