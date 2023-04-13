import signal
from PySide2 import QtCore, QtWidgets, QtGui

from onnxgraphqt.graph.onnx_node_graph import ONNXNodeGraph
from onnxgraphqt.graph.onnx_node import ONNXInput, ONNXOutput, ONNXNode, OnnxNodeIO


class NodeSearchWidget(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 500
    _DEFAULT_WINDOW_HEIGHT = 600

    def __init__(self, graph:ONNXNodeGraph=None, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("node search")
        # self.nodes = nodes
        self.graph = graph
        self.initUI()

    def initUI(self):
        if self.parentWidget():
            x = self.parentWidget().x()
            y = self.parentWidget().y()
            parent_w = self.parentWidget().width()
            parent_h = self.parentWidget().height()
            self.setGeometry(x + parent_w, y, self._DEFAULT_WINDOW_WIDTH, self._DEFAULT_WINDOW_HEIGHT)
        else:

            self.setGeometry(0, 0, self._DEFAULT_WINDOW_WIDTH, self._DEFAULT_WINDOW_HEIGHT)

        base_layout = QtWidgets.QVBoxLayout()

        # layout
        layout = QtWidgets.QHBoxLayout()
        self.tb = QtWidgets.QLineEdit()
        self.tb.setBaseSize(300, 50)
        self.btn = QtWidgets.QPushButton("search")
        self.btn.clicked.connect(self.btn_clicked)
        layout.addWidget(self.tb)
        layout.addWidget(self.btn)

        base_layout.addLayout(layout)

        self.model = QtGui.QStandardItemModel(0, 4)
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, "name")
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "type")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "input_names")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "output_names")

        self.view = QtWidgets.QTreeView()
        self.view.setSortingEnabled(True)
        self.view.doubleClicked.connect(self.viewClicked)
        self.view.setModel(self.model)
        base_layout.addWidget(self.view)

        self.setLayout(base_layout)
        self.update(self.graph)
        self.search("")
        self.view.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)

    def viewClicked(self, index:QtCore.QModelIndex):
        indexItem = self.model.index(index.row(), 0, index.parent())
        node_name = self.model.data(indexItem)
        inputs = self.graph.get_input_node_by_name(node_name)
        nodes = self.graph.get_node_by_name(node_name)
        outputs = self.graph.get_output_node_by_name(node_name)
        nodes = inputs + nodes + outputs
        self.graph.fit_to_selection_node(nodes[0])
        parent = self.parent()
        if hasattr(parent, "properties_bin"):
            parent.properties_bin.add_node(nodes[0])

    def btn_clicked(self, e):
        self.search(self.tb.text())

    def update(self, graph: ONNXNodeGraph=None):
        self.all_row_items = []

        for _ in range(self.model.rowCount()):
            self.model.takeRow(0)

        if graph is None:
            return

        for i, n in enumerate(self.graph.all_nodes()):
            if isinstance(n, ONNXNode):
                name = n.get_node_name()
                type_name = n.op
                input_names = [io.name for io in n.onnx_inputs]
                output_names = [io.name for io in n.onnx_outputs]

                name_item = QtGui.QStandardItem(name)
                type_item = QtGui.QStandardItem(type_name)
                input_names_item = QtGui.QStandardItem(", ".join(input_names))
                output_names_item = QtGui.QStandardItem(", ".join(output_names))
                name_item.setEditable(False)
                type_item.setEditable(False)
                input_names_item.setEditable(False)
                output_names_item.setEditable(False)
                self.model.setItem(i, 0, name_item)
                self.model.setItem(i, 1, type_item)
                self.model.setItem(i, 2, input_names_item)
                self.model.setItem(i, 3, output_names_item)
                self.all_row_items.append((name_item, type_item, input_names_item, output_names_item))

            elif isinstance(n, ONNXInput):
                name = n.get_node_name()
                type_name = "Input"
                output_names = [name for name in n.get_output_names()]

                name_item = QtGui.QStandardItem(name)
                type_item = QtGui.QStandardItem(type_name)
                input_names_item = QtGui.QStandardItem("")
                output_names_item = QtGui.QStandardItem(", ".join(output_names))
                name_item.setEditable(False)
                type_item.setEditable(False)
                input_names_item.setEditable(False)
                output_names_item.setEditable(False)
                self.model.setItem(i, 0, name_item)
                self.model.setItem(i, 1, type_item)
                self.model.setItem(i, 2, input_names_item)
                self.model.setItem(i, 3, output_names_item)
                self.all_row_items.append((name_item, type_item, input_names_item, output_names_item))

            elif isinstance(n, ONNXOutput):
                name = n.get_node_name()
                type_name = "Output"
                input_names = [name for name in n.get_input_names()]

                name_item = QtGui.QStandardItem(name)
                type_item = QtGui.QStandardItem(type_name)
                input_names_item = QtGui.QStandardItem(", ".join(input_names))
                output_names_item = QtGui.QStandardItem("")
                name_item.setEditable(False)
                type_item.setEditable(False)
                input_names_item.setEditable(False)
                output_names_item.setEditable(False)
                self.model.setItem(i, 0, name_item)
                self.model.setItem(i, 1, type_item)
                self.model.setItem(i, 2, input_names_item)
                self.model.setItem(i, 3, output_names_item)
                self.all_row_items.append((name_item, type_item, input_names_item, output_names_item))


    def search(self, word):
        for _ in range(self.model.rowCount()):
            self.model.takeRow(0)

        serach_words = [w.strip() for w in word.split(" ")]
        for row in self.all_row_items:
            all_matched = True
            for serach_word in serach_words:
                if serach_word == "":
                    continue
                values = [r.text() for r in row]
                found = False
                for val in values:
                    if val == "": continue
                    if val.find(serach_word) >= 0:
                        found = True
                        break
                if found is False:
                    all_matched = False
                    break

            if all_matched:
                self.model.appendRow(row)

if __name__ == "__main__":
    import signal
    import os
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])
    window = NodeSearchWidget(graph=ONNXNodeGraph("", 10, "", "", "", "", 0, 0))
    window.show()

    app.exec_()