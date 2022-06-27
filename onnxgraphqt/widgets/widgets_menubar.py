from typing import Callable, Union, List
from dataclasses import dataclass
from PySide2 import QtCore, QtWidgets, QtGui


@dataclass
class SubMenu:
    name: str
    func: Callable
    icon: str

class Separator:
    pass

@dataclass
class Menu:
    name: str
    contents: List[Union[SubMenu, Separator]]

class MenuBarWidget(QtWidgets.QMenuBar):
    def __init__(self, menu_list: List[Menu], parent=None) -> None:
        super().__init__(parent)

        self.menu_actions = {}
        for menu in menu_list:
            m = self.addMenu(menu.name)
            for content in menu.contents:
                if isinstance(content, Separator):
                    m.addSeparator()
                elif isinstance(content, SubMenu):
                    self.menu_actions[content.name] = m.addAction(content.name, content.func)
                    if content.icon:
                        self.menu_actions[content.name].setIcon(QtGui.QIcon(content.icon))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    m = MenuBarWidget()
    m.show()

    app.exec_()