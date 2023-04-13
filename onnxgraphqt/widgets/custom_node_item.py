
from PySide2 import QtCore, QtWidgets, QtGui
from NodeGraphQt.constants import NodeEnum
from NodeGraphQt.qgraphics.node_base import NodeItem

from onnxgraphqt.utils.color import NODE_BG_COLOR, NODE_SELECTED_BORDER_COLOR
from onnxgraphqt.utils.widgets import set_font


class CustomNodeItem(NodeItem):
    def __init__(self, name='node', parent=None):
        super().__init__(name, parent)
        self._display_name = ""

    def set_display_name(self, name: str):
        self._display_name = name

    def _paint_vertical(self, painter, option, widget):
        painter.save()
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.NoBrush)

        # base background.
        margin = 1.0
        radius = 4.0
        header_height = 20.0
        rect = self.boundingRect()
        rect = QtCore.QRectF(rect.left() + margin,
                            rect.top() + margin,
                            rect.width() - (margin * 2),
                            rect.height() - (margin * 2))

        painter.setBrush(QtGui.QColor(*NODE_BG_COLOR + [255]))
        painter.drawRoundedRect(rect, radius, radius)

        # header
        header_rect = QtCore.QRectF(rect.x() + margin, rect.y() + margin,
                                    rect.width() - margin * 2, header_height)
        painter.setBrush(QtGui.QColor(*self.color))
        painter.drawRoundedRect(header_rect, radius, radius)

        # header text
        r, g, b = self.color[:3]
        if 0.2126*r + 0.715*g + 0.0722*b > 128:
            painter.setPen(QtCore.Qt.black)
        else:
            painter.setPen(QtCore.Qt.white)
        if self.selected:
            set_font(painter, bold=True)
        painter.drawText(QtCore.QRectF(5, 5, rect.width(), rect.height()), self._display_name)
        set_font(painter, bold=False)

        # light overlay on background when selected.
        if self.selected:
            painter.setBrush(
                QtGui.QColor(*NodeEnum.SELECTED_COLOR.value)
            )
            painter.drawRoundedRect(rect, radius, radius)

        # # top & bottom edge background.
        # padding = 2.0
        # height = 10
        # if self.selected:
        #     painter.setBrush(QtGui.QColor(*NodeEnum.SELECTED_COLOR.value))
        # else:
        #     painter.setBrush(QtGui.QColor(0, 0, 0, 80))
        # for y in [rect.y() + padding, rect.height() - height - 1]:
        #     edge_rect = QtCore.QRectF(rect.x() + padding, y,
        #                                 rect.width() - (padding * 2), height)
        #     painter.drawRoundedRect(edge_rect, 3.0, 3.0)

        # node border
        border_width = 0.8
        border_color = QtGui.QColor(*self.border_color)
        if self.selected:
            border_width = 1.2
            border_color = QtGui.QColor(
                *list(NODE_SELECTED_BORDER_COLOR + [255])
            )
        border_rect = QtCore.QRectF(rect.left(), rect.top(),
                                    rect.width(), rect.height())

        pen = QtGui.QPen(border_color, border_width)
        pen.setCosmetic(self.viewer().get_zoom() < 0.0)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawRoundedRect(border_rect, radius, radius)

        painter.restore()