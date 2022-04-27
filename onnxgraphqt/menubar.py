from PySide2 import QtCore, QtWidgets, QtGui

class MenuBar(QtWidgets.QMenuBar):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        menu = {
            "File": {
                # "open": self.file_open_clicked,
                # "import": self.file_export_onnx_clicked,
                # "export": self.file_export_onnx_clicked,
                "exit": self.file_exit_clicked,
            },
            # "Edit": {
            #     "Redo": self.graph.undo_stack,
            #     "Undo": self.graph.undo_stack,
            # }
        }
        self.actions = {}
        for key, items in menu.items():
            m = self.addMenu(key)
            for key, func in items.items():
                self.actions[key] = m.addAction(key, func)

    def file_open_clicked(self, e):
        print("file_open")

    def file_import_onnx_clicked(self, e):
        print("import")

    def file_export_onnx_clicked(self, e):
        print("export")

    def file_exit_clicked(self, e):
        print("exit")
