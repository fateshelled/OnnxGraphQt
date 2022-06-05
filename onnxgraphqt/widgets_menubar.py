from typing import Callable, Union, List
from dataclasses import dataclass
from PySide2 import QtCore, QtWidgets, QtGui

@dataclass
class SubMenu:
    name: str
    func: Callable

class Separator:
    pass

@dataclass
class Menu:
    name: str
    contents: List[Union[SubMenu, Separator]]

class MenuBarWidget(QtWidgets.QMenuBar):
    def __init__(self, menu_list: List[Menu], parent=None) -> None:
        super().__init__(parent)

        self.actions = {}
        for menu in menu_list:
            m = self.addMenu(menu.name)
            for content in menu.contents:
                if isinstance(content, Separator):
                    m.menuAction()
                elif isinstance(content, SubMenu):
                    self.actions[content.name] = m.addAction(content.name, content.func)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    m = MenuBarWidget()
    m.show()

    app.exec_()