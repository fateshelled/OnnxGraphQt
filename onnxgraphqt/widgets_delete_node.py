from collections import namedtuple
import signal
from PySide2 import QtCore, QtWidgets, QtGui

DeleteNodeProperties = namedtuple("DeleteNodeProperties",
    [
        "remove_node_names",
    ])

class DeleteNodeWidgets(QtWidgets.QDialog):
    _DEFAULT_WINDOW_WIDTH = 400
    _MAX_REMOVE_NODE_NAMES_COUNT = 5

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle("delete node")
        self.initUI()

    def initUI(self):
        self.setFixedWidth(self._DEFAULT_WINDOW_WIDTH)

        base_layout = QtWidgets.QVBoxLayout()

        # attributes
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(QtWidgets.QLabel("remove_node_names"))
        self.visible_remove_node_names_count = 1
        self.remove_node_names = {}
        for index in range(self._MAX_REMOVE_NODE_NAMES_COUNT):
            self.remove_node_names[index] = {}
            self.remove_node_names[index]["base"] = QtWidgets.QWidget()
            self.remove_node_names[index]["layout"] = QtWidgets.QHBoxLayout(self.remove_node_names[index]["base"])
            self.remove_node_names[index]["layout"].setContentsMargins(0, 0, 0, 0)
            self.remove_node_names[index]["name"] = QtWidgets.QLineEdit()
            self.remove_node_names[index]["name"].setPlaceholderText("name")
            self.remove_node_names[index]["layout"].addWidget(self.remove_node_names[index]["name"])
            self.layout.addWidget(self.remove_node_names[index]["base"])
        self.btn_add = QtWidgets.QPushButton("+")
        self.btn_del = QtWidgets.QPushButton("-")
        self.btn_add.clicked.connect(self.btn_add_clicked)
        self.btn_del.clicked.connect(self.btn_del_clicked)
        self.set_visible()
        layout_btn = QtWidgets.QHBoxLayout()
        layout_btn.addWidget(self.btn_add)
        layout_btn.addWidget(self.btn_del)
        self.layout.addLayout(layout_btn)

        # add layout
        base_layout.addLayout(self.layout)

        # Dialog button
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        # layout.addWidget(btn)
        base_layout.addWidget(btn)

        self.setLayout(base_layout)

    def set_visible(self):
        for key, widgets in self.remove_node_names.items():
            widgets["base"].setVisible(key < self.visible_remove_node_names_count)
        if self.visible_remove_node_names_count == 1:
            self.btn_add.setEnabled(True)
            self.btn_del.setEnabled(False)
        elif self.visible_remove_node_names_count >= self._MAX_REMOVE_NODE_NAMES_COUNT:
            self.btn_add.setEnabled(False)
            self.btn_del.setEnabled(True)
        else:
            self.btn_add.setEnabled(True)
            self.btn_del.setEnabled(True)

    def btn_add_clicked(self, e):
        self.visible_remove_node_names_count = min(max(0, self.visible_remove_node_names_count + 1), self._MAX_REMOVE_NODE_NAMES_COUNT)
        self.set_visible()

    def btn_del_clicked(self, e):
        self.visible_remove_node_names_count = min(max(0, self.visible_remove_node_names_count - 1), self._MAX_REMOVE_NODE_NAMES_COUNT)
        self.set_visible()


    def get_properties(self)->DeleteNodeProperties:

        remove_node_names = []
        for i in range(self.visible_remove_node_names_count):
            name = self.remove_node_names[i]["name"].text()
            if str.strip(name):
                remove_node_names.append(name)

        return DeleteNodeProperties(
            remove_node_names=remove_node_names
        )

    def accept(self) -> None:
        # value check
        invalid = False
        props = self.get_properties()
        print(props)
        if len(props.remove_node_names) == 0:
            print("ERROR: remove_node_names.")
            invalid = True

        if invalid:
            return
        return super().accept()



if __name__ == "__main__":
    import signal
    import os
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])
    window = DeleteNodeWidgets()
    window.show()

    app.exec_()