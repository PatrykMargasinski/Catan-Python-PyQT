import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from wymiary import x,y,min
class Sygnal(QObject):
    c=pyqtSignal()


class Wierzcholek(QGraphicsEllipseItem):

    def __init__(self, zrodlo=None):
        super().__init__()
        self.zrodlo=zrodlo
        self.x=0
        self.y=0
        self.setRect(0,0,20*x,20*y)
        self.s=Sygnal()
        self.setBrush(QBrush(QColor("white")))
        self.kolor="white"
        self.sas_hexy = []
        self.sas_wierz = {}
        self.handel=-1
        self.miasto=""
        self.ulepszone=False
        self.setZValue(10)

    def mousePressEvent(self, ev):
        self.zaznaczenie()
        self.s.c.emit()
        print("Srodek:", self.x, self.y)
        for i in self.sas_wierz.keys():
            print([i.x,i.y],end="")
        print("jest")

    def ulepszenie(self):
        kolo = QGraphicsEllipseItem(self)
        kolo.setBrush(QColor(255,215,0))
        kolo.setRect(20 * x * 0.30, 20 * y * 0.30, 20 * x * 0.40, 20 * y * 0.40)

    def zaznaczenie(self):
        self.zrodlo.zaznaczony=self


