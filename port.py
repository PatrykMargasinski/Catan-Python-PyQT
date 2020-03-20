from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsPixmapItem
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QLabel
from copy import deepcopy
from wymiary import x,y,min

class Port(QGraphicsEllipseItem):
    def __init__(self,sur):
        QGraphicsEllipseItem.__init__(self)
        self.setRect(0,0,20*min,20*min)
        self.setBrush(QBrush(Qt.cyan))
        self.surowiec=sur
        self.ikona=QGraphicsPixmapItem()
        self.ikona.setParentItem(self)
        self.ikona.setPixmap(self.wybor().scaled(20*x,20*x))

    def wybor(self):
        if self.surowiec==0:
            return QPixmap("obrazki/drewnoicon.png")
        if self.surowiec==1:
            return QPixmap("obrazki/welnaicon.png")
        if self.surowiec==2:
            return QPixmap("obrazki/zbozeicon.png")
        if self.surowiec==3:
            return QPixmap("obrazki/kamienicon.png")
        if self.surowiec==4:
            return QPixmap("obrazki/ceglaicon.png")
        if self.surowiec==5:
            self.setBrush(QBrush(Qt.darkCyan))
            return QPixmap()

    def mousePressEvent(self, ev):
        print(self.surowiec)
