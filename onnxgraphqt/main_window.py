import sys, os, io
import time

from PySide2 import QtCore, QtWidgets, QtGui
import onnx
import onnx_graphsurgeon as gs

from NodeGraphQt.widgets.node_graph import NodeGraphWidget
from snc4onnx import combine as onnx_tools_combine
from sne4onnx import extraction as onnx_tools_extraction
from snd4onnx import remove as onnx_tools_deletion
from scs4onnx import shrinking as onnx_tools_shrinking
from sog4onnx import generate as onnx_tools_generate
from sam4onnx import modify as onnx_tools_modify
from soc4onnx import change as onnx_tools_op_change
from scc4onnx import order_conversion as onnx_tools_order_conversion
from sna4onnx import add as onnx_tools_add
from sbi4onnx import initialize as onnx_tools_batchsize_initialize
from sor4onnx import rename as onnx_tools_rename
from onnx2json.onnx2json import convert as onnx_tools_onnx2json
from json2onnx.json2onnx import convert as onnx_tools_json2onnx
from ssc4onnx import structure_check

from widgets.widgets_menubar import MenuBarWidget, Menu, Separator, SubMenu
from widgets.widgets_message_box import MessageBox
from widgets.widgets_combine_network import CombineNetworkWidgets
from widgets.widgets_extract_network import ExtractNetworkWidgets
from widgets.widgets_add_node import AddNodeWidgets
from widgets.widgets_change_opset import ChangeOpsetWidget
from widgets.widgets_change_channel import ChangeChannelWidgets
from widgets.widgets_constant_shrink import ConstantShrinkWidgets
from widgets.widgets_modify_attrs import ModifyAttrsWidgets
from widgets.widgets_delete_node import DeleteNodeWidgets
from widgets.widgets_generate_operator import GenerateOperatorWidgets
from widgets.widgets_initialize_batchsize import InitializeBatchsizeWidget
from widgets.widgets_rename_op import RenameOpWidget
from widgets.widgets_node_search import NodeSearchWidget
from widgets.widgets_inference_test import InferenceTestWidgets

from widgets.custom_properties_bin import CustomPropertiesBinWidget

from graph.onnx_node_graph import ONNXNodeGraph
from utils.opset import DEFAULT_OPSET
from utils.color import remove_PrintColor
from utils.widgets import BASE_FONT_SIZE, LARGE_FONT_SIZE, set_font, createIconButton


class MainWindow(QtWidgets.QMainWindow):
    _default_window_width = 1200
    _default_window_height = 800
    _sidemenu_width = 400

    def __init__(self, onnx_model_path="", parent=None):
        super(MainWindow, self).__init__(parent)

        self.graph: ONNXNodeGraph = None
        self.load_graph()
        self.graph_widget: NodeGraphWidget = self.graph.widget

        self.properties_bin: CustomPropertiesBinWidget = None
        self.init_ui()

        ext = os.path.splitext(onnx_model_path)[-1]

        if ext == ".onnx":
            self.load_graph(onnx_model_path=onnx_model_path, clear_undo_stack=True, push_undo=False)
        elif ext == ".json":
            onnx_graph = onnx_tools_json2onnx(input_json_path=onnx_model_path)
            self.load_graph(onnx_model=onnx_graph, clear_undo_stack=True, push_undo=False)

        self.update_graph()

    def init_ui(self):
        # Window size
        self.setGeometry(0, 0, self._default_window_width, self._default_window_height)

        icon_dir = os.path.join(os.path.dirname(__file__), "data/icon")

        window_icon = QtGui.QIcon(os.path.join(icon_dir, "../splash.png"))
        self.setWindowIcon(window_icon)

        # MenuBar
        menu_list = [
            Menu(
                "File (&F)",
                [
                    SubMenu("Open", self.btnOpenONNX_clicked, None),
                    SubMenu("Export", self.btnExportONNX_clicked, None),
                    SubMenu("Export PNG", self.btnExportPNG_clicked, None),
                    Separator(),
                    SubMenu("Exit", self.exit, None),
                ]
            ),
            Menu(
                "View (&V)",
                [
                    SubMenu("&Search", self.btnSearch_clicked, None),
                    SubMenu("Auto &Layout", self.btnAutoLayout_clicked, None),
                ]
            ),
            Menu(
                "Tools (&T)",
                [
                    SubMenu("Inference Test", self.btnInferenceTest_clicked, None),
                ]
            ),
        ]
        self.menu_bar = MenuBarWidget(menu_list=menu_list)
        set_font(self, BASE_FONT_SIZE)
        for key, action in self.menu_bar.menu_actions.items():
            set_font(action, BASE_FONT_SIZE)
        self.setMenuBar(self.menu_bar)
        # Search Widget
        self.search_widget = NodeSearchWidget(self.graph, parent=self)

        # Main Layout
        # Fixed side menu size.
        self.layout_graph = QtWidgets.QStackedLayout()
        self.layout_graph.addWidget(self.graph.widget)

        self.layout_base = QtWidgets.QHBoxLayout()

        # Enable Drag&Drop
        self.setAcceptDrops(True)
        self.graph._viewer.dropEvent = self.dropEvent

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
        layout_lbl = QtWidgets.QFormLayout()

        lbl_graph_opset_ = QtWidgets.QLabel("opset")
        lbl_graph_name_ = QtWidgets.QLabel("name")
        lbl_graph_doc_string_ = QtWidgets.QLabel("doc_string")
        lbl_graph_ir_version_ = QtWidgets.QLabel("ir_version")
        self.set_font_bold(lbl_graph_opset_)
        self.set_font_bold(lbl_graph_name_)
        self.set_font_bold(lbl_graph_doc_string_)
        self.set_font_bold(lbl_graph_ir_version_)
        self.lbl_graph_opset = QtWidgets.QLabel()
        self.lbl_graph_name = QtWidgets.QLabel()
        self.lbl_graph_doc_string = QtWidgets.QLabel()
        self.lbl_graph_ir_version = QtWidgets.QLabel()

        layout_lbl.addRow(lbl_graph_name_, self.lbl_graph_name)
        layout_lbl.addRow(lbl_graph_opset_, self.lbl_graph_opset)
        layout_lbl.addRow(lbl_graph_ir_version_, self.lbl_graph_ir_version)
        layout_lbl.addRow(lbl_graph_doc_string_, self.lbl_graph_doc_string)
        self.layout_main_properties.addLayout(layout_lbl)

        # Operator Button
        layout_operator_btn = QtWidgets.QGridLayout()
        for i in range(6):
            layout_operator_btn.setRowMinimumHeight(i, 45)

        self.btnCombineNetwork = createIconButton("Combine Network\n(snc4onnx)", os.path.join(icon_dir, "snc4onnx.png"))
        self.btnCombineNetwork.clicked.connect(self.btnCombineNetwork_clicked)

        self.btnExtractNetwork = createIconButton("Extract Network\n(sne4onnx)", os.path.join(icon_dir, "sne4onnx.png"))
        self.btnExtractNetwork.clicked.connect(self.btnExtractNetwork_clicked)

        self.btnDelNode = createIconButton("Delete Node\n(snd4onnx)", os.path.join(icon_dir, "snd4onnx.png"))
        self.btnDelNode.clicked.connect(self.btnDelNode_clicked)

        self.btnConstShrink = createIconButton("Const Shrink\n(scs4onnx)", os.path.join(icon_dir, "scs4onnx.png"))
        self.btnConstShrink.clicked.connect(self.btnConstShrink_clicked)

        self.btnGenerateOperator = createIconButton("Generate Operator\n(sog4onnx)", os.path.join(icon_dir, "sog4onnx.png"))
        self.btnGenerateOperator.clicked.connect(self.btnGenerateOperator_clicked)

        self.btnModifyAttrConst = createIconButton("Mod Attr and Const\n(sam4onnx)", os.path.join(icon_dir, "sam4onnx.png"))
        self.btnModifyAttrConst.clicked.connect(self.btnModifyAttrConst_clicked)

        self.btnChangeOpset = createIconButton("Change Opset\n(soc4onnx)", os.path.join(icon_dir, "soc4onnx.png"))
        self.btnChangeOpset.clicked.connect(self.btnChangeOpset_clicked)

        self.btnChannelConvert = createIconButton("Channel Convert\n(scc4onnx)", os.path.join(icon_dir, "scc4onnx.png"))
        self.btnChannelConvert.clicked.connect(self.btnChannelConvert_clicked)

        self.btnAddNode = createIconButton("Add Node\n(sna4onnx)", os.path.join(icon_dir, "sna4onnx.png"))
        self.btnAddNode.clicked.connect(self.btnAddNode_clicked)

        self.btnInitializeBatchSize = createIconButton("Initialize Batchsize\n(sbi4onnx)", os.path.join(icon_dir, "sbi4onnx.png"))
        self.btnInitializeBatchSize.clicked.connect(self.btnInitializeBatchSize_clicked)

        self.btnRenameOp = createIconButton("Rename Op\n(sor4onnx)", os.path.join(icon_dir, "sor4onnx.png"))
        self.btnRenameOp.clicked.connect(self.btnRenameOp_clicked)

        layout_operator_btn.addWidget(self.btnGenerateOperator, 0, 0)
        layout_operator_btn.addWidget(self.btnAddNode, 0, 1)
        layout_operator_btn.addWidget(self.btnCombineNetwork)
        layout_operator_btn.addWidget(self.btnExtractNetwork)
        layout_operator_btn.addWidget(self.btnRenameOp)
        layout_operator_btn.addWidget(self.btnModifyAttrConst)
        layout_operator_btn.addWidget(self.btnChannelConvert)
        layout_operator_btn.addWidget(self.btnInitializeBatchSize)
        layout_operator_btn.addWidget(self.btnChangeOpset)
        layout_operator_btn.addWidget(self.btnConstShrink)
        layout_operator_btn.addWidget(self.btnDelNode)

        self.layout_main_properties.addSpacerItem(QtWidgets.QSpacerItem(self._sidemenu_width, 10))
        self.layout_main_properties.addLayout(layout_operator_btn)

    def update_graph(self, update_layout=True):

        t0 = time.time()
        self.set_cursor_busy()

        self.graph.update_pipe_paint()
        self.graph.auto_layout(push_undo=False)

        if update_layout:
            self.graph.fit_to_selection()
        self.graph.reset_selection()

        self.lbl_graph_opset.setText(f"{self.graph.opset}")
        self.lbl_graph_ir_version.setText(f"{self.graph.ir_version}")
        self.lbl_graph_name.setText(f"{self.graph.name}")
        self.lbl_graph_doc_string.setText(f"{self.graph.doc_string}")

        if self.properties_bin is not None:
            self.properties_bin.hide()
            self.layout_node_properties.removeWidget(self.properties_bin)
            del self.properties_bin
        self.properties_bin = self.create_properties_bin(self.graph)
        self.layout_node_properties.addWidget(self.properties_bin)

        self.set_sidemenu_buttons_enabled(True)
        self.search_widget.update(self.graph)

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

    def set_font_bold(self, widget: QtWidgets.QWidget, bold=True):
        set_font(widget, bold=bold)

    def set_sidemenu_buttons_enabled(self, enable=True, current_button: QtWidgets.QPushButton=None):

        if enable:
            self.menu_bar.menu_actions["Open"].setEnabled(True)
            self.menu_bar.menu_actions["Export"].setEnabled(True)
            self.menu_bar.menu_actions["Export PNG"].setEnabled(True)
            self.btnCombineNetwork.setEnabled(True)
            self.btnGenerateOperator.setEnabled(True)
            self.btnAddNode.setEnabled(True)

            if self.graph.node_count() > 0:
                self.menu_bar.menu_actions["Export"].setEnabled(True)
                self.menu_bar.menu_actions["Export PNG"].setEnabled(True)
                self.btnExtractNetwork.setEnabled(True)
                self.btnDelNode.setEnabled(True)
                self.btnConstShrink.setEnabled(True)
                self.btnModifyAttrConst.setEnabled(True)
                self.btnChangeOpset.setEnabled(True)
                self.btnChannelConvert.setEnabled(True)
                self.btnInitializeBatchSize.setEnabled(True)
                self.btnRenameOp.setEnabled(True)
            else:
                self.menu_bar.menu_actions["Export"].setEnabled(False)
                self.menu_bar.menu_actions["Export PNG"].setEnabled(False)
                self.btnExtractNetwork.setEnabled(False)
                self.btnDelNode.setEnabled(False)
                self.btnConstShrink.setEnabled(False)
                self.btnModifyAttrConst.setEnabled(False)
                self.btnChangeOpset.setEnabled(False)
                self.btnChannelConvert.setEnabled(False)
                self.btnInitializeBatchSize.setEnabled(False)
                self.btnRenameOp.setEnabled(False)

        else:
            self.menu_bar.menu_actions["Open"].setEnabled(False)
            self.menu_bar.menu_actions["Export"].setEnabled(False)
            self.menu_bar.menu_actions["Export PNG"].setEnabled(False)
            self.btnCombineNetwork.setEnabled(False)
            self.btnExtractNetwork.setEnabled(False)
            self.btnDelNode.setEnabled(False)
            self.btnConstShrink.setEnabled(False)
            self.btnModifyAttrConst.setEnabled(False)
            self.btnChangeOpset.setEnabled(False)
            self.btnChannelConvert.setEnabled(False)
            self.btnInitializeBatchSize.setEnabled(False)
            self.btnRenameOp.setEnabled(False)
            self.btnGenerateOperator.setEnabled(False)
            self.btnAddNode.setEnabled(False)

        self.current_button = current_button
        if current_button:
            current_button.setEnabled(True)

    def load_graph(self, onnx_model:onnx.ModelProto=None, onnx_model_path:str=None, model_name:str=None, clear_undo_stack=False, push_undo=False):

        t0 = time.time()
        self.set_cursor_busy()

        if not onnx_model and not onnx_model_path:
            if self.graph is None:
                self.graph = ONNXNodeGraph(name="onnx_graph_qt",
                                           opset=DEFAULT_OPSET,
                                           doc_string="",
                                           import_domains=None,
                                           producer_name="onnx_graph_qt",
                                           producer_version=0,
                                           ir_version=8,
                                           model_version=0)
            return

        onnx_graph = None
        if onnx_model:
            onnx_graph = gs.import_onnx(onnx_model)
        elif onnx_model_path:
            onnx_model = onnx.load(onnx_model_path)
            onnx_graph = gs.import_onnx(onnx_model)

        if model_name is None:
            if onnx_model_path:
                model_name = os.path.basename(onnx_model_path)
            else:
                model_name = "new graph"
        self.setWindowTitle(model_name)

        # create graph controller.
        if self.graph is None:
            self.graph = ONNXNodeGraph(name=onnx_graph.name,
                                       opset=onnx_graph.opset,
                                       doc_string=onnx_graph.doc_string,
                                       import_domains=onnx_graph.import_domains,
                                       producer_name=onnx_model.producer_name,
                                       producer_version=onnx_model.producer_version,
                                       ir_version=onnx_model.ir_version,
                                       model_version=onnx_model.model_version)
        else:
            self.graph.name = onnx_graph.name
            self.graph.opset = onnx_graph.opset
            self.graph.doc_string = onnx_graph.doc_string
            self.graph.import_domains = onnx_graph.import_domains
            self.graph.producer_name=onnx_model.producer_name
            self.graph.producer_version=onnx_model.producer_version
            self.graph.ir_version=onnx_model.ir_version
            self.graph.model_version=onnx_model.model_version

        if clear_undo_stack:
            self.graph.clear_undo_stack()

        self.graph.remove_all_nodes(push_undo=push_undo)
        self.graph.load_onnx_graph(onnx_graph, push_undo=push_undo)

        if onnx_model_path:
            op_num, model_size = structure_check(onnx_graph=onnx_model)
            print(op_num)
            print(f"{model_size} bytes")

        self.set_cursor_arrow()
        dt0 = time.time() - t0
        print(f"load graph: {dt0}s")

    def create_properties_bin(self, graph: ONNXNodeGraph):
        properties_bin = CustomPropertiesBinWidget(node_graph=graph)
        return properties_bin

    def open_onnx(self, file_name:str):
        if not os.path.exists(file_name):
            MessageBox.warn(f"not found {file_name}.", title="open")
            return
        ext = os.path.splitext(file_name)[-1]
        model_name = os.path.basename(file_name)
        if ext == ".onnx":
            self.load_graph(onnx_model_path=file_name, model_name=model_name, clear_undo_stack=True, push_undo=False)
            self.update_graph()
        elif ext == ".json":
            onnx_graph = onnx_tools_json2onnx(input_json_path=file_name)
            self.load_graph(onnx_model=onnx_graph, model_name=model_name, clear_undo_stack=True, push_undo=False)
            self.update_graph()
        else:
            MessageBox.warn(f"no supported format ({ext}).", title="open")

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        mime = event.mimeData()

        if mime.hasUrls() == True:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        mimedata = event.mimeData()
        if mimedata.hasUrls():
            urls = mimedata.urls()
            files = [url.path() for url in urls]
            for file in files:
                ext = os.path.splitext(file)[-1]
                if ext in [".onnx", ".json"]:
                    self.open_onnx(file)
                    break

    def btnOpenONNX_clicked(self):
        self.set_sidemenu_buttons_enabled(False)
        file_name, filter = QtWidgets.QFileDialog.getOpenFileName(
                            self,
                            caption="Open ONNX Model File",
                            # directory=os.path.abspath(os.curdir),
                            filter="*.onnx *.json")
        if not file_name:
            self.set_sidemenu_buttons_enabled(True)
            return
        print(f"Open: {file_name}")
        self.open_onnx(file_name)
        self.set_sidemenu_buttons_enabled(True)

    def btnExportONNX_clicked(self):
        self.set_sidemenu_buttons_enabled(False)
        file_name, filter = QtWidgets.QFileDialog.getSaveFileName(
                            self,
                            caption="Export ONNX Model File",
                            directory=os.path.abspath(os.curdir),
                            filter="*.onnx;;*.json")
        if not file_name:
            self.set_sidemenu_buttons_enabled(True)
            return
        ext = os.path.splitext(file_name)[-1]
        if filter == "*.onnx":
            if ext != ".onnx":
                file_name += ".onnx"
                if os.path.exists(file_name):
                    ret = MessageBox.question([f"{file_name} is already exist.", "overwrite?"], "export")
                    if ret == MessageBox.No:
                        self.set_sidemenu_buttons_enabled(True)
                        return
            self.graph.export(file_name)
        elif filter == "*.json":
            if ext != ".json":
                file_name += ".json"
            onnx_tools_onnx2json(onnx_graph=self.graph.to_onnx(),
                                 output_json_path=file_name,
                                 json_indent=2)
        print(f"Export: {file_name}.")
        MessageBox.info(
            ["Success.", f"Export to {file_name}."],
            "Export ONNX",
            parent=self)
        self.set_sidemenu_buttons_enabled(True)

    def btnExportPNG_clicked(self):
        self.set_sidemenu_buttons_enabled(False)
        default_file_name = "screenshot.png"
        dialog = QtWidgets.QFileDialog(
            self,
            caption="Export Graph Image",
            directory=os.path.abspath(os.curdir),
            filter="*.png")
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave)
        dialog.selectFile(default_file_name)
        ret = dialog.exec_()
        if ret == 0:
            self.set_sidemenu_buttons_enabled(True)
            return
        file_name = dialog.selectedFiles()[0]
        if not file_name:
            self.set_sidemenu_buttons_enabled(True)
            return
        self.graph.export_to_png(file_name)
        MessageBox.info(
            ["Success.", f"Export to {file_name}."],
            "Export PNG",
            parent=self)
        self.set_sidemenu_buttons_enabled(True)

    def btnAutoLayout_clicked(self):
        self.set_cursor_busy()
        self.set_sidemenu_buttons_enabled(False)

        self.graph.auto_layout(push_undo=True)

        self.set_sidemenu_buttons_enabled(True)
        self.set_cursor_arrow()

    def btnSearch_clicked(self):
        self.search_widget.show()

    def btnInferenceTest_clicked(self):
        w = InferenceTestWidgets(self.graph.to_onnx(), parent=self)
        w.show()

    def btnCombineNetwork_clicked(self):
        btn = self.btnCombineNetwork
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)
        msg_title = "Combine Network"

        self.current_widgets = CombineNetworkWidgets(graph=self.graph.to_data(), parent=self)
        while True:
            self.current_widgets.show()
            if self.current_widgets.exec_():
                onnx_tool_error = False
                print_msg = ""

                props = self.current_widgets.get_properties()
                try:
                    onnx_graph=self.graph.to_onnx(non_verbose=True)
                    onnx_graphs = []
                    if props.combine_with_current_graph:
                        onnx_graphs.append(onnx_graph)
                    for onnx_file in props.input_onnx_file_paths:
                        graph = onnx.load(onnx_file)
                        onnx_graphs.append(graph)

                    exception = None
                    try:
                        f = io.StringIO()
                        sys.stdout = f
                        onnx_model:onnx.ModelProto = onnx_tools_combine(
                            srcop_destop=props.srcop_destop,
                            op_prefixes_after_merging=props.op_prefixes_after_merging,
                            input_onnx_file_paths=[],
                            onnx_graphs=onnx_graphs,
                            output_of_onnx_file_in_the_process_of_fusion=props.output_of_onnx_file_in_the_process_of_fusion,
                            non_verbose=False,
                        )
                    except BaseException as e:
                        exception = e
                        onnx_tool_error = True
                        raise e
                    finally:
                        sys.stdout = sys.__stdout__
                        print_msg = f.getvalue()
                        print(print_msg)
                        print_msg = remove_PrintColor(print_msg)
                        print_msg = print_msg[:1000]
                        f.close()
                except BaseException as e:
                    print(e)

                if onnx_tool_error:
                    if print_msg:
                        MessageBox.error(
                            print_msg,
                            msg_title,
                            parent=self)
                    else:
                        MessageBox.error(
                            str(exception),
                            msg_title,
                            parent=self)
                    continue

                if print_msg.strip() and print_msg != "INFO: Finish!\n":
                    MessageBox.warn(
                        print_msg,
                        msg_title,
                        parent=self)

                model_name = self.windowTitle()
                self.load_graph(onnx_model=onnx_model, model_name=model_name)
                self.update_graph(update_layout=True)
                MessageBox.info(
                    f"complete.",
                    msg_title,
                    parent=self)
                break
            else:
                break
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def btnExtractNetwork_clicked(self, e:bool):
        btn = self.btnExtractNetwork
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)
        msg_title = "Extract Network"

        self.current_widgets = ExtractNetworkWidgets(graph=self.graph.to_data(), parent=self)
        while True:
            self.current_widgets.show()
            if self.current_widgets.exec_():
                onnx_tool_error = False
                print_msg = ""

                exception = None
                props = self.current_widgets.get_properties()
                try:
                    onnx_graph=self.graph.to_onnx(non_verbose=True)
                    try:
                        f = io.StringIO()
                        sys.stdout = f
                        onnx_model:onnx.ModelProto = onnx_tools_extraction(
                            onnx_graph=onnx_graph,
                            non_verbose=False,
                            **props._asdict(),
                        )
                    except BaseException as e:
                        exception = e
                        onnx_tool_error = True
                        raise e
                    finally:
                        sys.stdout = sys.__stdout__
                        print_msg = f.getvalue()
                        print(print_msg)
                        print_msg = remove_PrintColor(print_msg)
                        print_msg = print_msg[:1000]
                        f.close()
                except BaseException as e:
                    print(e)

                if onnx_tool_error:
                    if print_msg:
                        MessageBox.error(
                            print_msg,
                            msg_title,
                            parent=self)
                    else:
                        MessageBox.error(
                            str(exception),
                            msg_title,
                            parent=self)
                    continue

                if print_msg.strip() and print_msg != "INFO: Finish!\n":
                    MessageBox.warn(
                        print_msg,
                        msg_title,
                        parent=self)

                model_name = self.windowTitle()
                self.load_graph(onnx_model=onnx_model, model_name=model_name)
                self.update_graph(update_layout=True)
                MessageBox.info(
                    f"complete.",
                    msg_title,
                    parent=self)
                break
            else:
                break
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
        msg_title = "Delete Node"

        selected_nodes = self.graph.get_selected_node_names()
        self.current_widgets = DeleteNodeWidgets(parent=self, graph=self.graph.to_data(), selected_nodes=selected_nodes)
        while True:
            self.current_widgets.show()
            if self.current_widgets.exec_():
                onnx_tool_error = False
                print_msg = ""

                exception = None
                props = self.current_widgets.get_properties()
                try:
                    onnx_graph=self.graph.to_onnx(non_verbose=True)
                    try:
                        f = io.StringIO()
                        sys.stdout = f
                        onnx_model:onnx.ModelProto = onnx_tools_deletion(
                            onnx_graph=onnx_graph,
                            **props._asdict(),
                        )
                    except BaseException as e:
                        onnx_tool_error = True
                        raise e
                    finally:
                        sys.stdout = sys.__stdout__
                        print_msg = f.getvalue()
                        print(print_msg)
                        print_msg = remove_PrintColor(print_msg)
                        print_msg = print_msg[:1000]
                        f.close()
                except BaseException as e:
                    exception = e
                    print(e)

                if onnx_tool_error:
                    if print_msg:
                        MessageBox.error(
                            print_msg,
                            msg_title,
                            parent=self)
                    else:
                        MessageBox.error(
                            str(exception),
                            msg_title,
                            parent=self)
                    continue

                if print_msg.strip() and print_msg != "INFO: Finish!\n":
                    MessageBox.warn(
                        print_msg,
                        msg_title,
                        parent=self)

                model_name = self.windowTitle()
                self.graph.begin_undo(msg_title)
                self.load_graph(onnx_model=onnx_model, model_name=model_name, clear_undo_stack=False, push_undo=True)
                self.graph.end_undo()
                self.update_graph(update_layout=False)
                MessageBox.info(
                    f"complete.",
                    msg_title,
                    parent=self)
                break
            else:
                break
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
        msg_title = "Const Shrink"

        self.current_widgets = ConstantShrinkWidgets(parent=self)
        while True:
            self.current_widgets.show()
            if self.current_widgets.exec_():
                onnx_tool_error = False
                print_msg = ""

                exception = None
                props = self.current_widgets.get_properties()
                try:
                    onnx_graph=self.graph.to_onnx(non_verbose=True)
                    try:
                        f = io.StringIO()
                        sys.stdout = f
                        onnx_model, _ = onnx_tools_shrinking(
                            onnx_graph=onnx_graph,
                            non_verbose=False,
                            **props._asdict()
                        )
                    except BaseException as e:
                        onnx_tool_error = True
                        raise e
                    finally:
                        sys.stdout = sys.__stdout__
                        print_msg = f.getvalue()
                        print(print_msg)
                        print_msg = remove_PrintColor(print_msg)
                        print_msg = print_msg[:1000]
                        f.close()
                except BaseException as e:
                    exception = e
                    print(e)

                if onnx_tool_error:
                    if print_msg:
                        MessageBox.error(
                            print_msg,
                            msg_title,
                            parent=self)
                    else:
                        MessageBox.error(
                            str(exception),
                            msg_title,
                            parent=self)
                    continue

                if print_msg.strip() and print_msg != "INFO: Finish!\n":
                    MessageBox.warn(
                        print_msg,
                        msg_title,
                        parent=self)

                model_name = self.windowTitle()
                self.graph.begin_undo(msg_title)
                self.load_graph(onnx_model=onnx_model, model_name=model_name, clear_undo_stack=False, push_undo=True)
                self.graph.end_undo()
                self.update_graph(update_layout=False)
                MessageBox.info(
                    f"complete.",
                    msg_title,
                    parent=self)
                break
            else:
                break
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
        msg_title = "Generate Operator"

        self.current_widgets = GenerateOperatorWidgets(opset=self.graph.opset, parent=self)
        while True:
            self.current_widgets.show()
            if self.current_widgets.exec_():
                onnx_tool_error = False
                print_msg = ""

                exception = None
                props = self.current_widgets.get_properties()
                try:
                    f = io.StringIO()
                    sys.stdout = f
                    onnx_model:onnx.ModelProto = onnx_tools_generate(
                        non_verbose=False,
                        **props._asdict()
                    )
                except BaseException as e:
                    onnx_tool_error = True
                    exception = e
                    pass
                finally:
                    sys.stdout = sys.__stdout__
                    print_msg = f.getvalue()
                    print(print_msg)
                    print_msg = remove_PrintColor(print_msg)
                    print_msg = print_msg[:1000]
                    f.close()

                if onnx_tool_error:
                    if print_msg:
                        MessageBox.error(
                            print_msg,
                            msg_title,
                            parent=self)
                    else:
                        MessageBox.error(
                            str(exception),
                            msg_title,
                            parent=self)
                    continue

                if print_msg.strip() and print_msg != "INFO: Finish!\n":
                    MessageBox.warn(
                        print_msg,
                        msg_title,
                        parent=self)

                model_name = self.windowTitle()
                self.graph.begin_undo(msg_title)
                self.load_graph(onnx_model=onnx_model, model_name=model_name, clear_undo_stack=False, push_undo=True)
                self.graph.end_undo()
                self.update_graph(update_layout=True)
                MessageBox.info(
                    f"complete.",
                    msg_title,
                    parent=self)
                break
            else:
                break
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
        msg_title = "Modify Attributes and Constants"

        selected_nodes = self.graph.selected_nodes()
        selected_node = ""
        if len(selected_nodes) > 0:
            selected_node = selected_nodes[0].node_name
        self.current_widgets = ModifyAttrsWidgets(parent=self, graph=self.graph.to_data(), selected_node=selected_node)
        while True:
            self.current_widgets.show()
            if self.current_widgets.exec_():
                onnx_tool_error = False
                print_msg = ""

                exception = None
                props = self.current_widgets.get_properties()
                try:
                    onnx_graph=self.graph.to_onnx(non_verbose=True)
                    try:
                        f = io.StringIO()
                        sys.stdout = f
                        onnx_model:onnx.ModelProto = onnx_tools_modify(
                            onnx_graph=onnx_graph,
                            non_verbose=False,
                            **props._asdict()
                        )
                    except BaseException as e:
                        onnx_tool_error = True
                        raise e
                    finally:
                        sys.stdout = sys.__stdout__
                        print_msg = f.getvalue()
                        print(print_msg)
                        print_msg = remove_PrintColor(print_msg)
                        print_msg = print_msg[:1000]
                        f.close()
                except BaseException as e:
                    exception = e
                    print(e)

                if onnx_tool_error:
                    if print_msg:
                        MessageBox.error(
                            print_msg,
                            msg_title,
                            parent=self)
                    else:
                        MessageBox.error(
                            str(exception),
                            msg_title,
                            parent=self)
                    continue

                if print_msg.strip() and print_msg != "INFO: Finish!\n":
                    MessageBox.warn(
                        print_msg,
                        msg_title,
                        parent=self)

                model_name = self.windowTitle()
                self.graph.begin_undo(msg_title)
                self.load_graph(onnx_model=onnx_model, model_name=model_name, clear_undo_stack=False, push_undo=True)
                self.graph.end_undo()
                self.update_graph(update_layout=False)
                MessageBox.info(
                    f"complete.",
                    msg_title,
                    parent=self)
                break
            else:
                break
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
        msg_title = "Change Opset"

        self.current_widgets = ChangeOpsetWidget(parent=self, current_opset=self.graph.opset)
        old_opset = self.graph.opset
        while True:
            self.current_widgets.show()
            if self.current_widgets.exec_():
                onnx_tool_error = False
                print_msg = ""

                exception = None
                props = self.current_widgets.get_properties()
                try:
                    new_opset = int(props.opset)
                    if old_opset == new_opset:
                        MessageBox.warn(
                            f"opset num is same. not change.",
                            msg_title,
                            parent=self)
                        self.set_sidemenu_buttons_enabled(True)
                        continue

                    onnx_graph=self.graph.to_onnx(non_verbose=True)
                    try:
                        f = io.StringIO()
                        sys.stdout = f
                        onnx_model:onnx.ModelProto = onnx_tools_op_change(
                            opset=new_opset,
                            onnx_graph=onnx_graph,
                            non_verbose=False,
                        )
                    except BaseException as e:
                        onnx_tool_error = True
                        raise e
                    finally:
                        sys.stdout = sys.__stdout__
                        print_msg = f.getvalue()
                        print(print_msg)
                        print_msg = remove_PrintColor(print_msg)
                        print_msg = print_msg[:1000]
                        f.close()
                except BaseException as e:
                    exception = e
                    print(e)

                if onnx_tool_error:
                    if print_msg:
                        MessageBox.error(
                            print_msg,
                            msg_title,
                            parent=self)
                    else:
                        MessageBox.error(
                            str(exception),
                            msg_title,
                            parent=self)
                    continue

                if print_msg.strip() and print_msg != "INFO: Finish!\n":
                    MessageBox.warn(
                        print_msg,
                        msg_title,
                        parent=self)

                model_name = self.windowTitle()
                self.graph.begin_undo(msg_title)
                self.load_graph(onnx_model=onnx_model, model_name=model_name, clear_undo_stack=False, push_undo=True)
                self.graph.end_undo()
                self.update_graph(update_layout=False)
                MessageBox.info(
                    f"Change opset {old_opset} to {new_opset}.",
                    msg_title,
                    parent=self)
                break
            else:
                break
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
        msg_title = "Channel Convert"

        self.current_widgets = ChangeChannelWidgets(graph=self.graph.to_data(), parent=self)
        while True:
            self.current_widgets.show()
            if self.current_widgets.exec_():
                onnx_tool_error = False
                print_msg = ""

                exception = e
                props = self.current_widgets.get_properties()
                try:
                    onnx_graph=self.graph.to_onnx(non_verbose=True)
                    try:
                        f = io.StringIO()
                        sys.stdout = f
                        onnx_model:onnx.ModelProto = onnx_tools_order_conversion(
                            onnx_graph=onnx_graph,
                            non_verbose=False,
                            **props._asdict()
                        )
                    except BaseException as e:
                        onnx_tool_error = True
                        raise e
                    finally:
                        sys.stdout = sys.__stdout__
                        print_msg = f.getvalue()
                        print(print_msg)
                        print_msg = remove_PrintColor(print_msg)
                        print_msg = print_msg[:1000]
                        f.close()
                except BaseException as e:
                    exception = e
                    print(e)

                if onnx_tool_error:
                    if print_msg:
                        MessageBox.error(
                            print_msg,
                            msg_title,
                            parent=self)
                    else:
                        MessageBox.error(
                            str(exception),
                            msg_title,
                            parent=self)
                    continue

                if print_msg.strip() and print_msg != "INFO: Finish!\n":
                    MessageBox.warn(
                        print_msg,
                        msg_title,
                        parent=self)

                model_name = self.windowTitle()
                self.graph.begin_undo(msg_title)
                self.load_graph(onnx_model=onnx_model, model_name=model_name, clear_undo_stack=False, push_undo=True)
                self.graph.end_undo()
                self.update_graph(update_layout=False)
                MessageBox.info(
                    f"complete.",
                    msg_title,
                    parent=self)
                break
            else:
                break
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def btnAddNode_clicked(self, e:bool):
        btn = self.btnAddNode
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)
        msg_title = "Add Node"

        self.current_widgets = AddNodeWidgets(current_opset=self.graph.opset,
                                              graph=self.graph.to_data(), parent=self)
        while True:
            self.current_widgets.show()
            if self.current_widgets.exec_():
                onnx_tool_error = False
                print_msg = ""

                exception = None
                props = self.current_widgets.get_properties()
                try:
                    onnx_graph=self.graph.to_onnx(non_verbose=True)
                    f = io.StringIO()
                    sys.stdout = f
                    try:
                        onnx_model:onnx.ModelProto = onnx_tools_add(
                            onnx_graph=onnx_graph,
                            non_verbose=False,
                            **props._asdict(),
                        )
                    except BaseException as e:
                        onnx_tool_error = True
                        raise e
                    finally:
                        sys.stdout = sys.__stdout__
                        print_msg = f.getvalue()
                        print(print_msg)
                        print_msg = remove_PrintColor(print_msg)
                        print_msg = print_msg[:1000]
                        f.close()
                except BaseException as e:
                    exception = e
                    print(e)

                if onnx_tool_error:
                    if print_msg:
                        MessageBox.error(
                            print_msg,
                            msg_title,
                            parent=self)
                    else:
                        MessageBox.error(
                            str(exception),
                            msg_title,
                            parent=self)
                    continue

                if print_msg.strip() and print_msg != "INFO: Finish!\n":
                    MessageBox.warn(
                        print_msg,
                        msg_title,
                        parent=self)

                model_name = self.windowTitle()
                self.graph.begin_undo(msg_title)
                self.load_graph(onnx_model=onnx_model, model_name=model_name, clear_undo_stack=False, push_undo=True)
                self.graph.end_undo()
                self.update_graph(update_layout=False)
                MessageBox.info(
                    f"complete.",
                    msg_title,
                    parent=self)
                break
            else:
                break
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def btnInitializeBatchSize_clicked(self, e:bool):
        btn = self.btnInitializeBatchSize
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)
        msg_title = "Initialize Batchsize"

        d = self.graph.to_data()
        current_batchsize = "-1"
        for key, inp in d.inputs.items():
            current_batchsize = inp.shape[0]
            break
        self.current_widgets = InitializeBatchsizeWidget(
                                    current_batchsize=current_batchsize,
                                    parent=self)
        while True:
            self.current_widgets.show()
            if self.current_widgets.exec_():
                onnx_tool_error = False
                print_msg = ""

                exception = None
                props = self.current_widgets.get_properties()
                try:
                    onnx_graph=self.graph.to_onnx(non_verbose=True)
                    try:
                        f = io.StringIO()
                        sys.stdout = f
                        onnx_model:onnx.ModelProto = onnx_tools_batchsize_initialize(
                            onnx_graph=onnx_graph,
                            non_verbose=False,
                            **props._asdict()
                        )
                    except BaseException as e:
                        onnx_tool_error = True
                        raise e
                    finally:
                        sys.stdout = sys.__stdout__
                        print_msg = f.getvalue()
                        print(print_msg)
                        print_msg = remove_PrintColor(print_msg)
                        print_msg = print_msg[:1000]
                        f.close()
                except BaseException as e:
                    exception = e
                    print(e)

                if onnx_tool_error:
                    if print_msg:
                        MessageBox.error(
                            print_msg,
                            msg_title,
                            parent=self)
                    else:
                        MessageBox.error(
                            str(exception),
                            msg_title,
                            parent=self)
                    continue

                if print_msg.strip() and print_msg != "INFO: Finish!\n":
                    MessageBox.warn(
                        print_msg,
                        msg_title,
                        parent=self)

                model_name = self.windowTitle()
                self.graph.begin_undo(msg_title)
                self.load_graph(onnx_model=onnx_model, model_name=model_name, clear_undo_stack=False, push_undo=True)
                self.graph.end_undo()
                self.update_graph(update_layout=False)
                MessageBox.info(
                    f"complete.",
                    msg_title,
                    parent=self)
                break
            else:
                break
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def btnRenameOp_clicked(self, e:bool):
        btn = self.btnRenameOp
        if self.current_button is btn:
            self.current_widgets.close()
            return

        self.set_font_bold(btn, True)
        self.set_sidemenu_buttons_enabled(False, btn)
        msg_title = "Rename Op"

        self.current_widgets = RenameOpWidget(parent=self)
        while True:
            self.current_widgets.show()
            if self.current_widgets.exec_():
                onnx_tool_error = False
                print_msg = ""

                exception = None
                props = self.current_widgets.get_properties()
                try:
                    onnx_graph=self.graph.to_onnx(non_verbose=True)
                    try:
                        f = io.StringIO()
                        sys.stdout = f
                        onnx_model:onnx.ModelProto = onnx_tools_rename(
                            onnx_graph=onnx_graph,
                            non_verbose=False,
                            **props._asdict()
                        )
                    except BaseException as e:
                        onnx_tool_error = True
                        raise e
                    finally:
                        sys.stdout = sys.__stdout__
                        print_msg = f.getvalue()
                        print(print_msg)
                        print_msg = remove_PrintColor(print_msg)
                        print_msg = print_msg[:1000]
                        f.close()
                except BaseException as e:
                    exception = e
                    print(e)

                if onnx_tool_error:
                    if print_msg:
                        MessageBox.error(
                            print_msg,
                            msg_title,
                            parent=self)
                    else:
                        MessageBox.error(
                            str(exception),
                            msg_title,
                            parent=self)
                    continue

                if print_msg.strip() and print_msg != "INFO: Finish!\n":
                    MessageBox.warn(
                        print_msg,
                        msg_title,
                        parent=self)

                model_name = self.windowTitle()
                self.graph.begin_undo(msg_title)
                self.load_graph(onnx_model=onnx_model, model_name=model_name, clear_undo_stack=False, push_undo=True)
                self.graph.end_undo()
                self.update_graph(update_layout=False)
                MessageBox.info(
                    f"complete.",
                    msg_title,
                    parent=self)
                break
            else:
                break
        self.current_widgets = None
        self.set_sidemenu_buttons_enabled(True)
        self.set_font_bold(btn, False)

    def exit(self):
        self.close()
        sys.exit(0)


if __name__ == "__main__":
    import signal
    import os, time
    from widgets.splash_screen import create_screen, create_screen_progressbar
    from run_dagre_server import run as run_dagre_server

    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])

    proc1 = run_dagre_server()

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

    proc1.terminate()
