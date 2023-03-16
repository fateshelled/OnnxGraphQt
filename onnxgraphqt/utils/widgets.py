from typing import List
import math
from PySide2 import QtCore, QtWidgets, QtGui
from NodeGraphQt.constants import PipeEnum
from NodeGraphQt.qgraphics.pipe import PIPE_STYLES


BASE_FONT_SIZE = 16
LARGE_FONT_SIZE = 18
GRAPH_FONT_SIZE = 32
PIPE_WIDTH = 3.0

def set_font(widget: QtWidgets.QWidget, font_size:int=None, bold=False):
    f = widget.font()
    if font_size:
        f.setPixelSize(font_size)
    f.setBold(bold)
    widget.setFont(f)

def iconButton_paintEvent(button: QtWidgets.QPushButton, pixmap: QtGui.QPixmap, event: QtGui.QPaintEvent):
    QtWidgets.QPushButton.paintEvent(button, event)
    pos_x = 5 + int((30 - pixmap.width())*0.5 + 0.5)
    pos_y = (button.height() - pixmap.height()) / 2
    painter = QtGui.QPainter(button)
    painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
    painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
    painter.drawPixmap(pos_x, pos_y, pixmap)

def createIconButton(text:str, icon_path: str, icon_size:List[int]=[25, 25], font_size:int=None) -> QtWidgets.QPushButton:
    button = QtWidgets.QPushButton()
    button.setContentsMargins(QtCore.QMargins(5, 5, 5, 5))
    button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    pixmap = QtGui.QPixmap(icon_path).scaled(icon_size[0], icon_size[1], QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
    def paintEvent(button, pixmap):
        def func(event):
            return iconButton_paintEvent(button, pixmap, event)
        return func
    button.paintEvent = paintEvent(button, pixmap)
    button_layout = QtWidgets.QVBoxLayout()
    button_layout.setMargin(0)
    button.setLayout(button_layout)
    label = QtWidgets.QLabel(text=text)
    label.setMargin(0)
    label.setAlignment(QtCore.Qt.AlignRight)
    set_font(label, font_size=font_size)
    button_layout.addWidget(label)
    return button


def pipe_paint(pipe, painter, option, widget, text=""):
    """
    Draws the connection line between nodes.

    Args:
        painter (QtGui.QPainter): painter used for drawing the item.
        option (QtGui.QStyleOptionGraphicsItem):
            used to describe the parameters needed to draw.
        widget (QtWidgets.QWidget): not used.
    """
    color = QtGui.QColor(*pipe._color)
    pen_style = PIPE_STYLES.get(pipe.style)
    pen_width = PIPE_WIDTH #PipeEnum.WIDTH.value
    if pipe._active:
        color = QtGui.QColor(*PipeEnum.ACTIVE_COLOR.value)
        if pen_style == QtCore.Qt.DashDotDotLine:
            pen_width += 1
        else:
            pen_width += 0.35
    elif pipe._highlight:
        color = QtGui.QColor(*PipeEnum.HIGHLIGHT_COLOR.value)
        pen_style = PIPE_STYLES.get(PipeEnum.DRAW_TYPE_DEFAULT.value)

    if pipe.disabled():
        if not pipe._active:
            color = QtGui.QColor(*PipeEnum.DISABLED_COLOR.value)
        pen_width += 0.2
        pen_style = PIPE_STYLES.get(PipeEnum.DRAW_TYPE_DOTTED.value)

    pen = QtGui.QPen(color, pen_width, pen_style)
    pen.setCapStyle(QtCore.Qt.RoundCap)
    pen.setJoinStyle(QtCore.Qt.MiterJoin)

    painter.save()
    painter.setPen(pen)
    painter.setRenderHint(painter.Antialiasing, True)
    painter.drawPath(pipe.path())

    # draw arrow
    if pipe.input_port and pipe.output_port:
        cen_x = pipe.path().pointAtPercent(0.5).x()
        cen_y = pipe.path().pointAtPercent(0.5).y()
        loc_pt = pipe.path().pointAtPercent(0.49)
        tgt_pt = pipe.path().pointAtPercent(0.51)
        dist = math.hypot(tgt_pt.x() - cen_x, tgt_pt.y() - cen_y)
        if dist < 0.5:
            painter.restore()
            return

        color.setAlpha(255)
        if pipe._highlight:
            painter.setBrush(QtGui.QBrush(color.lighter(150)))
        elif pipe._active or pipe.disabled():
            painter.setBrush(QtGui.QBrush(color.darker(200)))
        else:
            painter.setBrush(QtGui.QBrush(color.darker(130)))

        pen_width = 0.6
        if dist < 1.0:
            pen_width *= (1.0 + dist)

        pen = QtGui.QPen(color, pen_width)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        painter.setPen(pen)

        transform = QtGui.QTransform()
        transform.translate(cen_x, cen_y)
        radians = math.atan2(tgt_pt.y() - loc_pt.y(),
                                tgt_pt.x() - loc_pt.x())
        degrees = math.degrees(radians) - 90
        transform.rotate(degrees)
        if dist < 1.0:
            transform.scale(dist, dist)
        painter.drawPolygon(transform.map(pipe._arrow))
        if text:
            painter.setPen(QtCore.Qt.black)
            set_font(painter, font_size=20)
            painter.drawText(QtCore.QRectF(cen_x, cen_y, 200, 100), text)


    # QPaintDevice: Cannot destroy paint device that is being painted.
    painter.restore()
