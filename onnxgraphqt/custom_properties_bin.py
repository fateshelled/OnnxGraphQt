#!/usr/bin/python
from PySide2 import QtWidgets, QtCore, QtGui
from Qt import QtCompat

from custom_properties import CustomNodePropWidget
from NodeGraphQt.custom_widgets.properties_bin import PropertiesDelegate, PropertiesList

class CustomPropertiesBinWidget(QtWidgets.QWidget):
    """
    The :class:`NodeGraphQt.PropertiesBinWidget` is a list widget for displaying
    and editing a nodes properties.

    .. image:: _images/prop_bin.png
        :width: 950px

    .. code-block:: python
        :linenos:

        from NodeGraphQt import NodeGraph, PropertiesBinWidget

        # create node graph.
        graph = NodeGraph()

        # create properties bin widget.
        properties_bin = PropertiesBinWidget(parent=None, node_graph=graph)
        properties_bin.show()

    Args:
        parent (QtWidgets.QWidget): parent of the new widget.
        node_graph (NodeGraphQt.NodeGraph): node graph.
    """

    #: Signal emitted (node_id, prop_name, prop_value)
    property_changed = QtCore.Signal(str, str, object)

    def __init__(self, parent=None, node_graph=None):
        super(CustomPropertiesBinWidget, self).__init__(parent)
        self.setWindowTitle('Properties Bin')
        self._prop_list = PropertiesList()
        self.resize(450, 400)

        self._block_signal = False
        self._lock = False

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._prop_list, 1)

        # wire up node graph.
        node_graph.add_properties_bin(self)
        node_graph.node_double_clicked.connect(self.add_node)

    def __repr__(self):
        return '<{} object at {}>'.format(self.__class__.__name__, hex(id(self)))

    def __on_prop_close(self, node_id):
        items = self._prop_list.findItems(node_id, QtCore.Qt.MatchExactly)
        [self._prop_list.removeRow(i.row()) for i in items]

    def add_node(self, node):
        """
        Add node to the properties bin.

        Args:
            node (NodeGraphQt.NodeObject): node object.
        """

        rows = self._prop_list.rowCount()
        if rows >= 1:
            self._prop_list.removeRow(rows - 1)

        itm_find = self._prop_list.findItems(node.id, QtCore.Qt.MatchExactly)
        if itm_find:
            self._prop_list.removeRow(itm_find[0].row())

        self._prop_list.insertRow(0)
        prop_widget = CustomNodePropWidget(node=node)
        prop_widget.property_closed.connect(self.__on_prop_close)
        self._prop_list.setCellWidget(0, 0, prop_widget)

        item = QtWidgets.QTableWidgetItem(node.id)
        self._prop_list.setItem(0, 0, item)
        self._prop_list.selectRow(0)

    def remove_node(self, node):
        """
        Remove node from the properties bin.

        Args:
            node (str or NodeGraphQt.BaseNode): node id or node object.
        """
        node_id = node if isinstance(node, str) else node.id
        self.__on_prop_close(node_id)

    def prop_widget(self, node):
        """
        Returns the node property widget.

        Args:
            node (str or NodeGraphQt.NodeObject): node id or node object.

        Returns:
            CustomNodePropWidget: node property widget.
        """
        node_id = node if isinstance(node, str) else node.id
        itm_find = self._prop_list.findItems(node_id, QtCore.Qt.MatchExactly)
        if itm_find:
            item = itm_find[0]
            return self._prop_list.cellWidget(item.row(), 0)


if __name__ == '__main__':
    import sys
    from NodeGraphQt import BaseNode, NodeGraph
    from NodeGraphQt.constants import (NODE_PROP_QLABEL,
                                       NODE_PROP_QLINEEDIT,
                                       NODE_PROP_QCOMBO,
                                       NODE_PROP_QSPINBOX,
                                       NODE_PROP_COLORPICKER,
                                       NODE_PROP_SLIDER)


    class TestNode(BaseNode):
        NODE_NAME = 'test node'

        def __init__(self):
            super(TestNode, self).__init__()
            self.create_property('label_test', 'foo bar',
                                 widget_type=NODE_PROP_QLABEL)
            self.create_property('text_edit', 'hello',
                                 widget_type=NODE_PROP_QLINEEDIT)
            self.create_property('color_picker', (0, 0, 255),
                                 widget_type=NODE_PROP_COLORPICKER)
            self.create_property('integer', 10,
                                 widget_type=NODE_PROP_QSPINBOX)
            self.create_property('list', 'foo',
                                 items=['foo', 'bar'],
                                 widget_type=NODE_PROP_QCOMBO)
            self.create_property('range', 50,
                                 range=(45, 55),
                                 widget_type=NODE_PROP_SLIDER)

    def prop_changed(node_id, prop_name, prop_value):
        print('-'*100)
        print(node_id, prop_name, prop_value)


    app = QtWidgets.QApplication(sys.argv)

    graph = NodeGraph()
    graph.register_node(TestNode)

    prop_bin = CustomPropertiesBinWidget(node_graph=graph)
    prop_bin.property_changed.connect(prop_changed)

    node = graph.create_node('nodeGraphQt.nodes.TestNode')

    prop_bin.add_node(node)
    prop_bin.show()

    app.exec_()
