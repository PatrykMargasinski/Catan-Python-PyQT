import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtCore import *
from PyQt5.QtGui import *

kolory=["red","green","yellow","orange","magenta"]
class Gracz:
    def __init__(self,i):
        self.imie=str(i)
        self.surowce=[9,9,9,9,9] #drewno, owce, zboze, kamien, glina
        self.karty_akcji=[0,0,0,0,0]
        self.wymiany_specjalne=[0,0,0,0,0,0] #surowce, 3:1
        self.punkty=0
        self.przychod={i:[0,0,0,0,0] for i in range(2,13)}
        del self.przychod[7]
        self.kolor=kolory.pop()
        self.ranking=None
    def __gt__(self, other):
        return self.punkty<other.punkty

    def wygral(self):
        return self.punkty>=10


