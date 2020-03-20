from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QGraphicsTextItem
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from wymiary import x,y

class Sygnal(QObject):
    c=pyqtSignal()

class Hex(QGraphicsPixmapItem):
    def __init__(self,i, j, zrodlo=None):
        super().__init__()
        Hy = 100*y
        Hx = (3 ** 0.5) * Hy // 2
        self.x=i
        self.y=j
        self.zrodlo=zrodlo
        self.surowiec=-1
        self.numer=-1
        self.sas_hexy=[]
        self.sas_wierz=[]
        self.setPixmap(QPixmap("obrazki/pustka.png").scaled(Hx, Hy))
        self.s = Sygnal()

    def mousePressEvent(self, ev):
        print("Hex:",self.x,self.y)
        self.zaznaczenie()
        self.s.c.emit()
        for i in self.sas_wierz:
            print([i.x,i.y],end="")
        print("Numer: ",self.numer)
        print("Surowiec: ", self.surowiec)

    def dodaj_liczbe(self, numer):
        Hy = 100*y
        Hx = (3 ** 0.5) * Hy // 2
        self.numer = numer
        liczba=QGraphicsPixmapItem(self)
        liczba.setPixmap(QPixmap("obrazki/"+str(numer)+".png").scaled(Hx*0.6,Hy*0.6))
        liczba.setPos(Hx*0.2,Hy*0.2)
        print(liczba)

    def ustaw(self, numer):
        self.surowiec = numer
        Hy = 100*y
        Hx = (3 ** 0.5) * Hy // 2
        if numer == 0: self.setPixmap(QPixmap("obrazki/drewno.png").scaled(Hx, Hy))
        if numer == 1: self.setPixmap(QPixmap("obrazki/owieczki.png").scaled(Hx, Hy))
        if numer == 2: self.setPixmap(QPixmap("obrazki/siano.png").scaled(Hx, Hy))
        if numer == 3: self.setPixmap(QPixmap("obrazki/kamyczek.png").scaled(Hx, Hy))
        if numer == 4: self.setPixmap(QPixmap("obrazki/cegla.png").scaled(Hx, Hy))
        if numer == 5: self.setPixmap(QPixmap("obrazki/pustka.png").scaled(Hx, Hy))

    def zaznaczenie(self):
        self.zrodlo.zaznaczony_hex=self