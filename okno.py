from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import *
from PyQt5.QtGui import *



class Okno(QLabel):
    def __init__(self, zrodlo=None):
        QLabel.__init__(self, zrodlo)
        self.aktywny=True

    def dzialanie(self):
        if self.aktywny==True:
            self.hide()
        else:
            self.show()

    def hideEvent(self, *args, **kwargs):
        self.aktywny=False

    def showEvent(self, *args, **kwargs):
        self.aktywny=True

