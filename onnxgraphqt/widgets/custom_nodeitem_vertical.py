from PySide2 import QtCore, QtGui
from NodeGraphQt.qgraphics.node_base import NodeItemVertical
from NodeGraphQt.constants import NodeEnum

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.color import COLOR_GRAY

class CustomNodeItemVertical(NodeItemVertical):
    def __init__(self, name='node', parent=None):
        super().__init__(name, parent)
        self._op = ""

    def paint(self, painter, option, widget):
        """
        Draws the node base not the ports.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        self.auto_switch_mode()

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

        painter.setBrush(QtGui.QColor(*COLOR_GRAY + [255]))
        painter.drawRoundedRect(rect, radius, radius)

        header_rect = QtCore.QRectF(rect.x() + margin, rect.y() + margin,
                                    rect.width() - margin * 2, header_height)
        painter.setBrush(QtGui.QColor(*self.color))
        painter.drawRoundedRect(header_rect, radius, radius)


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
        # # for y in [rect.y() + padding, rect.height() - height - 1]:
        # for y in [rect.y() + padding]:
        #     edge_rect = QtCore.QRectF(rect.x() + padding, y,
        #                               rect.width() - (padding * 2), height)
        #     painter.drawRoundedRect(edge_rect, radius, radius)
        r, g, b = self.color[:3]
        if 0.2126*r + 0.715*g + 0.0722*b > 128:
            painter.setPen(QtCore.Qt.black)
        else:
            painter.setPen(QtCore.Qt.white)
        # set_font(painter, font_size=20)
        # painter.drawText(QtCore.QRectF(5, 5, rect.width(), rect.height()), self._op)
        painter.drawText(QtCore.QRectF(margin * 5, margin * 2, rect.width(), rect.height()), self.name)


        # node border
        border_width = 0.8
        border_color = QtGui.QColor(*self.border_color)
        if self.selected:
            border_width = 1.2
            border_color = QtGui.QColor(
                *NodeEnum.SELECTED_BORDER_COLOR.value
            )
        border_rect = QtCore.QRectF(rect.left(), rect.top(),
                                    rect.width(), rect.height())

        pen = QtGui.QPen(border_color, border_width)
        pen.setCosmetic(self.viewer().get_zoom() < 0.0)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawRoundedRect(border_rect, radius, radius)

        painter.restore()
