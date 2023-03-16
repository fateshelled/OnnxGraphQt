from collections import defaultdict
from PySide2 import QtWidgets, QtCore, QtGui
from NodeGraphQt.constants import NodePropWidgetEnum
from NodeGraphQt.widgets.dialogs import FileDialog
from NodeGraphQt.custom_widgets.properties_bin.prop_widgets_base import (
    PropLineEdit,
    PropTextEdit
)
from NodeGraphQt.custom_widgets.properties_bin.node_property_factory import NodePropertyWidgetFactory
from NodeGraphQt.custom_widgets.properties_bin.node_property_widgets import _PropertiesContainer


class CustomPropWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(CustomPropWindow, self).__init__(parent)
        self.__layout = QtWidgets.QGridLayout()
        self.__layout.setColumnStretch(1, 1)
        # self.__layout.setSpacing(6)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addLayout(self.__layout)

    def __repr__(self):
        return '<CustomPropWindow object at {}>'.format(hex(id(self)))

    def add_widget(self, name, widget, value, label=None):
        """
        Add a property widget to the window.

        Args:
            name (str): property name to be displayed.
            widget (BaseProperty): property widget.
            value (object): property value.
            label (str): custom label to display.
        """
        widget.setToolTip(name)
        if value is not None:
            widget.set_value(value)
        if label is None:
            label = name
        row = self.__layout.rowCount()
        if row > 0:
            row += 1

        label_flags = QtCore.Qt.AlignCenter | QtCore.Qt.AlignRight
        # label_flags = QtCore.Qt.AlignTop
        if widget.__class__.__name__ == 'PropTextEdit':
            label_flags = label_flags | QtCore.Qt.AlignTop
        elif widget.__class__.__name__ == 'PropList':
            label_flags = QtCore.Qt.AlignTop | QtCore.Qt.AlignRight

        self.__layout.addWidget(QtWidgets.QLabel(label), row, 0, label_flags)
        self.__layout.addWidget(widget, row, 1)

    def get_widget(self, name):
        """
        Returns the property widget from the name.

        Args:
            name (str): property name.

        Returns:
            QtWidgets.QWidget: property widget.
        """
        for row in range(self.__layout.rowCount()):
            item = self.__layout.itemAtPosition(row, 1)
            if item and name == item.widget().toolTip():
                return item.widget()


class PropList(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(PropList, self).__init__(parent)
        self.__layout = QtWidgets.QVBoxLayout()
        self.__layout.setAlignment(QtCore.Qt.AlignTop)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addLayout(self.__layout)
        layout.setContentsMargins(0, 0 ,0 ,0)

    def add_item(self, name, dtype, shape, value):
        if dtype is None:
            label = QtWidgets.QLabel(f"{name}")
            self.__layout.addWidget(label)
        elif value is None or value == -1:
            label = QtWidgets.QLabel(f"{name}")
            type_shape = QtWidgets.QLabel(f"{dtype} {list(shape)}")
            self.__layout.addWidget(label)
            self.__layout.addWidget(type_shape)
        else:
            # has value
            content_layout = QtWidgets.QVBoxLayout()
            label = QtWidgets.QLabel(f"{name}")
            type_shape = QtWidgets.QLabel(f"{dtype} {list(shape)}")
            txt = QtWidgets.QLineEdit()
            txt.setText(str(value))
            txt.setReadOnly(True)
            content_layout.addWidget(label)
            content_layout.addWidget(type_shape)
            content_layout.addWidget(txt)
            self.__layout.addLayout(content_layout)


class CustomNodePropWidget(QtWidgets.QWidget):
    """
    Node properties widget for display a Node object.

    Args:
        parent (QtWidgets.QWidget): parent object.
        node (NodeGraphQt.BaseNode): node.
    """

    #: signal (node_id, prop_name, prop_value)
    property_changed = QtCore.Signal(str, str, object)
    property_closed = QtCore.Signal(str)

    def __init__(self, parent=None, node=None):
        super(CustomNodePropWidget, self).__init__(parent)
        self.__node_id = node.id

        self.prop_window = CustomPropWindow(self)

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout .addWidget(self.prop_window)
        # layout.setSpacing(4)
        # layout.addWidget(self.prop_window)

        self._read_node(node)

    def __repr__(self):
        return '<NodePropWidget object at {}>'.format(hex(id(self)))

    def _on_close(self):
        """
        called by the close button.
        """
        self.property_closed.emit(self.__node_id)

    def _on_property_changed(self, name, value):
        """
        slot function called when a property widget has changed.
        Args:
            name (str): property name.
            value (object): new value.
        """
        self.property_changed.emit(self.__node_id, name, value)

    def _read_node(self, node):
        """
        Populate widget from a node.

        Args:
            node (NodeGraphQt.BaseNode): node class.
        """
        model = node.model
        graph_model = node.graph.model

        common_props = graph_model.get_node_common_properties(node.type_)

        properties = []

        for prop_name, prop_val in model.custom_properties.items():
            tab_name = model.get_tab_name(prop_name)
            if tab_name == 'Properties':
                properties.append((prop_name, prop_val))

        # property widget factory.
        widget_factory = NodePropertyWidgetFactory()

        for prop_name, value in properties:
            wid_type = model.get_widget_type(prop_name).value
            if wid_type == 0:
                continue
            if prop_name in ["inputs_", "outputs_"]:
                io_len = len(value)
                for i, (name, dtype, shape, v) in enumerate(value):
                    widget = PropList()
                    widget.add_item(name, dtype, shape, v)
                    if io_len == 1:
                        self.prop_window.add_widget(prop_name, widget, None,
                                                    prop_name.replace('_', ' '))
                    else:
                        self.prop_window.add_widget(prop_name, widget, None,
                                                    prop_name.replace('_', ' ') + f"[{i+1}]")
            else:
                widget = widget_factory.get_widget(wid_type)
                if isinstance(widget, PropLineEdit) or isinstance(widget, PropTextEdit):
                    widget.setReadOnly(True)

                self.prop_window.add_widget(prop_name, widget, value,
                                            prop_name.replace('_', ' '))


    def node_id(self):
        """
        Returns the node id linked to the widget.

        Returns:
            str: node id
        """
        return self.__node_id

    def add_widget(self, name, widget, tab='Properties'):
        """
        add new node property widget.
        Args:
            name (str): property name.
            widget (BaseProperty): property widget.
            tab (str): tab name.
        """
        if tab not in self._widgets.keys():
            tab = 'Properties'
        window = self.__tab_windows[tab]
        window.add_widget(name, widget)
        widget.value_changed.connect(self._on_property_changed)

    def get_widget(self, name):
        """
        get property widget.
        Args:
            name (str): property name.
        Returns:
            QtWidgets.QWidget: property widget.
        """
        if name == 'name':
            return self.name_wgt
        for tab_name, prop_win in self.__tab_windows.items():
            widget = prop_win.get_widget(name)
            if widget:
                return 

if __name__ == '__main__':
    import sys
    from NodeGraphQt import BaseNode, NodeGraph
    from NodeGraphQt.constants import NodePropWidgetEnum


    class TestNode(BaseNode):
        NODE_NAME = 'test node'

        def __init__(self):
            super(TestNode, self).__init__()
            self.create_property('label_test', 'foo bar',
                                 widget_type=NodePropWidgetEnum.QLABEL)
            self.create_property('line_edit', 'hello',
                                 widget_type=NodePropWidgetEnum.QLINE_EDIT)
            self.create_property('color_picker', (0, 0, 255),
                                 widget_type=NodePropWidgetEnum.COLOR_PICKER)
            self.create_property('integer', 10,
                                 widget_type=NodePropWidgetEnum.QSPIN_BOX)
            self.create_property('list', 'foo',
                                 items=['foo', 'bar'],
                                 widget_type=NodePropWidgetEnum.QCOMBO_BOX)
            self.create_property('range', 50,
                                 range=(45, 55),
                                 widget_type=NodePropWidgetEnum.SLIDER)
            self.create_property('text_edit', 'test text',
                                 widget_type=NodePropWidgetEnum.QTEXT_EDIT,
                                 tab='text')


    def prop_changed(node_id, prop_name, prop_value):
        print('-' * 100)
        print(node_id, prop_name, prop_value)


    def prop_close(node_id):
        print('=' * 100)
        print(node_id)


    app = QtWidgets.QApplication(sys.argv)

    graph = NodeGraph()
    graph.register_node(TestNode)

    test_node = graph.create_node('nodeGraphQt.nodes.TestNode')

    node_prop = CustomNodePropWidget(node=test_node)
    node_prop.property_changed.connect(prop_changed)
    node_prop.property_closed.connect(prop_close)
    node_prop.show()

    app.exec_()
