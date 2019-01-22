from PyQt5.QtCore import QPointF, Qt, QRectF
from PyQt5.QtGui import QPainter, QPainterPath
from PyQt5.QtWidgets import QGraphicsEllipseItem


class DeusEx(QGraphicsEllipseItem):
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.width = 100
        self.height = 100
        self.m_boundingRect = QRectF(0, 0, self.width, self.height)

    def boundingRect(self):
        return self.m_boundingRect

    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.m_boundingRect)
        return path

    def paint(self, QPainter: QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.setBrush(Qt.red)
        QPainter.drawEllipse(self.m_boundingRect)
