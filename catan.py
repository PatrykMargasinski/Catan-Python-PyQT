import sys
from hex import Hex
from wierzcholek import Wierzcholek
from gracz import Gracz
from numpy import concatenate, arange
from okno import Okno
from port import Port
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from random import choice, randint, choices
from copy import copy
from functools import partial
from wymiary import x,y

def funkcja(x, granica):
    return abs(abs(x - granica) - granica)

def odleglosc(w1,w2):
    return QLineF(w1.pos(),w2.pos()).length()

def rzut():
    return randint(1,6)+randint(1,6)

class Gra(QGraphicsView):
    def __init__(self):
        QGraphicsView.__init__(self)
        self.podstawowe_ustwienia()
        self.stworzmy_graczy()
        self.stworz_plansze()
        self.wyswietl_plansze(450*x,100*y)
        self.stworz_wierzcholki()
        self.wyswietl_wierzcholki(450*x,100*y)
        self.sasiedztwoHexow()
        self.sasiedztwo_srodki()
        self.synchronizacja()
        self.ustawienie_hexow()
        self.zlodziej_przygotowanie()
        self.ustawienie_numerow()
        self.porty_wstawianie()
        self.przyciski_okna()
        self.polaczenia()
        self.aktualizacja()
        self.drogowe=[]
        self.poczatkowa_kolejnosc=[i for i in range(len(self.gracze))]+[i for i in range(len(self.gracze)-1,-1,-1)]
        self.poczatkowe_tury()

    def poczatkowe_tury(self):
        if len(self.poczatkowa_kolejnosc)!=0:
            self.obecny=self.poczatkowa_kolejnosc.pop()
            self.komunikat.setStyleSheet("background: %s"%self.gracze[self.obecny].kolor)
            for i in self.grupy:
                i.hide()
            self.komunikat.setText("%s, wstaw swe pierwsze miasto" % self.gracze[self.obecny].imie)
            for j in concatenate(self.wierzcholki):
                if j.miasto=="-1":
                    j.setBrush(QColor("black"))
                j.s.c.connect(self.pierwsze_miasto)
        else:
            self.obecny=-1
            for i in self.grupy:
                i.show()
            self.koniec_tury()
    def zlodziej_przygotowanie(self):
        self.zlodziej=None
        self.zlodziej_obraz=QGraphicsPixmapItem()
        self.zlodziej_obraz.setPixmap(QPixmap("obrazki/zlodziej.png").scaled(86*x,70*y))
        self.scene.addItem(self.zlodziej_obraz)

    def zlodziej_zmiana(self):
        for i in self.grupy:
            i.hide()
        temp=["gdzie postawisz złodzieja?", "możesz swemu sojusznikowi wsadzić złodzieja", "pokaz zlodziejowi, gdzie ma iść", "zablokuj jakieś czerwone pole"]
        self.komunikat.setText(self.gracze[self.obecny].imie +", "+ choice(temp))
        for j in concatenate(self.plansza):
            j.s.c.connect(self.zmien_zlodzieja)

    def znajdz_gracza(self, posz):
        for i in self.gracze:
            if i.imie==posz:
                return i

    def zmien_zlodzieja(self):
        hex = self.zaznaczony_hex
        byly = self.zlodziej
        #zwrot
        if self.zlodziej.surowiec != 5:
            for i in self.zlodziej.sas_wierz:
                if i.miasto != "" and i.miasto != "-1":
                    temp = self.znajdz_gracza(i.miasto)
                    temp.przychod[byly.numer][byly.surowiec] += (1 + (1 if (i.ulepszone == True) else 0))

        self.zlodziej_ustawienie(hex)
        for i in self.grupy:
            i.show()
        # blokada
        if hex.surowiec != 5:
            for i in hex.sas_wierz:
                if i.miasto != "" and i.miasto != "-1":
                    temp = self.znajdz_gracza(i.miasto)
                    temp.przychod[hex.numer][hex.surowiec] -= (1 + (1 if (i.ulepszone == True) else 0))
        for j in concatenate(self.plansza):
            j.s.c.disconnect()
        self.komunikat.setText(choice(["No, to teraz kontynuuj", "Też bym tak zrobił", "Dokonałeś swej zemsty", "Dobrze mu tak", "Jak brutalnie..."]))

    def zlodziej_ustawienie(self,hex):
        self.zlodziej=hex
        self.zlodziej_obraz.setPos(hex.pos().x(),(hex.pos().y()+15*y))

    def pierwsze_miasto(self):
        temp = self.gracze[self.obecny].surowce
        gracz = self.gracze[self.obecny]
        self.drogowe=[]
        if self.zaznaczony.miasto=="":
            temp = self.gracze[self.obecny].surowce
            gracz= self.gracze[self.obecny]
            self.drogowe.append(self.zaznaczony)
            self.komunikat.setText("Teraz droga")

            self.zaznaczony.setBrush(QBrush(QColor(gracz.kolor)))
            self.zaznaczony.kolor=gracz.kolor
            self.zaznaczony.miasto=gracz.imie

            for i in self.zaznaczony.sas_wierz.keys():
                i.miasto="-1"

            #wzrost przychodu
            for i in self.zaznaczony.sas_hexy:
                if i.surowiec!=5:
                    gracz.przychod[i.numer][i.surowiec]+=1

            #dodanie ewentualnych portow
            if self.zaznaczony.handel!=-1:
                gracz.wymiany_specjalne[self.zaznaczony.handel]=1
                self.handel_aktualizacja()

            #dodanie punktow
            self.gracze[self.obecny].punkty+=1
            self.ranking_aktualizacja()

            for j in concatenate(self.wierzcholki):
                j.s.c.disconnect()
                j.s.c.connect(self.pierwsza_droga)
                j.setBrush(QColor(j.kolor))
        else:
            self.komunikat.setText("Nie mozna wybudowac")

    def drogi_sasiaduja(self,w1,w2):
        return w1 in w2.sas_wierz.keys() and w2 in w1.sas_wierz.keys()

    def wolne_drogi(self,w1,w2):
        return w1.sas_wierz[w2]=="" and w2.sas_wierz[w1]==""

    def pierwsza_droga(self):
        temp = self.gracze[self.obecny].surowce
        gracz=self.gracze[self.obecny]
        self.drogowe.append(self.zaznaczony)
        if (self.drogi_sasiaduja(self.drogowe[0],self.drogowe[1]) and self.wolne_drogi(self.drogowe[0],self.drogowe[1]))==True:
            self.drogowe[0].sas_wierz[self.drogowe[1]]=self.gracze[self.obecny].imie
            self.drogowe[1].sas_wierz[self.drogowe[0]]=self.gracze[self.obecny].imie
            self.drogowe[0].setBrush(QColor(self.drogowe[0].kolor))
            temp1=self.drogowe[0].pos()
            temp2=self.drogowe[1].pos()
            linia=QGraphicsLineItem()
            linia.setLine((temp1.x()+10*x),(temp1.y()+10*y),(temp2.x()+10*x),(temp2.y()+10*y))
            pen=QPen(QColor(gracz.kolor))
            pen.setWidth(8*y)
            linia.setPen(pen)
            linia.setZValue(0)
            self.scene.addItem(linia)
            for j in concatenate(self.wierzcholki):
                j.s.c.disconnect()
            self.poczatkowe_tury()
        else:
            self.drogowe.pop()
            self.komunikat.setText("Zle miejsce")

    def podstawowe_ustwienia(self):
        self.faza=QLabel("Catanowo",self)
        self.faza.setGeometry(0,0,1200*x,40*y)
        self.faza.setAlignment(Qt.AlignCenter)
        self.faza.setFont(QFont("Arial", 20*y, QFont.Bold))
        self.komunikat=QLabel(self)
        self.komunikat.setGeometry(0, 40*y, 1200*x, 40*y)
        self.komunikat.setAlignment(Qt.AlignCenter)
        self.komunikat.setFont(QFont("Arial", 10*y, QFont.Bold))
        self.zaznaczony=None
        self.zaznaczony_hex=None
        self.ilosc = 4
        self.obecny = 0
        self.surowiec_wybrany = -1
        self.setFixedSize(1200*x, 900*y)
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(Qt.red))
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(Qt.blue))

    def stworz_plansze(self):
        self.plansza=[[Hex(i,j, self) for j in range(funkcja(i,self.ilosc-1)+self.ilosc)] for i in range(self.ilosc*2-1)]
        self.ilosc_hexow=len(concatenate(self.plansza))

    def wyswietl_plansze(self,x0,y0):
        Hy = 100*y
        Hx = (3 ** 0.5) * Hy // 2

        for i in range (len(self.plansza)):
            for j in range(len(self.plansza[i])):
                self.scene.addItem(self.plansza[i][j])
                self.plansza[i][j].setPos(x0 + (Hx*j) - (Hx/2*funkcja(i, self.ilosc-1)), y0 + (Hy*0.75*i))

    def stworz_wierzcholki(self):
        temp1=[[Wierzcholek(self) for j in range((self.ilosc+i)*2+1)] for i in range(self.ilosc)]
        temp2=[[Wierzcholek(self) for j in range((self.ilosc+i)*2+1)] for i in range(self.ilosc)]
        self.wierzcholki=temp1+list(reversed(temp2))

    def wyswietl_wierzcholki(self,x0,y0):
        Hy = 100*y
        Hx = (3 ** 0.5) * Hy // 2
        skret=-1
        for i in range(len(self.wierzcholki)):
            skret=skret+1 if i<self.ilosc else skret-1
            zmiana = 0 if i < self.ilosc else 1
            for j in range(len(self.wierzcholki[i])):
                self.scene.addItem(self.wierzcholki[i][j])
                self.wierzcholki[i][j].setX(x0-10*x + (j-zmiana)*(Hx/2) - (Hx/2)*skret)

                gorka=Hy//4 if (j+zmiana)%2==0 else 0
                self.wierzcholki[i][j].setY(y0-10*y + gorka+0.75*i*Hy)
                self.wierzcholki[i][j].x,self.wierzcholki[i][j].y=i,j

    def stworzmy_graczy(self):
        gracze=5
        self.gracze=[Gracz("Gracz "+str(i+1)) for i in range(gracze)]
        self.ilosc_graczy=gracze


    def sasiedztwoHexow(self):
        for i in range(len(self.plansza)):
            for j in range(len(self.plansza[i])):
                # prawy dolny
                temp = -1 if i >= self.ilosc - 1 else 0
                if i < len(self.plansza) - 1 and j + temp < len(self.plansza[i + 1]) - 1:
                    self.plansza[i][j].sas_hexy.append(self.plansza[i + 1][j + 1 + temp])

                # lewy dolny
                temp = -1 if j <= self.ilosc - 1 and i < self.ilosc - 1 else 0
                if i < len(self.plansza) - 1 and j - temp > 0:
                    self.plansza[i][j].sas_hexy.append(self.plansza[i + 1][j - 1 - temp])

                # lewy
                if j > 0:
                    self.plansza[i][j].sas_hexy.append(self.plansza[i][j - 1])

                # prawy
                if j < len(self.plansza[i]) - 1:
                    self.plansza[i][j].sas_hexy.append(self.plansza[i][j + 1])

                # lewy gorny
                temp = 1 if i > self.ilosc - 1 else 0
                if i > 0 and j + temp > 0:
                    self.plansza[i][j].sas_hexy.append(self.plansza[i - 1][j - 1 + temp])

                # prawy gorny
                temp = 1 if i >= self.ilosc else 0
                if i > 0 and j + temp < len(self.plansza[i - 1]):
                    self.plansza[i][j].sas_hexy.append(self.plansza[i - 1][j + temp])


    def sasiedztwo_srodki(self):
        for i in range(len(self.wierzcholki)):
            for j in range(len(self.wierzcholki[i])):
                sasiedztwo=self.wierzcholki[i][j].sas_wierz
                #lewy
                if j>0: sasiedztwo[self.wierzcholki[i][j-1]]=""

                #prawy
                if j<len(self.wierzcholki[i])-1: sasiedztwo[self.wierzcholki[i][j+1]]=""

                #dolny
                temp=0 if i<self.ilosc else 1
                temp2= 1 if i<self.ilosc-1 else 0 if i==self.ilosc-1 else -1
                if (j+temp)%2==0 and i<len(self.wierzcholki)-1: sasiedztwo[self.wierzcholki[i+1][j+temp2]]=""

                #gorny
                temp2 = 1 if i < self.ilosc else 0 if i == self.ilosc else -1
                if (j + temp) % 2 == 1 and i >0: sasiedztwo[self.wierzcholki[i - 1][j - temp2]]=""

    def ustawienie_hexow(self):
        surowce=[i%5 for i in range(self.ilosc_hexow-1)]+[5]
        for i in range(len(self.plansza)):
            for j in range(len(self.plansza[i])):
                wybor=surowce.copy()
                for a in self.plansza[i][j].sas_hexy:
                    while a.surowiec in wybor:
                        wybor.remove(a.surowiec)
                if len(wybor)==0:
                    print("Polegl hex")
                    wybor=surowce.copy()
                ustawienie=choice(wybor)
                surowce.remove(ustawienie)
                self.plansza[i][j].ustaw(ustawienie)


    def synchronizacja(self):
        #dodanie do hexow sasiednich srodkow i w druga strone
        for i in range(len(self.plansza)):
            for j in range(len(self.plansza[i])):
                temp = 0 if i<self.ilosc else 1
                temp2 = 0 if i < self.ilosc-1 else 1
                self.plansza[i][j].sas_wierz=[self.wierzcholki[i][2*j+k+temp] for k in range(3)]\
                                             +[self.wierzcholki[i+1][2*j+k+1-temp2] for k in range(3)]#gorne srodki + dolne
                for k in self.plansza[i][j].sas_wierz:
                    k.sas_hexy.append(self.plansza[i][j])

    def ustawienie_numerow(self):
        ilosc_liczb = self.ilosc_hexow // 2
        liczby=[(4 - i % 5 + 2) for i in range(ilosc_liczb)] #polowa od 2 do 6
        liczby+=[14-i for i in liczby] #polowa od 8 do 12
        for i in range(len(self.plansza)):
            for j in range(len(self.plansza[i])):
                if self.plansza[i][j].surowiec != 5:  # 5 to pustynia, ma nie miec numeru
                    wybor = liczby.copy()
                    for a in self.plansza[i][j].sas_hexy:
                        while a.numer in wybor:
                            wybor.remove(a.numer)
                        while 14 - a.numer in wybor:
                            wybor.remove(14 - a.numer)
                    if len(wybor) == 0:
                        print("Polegl numer")
                        wybor = liczby.copy()
                    ustawienie = choice(wybor)
                    liczby.remove(ustawienie)
                    self.plansza[i][j].dodaj_liczbe(ustawienie)
                else:
                    self.zlodziej_ustawienie(self.plansza[i][j])

    def przyciski_okna(self):
        self.przyciski=[]
        self.grupy=[]
        self.przyciski_dol()
        self.przyciski_lewo()
        self.przyciski_prawo()
        self.ranking()
        self.stan_surowcow()
        self.handlowanie()
        self.przycisk_anuluj=QPushButton(self)
        self.przycisk_anuluj.clicked.connect(self.odlaczenie)
        self.przycisk_anuluj.setGeometry(550*x,750*y,100*x,40*y)
        self.przycisk_anuluj.setText("Anuluj")
        self.przycisk_anuluj.hide()

    def przyciski_dol(self):
        grupa_dol=Okno(self)
        grupa_dol.setGeometry(0,750*y,1200*x,150*y)
        ilosc = 6
        odstep = (1200 / (1 + 3 * ilosc))*x
        przyciski_dol=[QPushButton(grupa_dol) for i in range(ilosc)]
        for i in range(len(przyciski_dol)):
            przyciski_dol[i].setGeometry(odstep + 3 * odstep * i, 100*y, 2 * odstep, 40*y)
            przyciski_dol[i].setFont(QFont("Arial",10*y))
            przyciski_dol[i].show()
        temp=QPushButton(grupa_dol)#koniec tury
        temp.setGeometry(600*x-odstep,40*y, 2 * odstep, 40*y)
        temp.setStyleSheet("background: orange")
        temp.setFont(QFont("Arial",8*y))
        przyciski_dol.append(temp)

        przyciski_dol[0].setText("Buduj miasto")
        przyciski_dol[1].setText("Ulepsz miasto")
        przyciski_dol[2].setText("Buduj droge")
        przyciski_dol[3].setText("Handel z wrogiem")
        przyciski_dol[4].setText("Kup karte akcji")
        przyciski_dol[5].setText("Handel 4:1")
        przyciski_dol[6].setText("Koniec tury")
        self.przyciski+=przyciski_dol
        self.przyciski_dol=przyciski_dol
        self.grupy.append(grupa_dol)

    def przyciski_lewo(self):
        ilosc=5
        grupa_lewo=Okno(self)
        grupa_lewo.setStyleSheet("Okno {background-color: yellow;  "
                                 "border-style: outset; "
                                 "border-width: 3px;  "
                                 "border-radius: 15px;   "
                                 "border-color: red;  "
                                 "padding: 6px; }")

        tytul=QLabel("Karty akcji",grupa_lewo)
        tytul.setGeometry(0,0,190*x,80*y)
        tytul.setAlignment(Qt.AlignCenter)
        tytul.setFont(QFont("Arial", 12*y, QFont.Bold))

        grupa_lewo.setGeometry(20*x, 420*y, 190*x, 380*y)
        przyciski_lewo=[QPushButton(grupa_lewo) for i in range(ilosc)]
        for i in range(ilosc):
            przyciski_lewo[i].setGeometry(35*x, 80*y + 60 * i*y, 120*x, 40*y)
            przyciski_lewo[i].setDisabled(True)
            przyciski_lewo[i].setFont(QFont("Arial",8*y))

        przyciski_lewo[0].setText("Rycerz")
        przyciski_lewo[1].setText("Budowa drog")
        przyciski_lewo[2].setText("Monopol")
        przyciski_lewo[3].setText("Wynalazek")
        przyciski_lewo[4].setText("Punkt zwyciestwa")
        self.przyciski+=przyciski_lewo
        self.przyciski_lewo=przyciski_lewo
        self.grupy.append(grupa_lewo)

    def przyciski_prawo(self):
        ilosc=6
        grupa_prawo=Okno(self)
        grupa_prawo.setStyleSheet("Okno {background-color: yellow;  "
                                 "border-style: outset; "
                                 "border-width: 3px;  "
                                 "border-radius: 15px;   "
                                 "border-color: red;  "
                                 "padding: 6px; }")


        tytul=QLabel("Handel specjalny",grupa_prawo)
        tytul.setGeometry(0,0,190*x,80*y)
        tytul.setAlignment(Qt.AlignCenter)
        tytul.setFont(QFont("Arial", 12*y, QFont.Bold))

        grupa_prawo.setGeometry(990*x, 370*y, 190*x, 440*y)
        przyciski_prawo=[QPushButton(grupa_prawo) for i in range(ilosc)]
        for i in range(ilosc):
            przyciski_prawo[i].setGeometry(35*x, (80 + 60 * i)*y, 120*x, 40*y)
            przyciski_prawo[i].setDisabled(True)
            przyciski_prawo[i].setFont(QFont("Arial",8*y))

        przyciski_prawo[0].setIcon(QIcon("obrazki/drewnoicon.png"))
        przyciski_prawo[0].setText("  Handel 2:1")
        przyciski_prawo[1].setIcon(QIcon("obrazki/welnaicon.png"))
        przyciski_prawo[1].setText("  Handel 2:1")
        przyciski_prawo[2].setIcon(QIcon("obrazki/zbozeicon.png"))
        przyciski_prawo[2].setText("  Handel 2:1")
        przyciski_prawo[3].setIcon(QIcon("obrazki/kamienicon.png"))
        przyciski_prawo[3].setText("  Handel 2:1")
        przyciski_prawo[4].setIcon(QIcon("obrazki/ceglaicon.png"))
        przyciski_prawo[4].setText("  Handel 2:1")
        for i in przyciski_prawo:
            i.setFont(QFont("Arial",8*y))
        for ind,i in enumerate(przyciski_prawo):
            i.clicked.connect(partial(self.handel_21,ind))
        przyciski_prawo[5].setText("Handel 3:1")
        przyciski_prawo[5].clicked.connect(self.handel_31)

        self.przyciski+=przyciski_prawo
        self.przyciski_prawo=przyciski_prawo
        self.grupy.append(grupa_prawo)

    def ranking(self):
        ilosc=5
        ranking=Okno(self)
        ranking.setStyleSheet("Okno {background-color: black;  "
                                 "border-style: outset; "
                                 "border-width: 3px;  "
                                 "border-radius: 15px;   "
                                 "border-color: red;  "
                                 "padding: 6px; }")

        tytul=QLabel("Ranking",ranking)
        tytul.setStyleSheet("color: red")
        tytul.setGeometry(0,0,190*x,80*y)
        tytul.setAlignment(Qt.AlignCenter)
        tytul.setFont(QFont("Arial", 12*y, QFont.Bold))

        ranking.setGeometry(20*x, 10*y, 190*x, 380*y)
        gracze_okna=[QPushButton(ranking) for i in range(ilosc)]
        for i in range(ilosc):
            gracze_okna[i].setGeometry(35*x, (70 + 60 * i)*y, 120*x, 50*y)
            gracze_okna[i].setFont(QFont("Arial",8*y))
        self.gracze_okna=gracze_okna
        self.grupy.append(ranking)
        self.ranking_aktualizacja()


    def ikony(self,i):
        t=20*x
        if i == 0: return QIcon(QPixmap("obrazki/drewnoicon.png").scaled(t,t))
        if i == 1: return QIcon(QPixmap("obrazki/welnaicon.png").scaled(t, t))
        if i == 2: return QIcon(QPixmap("obrazki/zbozeicon.png").scaled(t,t))
        if i == 3: return QIcon(QPixmap("obrazki/kamienicon.png").scaled(t, t))
        if i == 4: return QIcon(QPixmap("obrazki/ceglaicon.png").scaled(t, t))

    def stan_surowcow(self):
        surowce_okno=Okno(self)
        surowce_okno.setGeometry(990*x, 10*y, 190*x, 90*y)
        surowce_okno.setStyleSheet("Okno {background-color: teal;  "
                                 "border-style: outset; "
                                 "border-width: 3px;  "
                                 "border-radius: 15px;   "
                                 "border-color: red;  "
                                 "padding: 6px; }")
        tytul=QLabel("Surowce",surowce_okno)
        tytul.setGeometry(0,0,190*x,40*y)
        tytul.setAlignment(Qt.AlignCenter)
        tytul.setFont(QFont("Arial", 10*y, QFont.Bold))
        self.surowce=[QLabel(surowce_okno) for i in range(5)]
        self.surowceicon = [QPushButton(surowce_okno) for i in range(5)]
        for i in range(5):
            self.surowceicon[i].setGeometry((25+30*i)*x,40*y,20*x,20*y)
            self.surowceicon[i].setIcon(QIcon(self.ikony(i)))
            self.surowceicon[i].setStyleSheet("background-color: teal")
            self.surowce[i].setGeometry((25+30*i)*x, 60*y, 20*x, 20*y)
            self.surowce[i].setAlignment(Qt.AlignCenter)
            self.surowce[i].setFont(QFont("Arial",8*y))
        self.grupy.append(surowce_okno)
        self.surowce_aktualizacja()

    def handlowanie(self):
        self.sur_lewy=0
        self.sur_prawy=0
        handlowe=Okno(self)
        handlowe.setGeometry(990*x,110*y,190*x,250*y)
        handlowe.setStyleSheet("Okno {background-color: firebrick;  "
                                 "border-style: outset; "
                                 "border-width: 3px;  "
                                 "border-radius: 15px;   "
                                 "border-color: red;  "
                                 "padding: 6px; }")
        tytul=QLabel("Handel",handlowe)
        tytul.setGeometry(0,0,190*x,40*y)
        tytul.setAlignment(Qt.AlignCenter)
        tytul.setFont(QFont("Arial", 10*y, QFont.Bold))

        self.opcje=[QLineEdit(handlowe) for i in range(2)]
        self.opcje[0].setGeometry(50*x,70*y,40*x,30*y)
        self.opcje[1].setGeometry(100*x,70*y,40*x,30*y)
        self.opcje[1].setDisabled(1)


        self.tekst_surowca=[QLabel(handlowe) for i in range(2)]
        self.tekst_surowca[0].setGeometry(50*x,103*y,40*x,10*y)
        self.tekst_surowca[0].setText(str(4))
        self.tekst_surowca[1].setGeometry(100*x, 103*y, 40*x, 10*y)
        self.tekst_surowca[1].setText(str(1))

        for i in self.tekst_surowca:
            i.setAlignment(Qt.AlignCenter)
        przyciski = [QPushButton(handlowe) for i in range(5)]
        przyciski2 = [QPushButton(handlowe) for i in range(5)]
        odstep=190/26*x
        for i in range(5):
            przyciski[i].setGeometry(10,30*y+odstep+5*i*odstep,4*odstep,4*odstep)
            przyciski2[i].setGeometry(180*x-4 * odstep, 30*y + odstep + 5 * i * odstep, 4 * odstep, 4 * odstep)
            przyciski[i].setIcon(QIcon(self.ikony(i)))
            przyciski2[i].setIcon(QIcon(self.ikony(i)))
        akceptuj=QPushButton("Handluj",handlowe)
        akceptuj.setFont(QFont("Arial",8*y))
        akceptuj.setGeometry(65*x,130*y,60*x,30*y)
        akceptuj.clicked.connect(self.wymiana)
        self.opcje[0].editingFinished.connect(self.zmiany_wymiany)
        self.przyciski_wyboru_surowca=przyciski
        self.przyciski_zakupu_surowca=przyciski2
        self.sur_lewy = -1
        self.sur_lewy_liczba=4
        self.sur_prawy_liczba=1
        self.sur_prawy = -1
        self.grupy.append(handlowe)
        for i in range(5):
            przyciski[i].clicked.connect(partial(self.wybor_surowca,i))
            przyciski2[i].clicked.connect(partial(self.zakup_surowca,i))
            przyciski[i].setStyleSheet("background: white")
            przyciski2[i].setStyleSheet("background: white")

    def zmiany_wymiany(self):
        if self.sur_lewy==-1:
            self.komunikat.setText("Najpierw ustaw surowiec")
            self.opcje[0].setText("")
        else:
            temp=self.opcje[0].text()
            if temp.isdigit()==True:
                temp=int(temp)
                if temp>self.gracze[self.obecny].surowce[self.sur_lewy]:
                    temp=self.gracze[self.obecny].surowce[self.sur_lewy]
                temp=temp//self.sur_lewy_liczba*self.sur_lewy_liczba
            else:
                temp=""
            self.opcje[0].setText(str(temp))
            self.opcje[1].setText(str(temp//self.sur_lewy_liczba))


    def wybor_surowca(self,wybor):
        temp=self.przyciski_wyboru_surowca
        if temp!=-1:
            temp[self.sur_lewy].setStyleSheet("background: white")
        self.sur_lewy=wybor
        temp[wybor].setStyleSheet("background: red")

    def zakup_surowca(self,wybor):
        temp=self.przyciski_zakupu_surowca
        if temp!=-1:
            temp[self.sur_prawy].setStyleSheet("background: white")
        self.sur_prawy=wybor
        temp[wybor].setStyleSheet("background: red")



    def porty_kandydaci(self):
        #uczestnicy - wszystkie elementy (srodki) zewnetrzne z self.wierzcholek
        #kandydaci - grupy po 3 srodki, w kazdej grupie jeden srodek bedzie usuwany
        ilosc_portow=2*self.ilosc
        poczatek=randint(0,self.ilosc)
        uczestnicy=[self.wierzcholki[0][i] for i in range(0,len(self.wierzcholki[0])-2)]+\
                  [self.wierzcholki[i//2][len(self.wierzcholki[i//2])-1-(i+1)%2] for i in range(0, 2*self.ilosc)]+\
                  [self.wierzcholki[i//2][len(self.wierzcholki[i//2])-1-i%2] for i in range(2*self.ilosc, 4*self.ilosc-2)]+\
                  [self.wierzcholki[-1][i] for i in range(len(self.wierzcholki[-1])-1,1,-1)]+\
                  [self.wierzcholki[i//2][i%2] for i in range(4*self.ilosc-1, 2*self.ilosc-1,-1)]+\
                  [self.wierzcholki[i//2][(i+1)%2] for i in range(2*self.ilosc-1, 1,-1)]

        kandydaci=[[uczestnicy[(int(i)%len(uczestnicy)+j)%len(uczestnicy)] for j in range(-1,2)] for i in arange(poczatek,len(uczestnicy)+poczatek,len(uczestnicy)/ilosc_portow)]

        for i in kandydaci:
            del i[choice([0,2])]
        return kandydaci

    def porty_wstawianie(self):
        #wstawianie portow pomiedzy srodkami wskazanymi przed kandydatow
        wybrancy=self.porty_kandydaci()
        wybor=[i%5 for i in range(len(wybrancy)//5*5)]
        wybor+=[5 for i in range(len(wybrancy)-len(wybor))]
        self.porty=[]

        #ustawienie tak, zeby porty nie staly na hexie surowca ktory wymieniaja
        for a in range(len(wybrancy)):
            i=wybrancy[a]
            temp=wybor.copy()
            for j in (i[0].sas_hexy + i[1].sas_hexy):
                if j.surowiec in temp:
                    temp.remove(j.surowiec)
            if len(temp)==0:
                print("Polegl port")
                temp=wybor.copy()
            ustawienie=choice(temp)
            wybor.remove(ustawienie)
            i[0].handel,i[1].handel=ustawienie,ustawienie

            #wstawienie portu na mapke
            self.porty.append(Port(ustawienie))
            self.porty[a].setZValue(3)
            self.porty[a].setPos((i[0].pos().x()+i[1].pos().x())//2,(i[0].pos().y()+i[1].pos().y())//2)
            self.scene.addItem(self.porty[a])

    def aktualizacja(self):
        self.surowce_aktualizacja()
        self.kartyAkcji_aktualizacja()
        self.ranking_aktualizacja()
        self.handel_aktualizacja()
        self.komunikat_aktualizacja()
        self.wymiana_aktualizacja()

    def surowce_aktualizacja(self):
        self.surowiec_wybrany=-1
        temp=self.gracze[self.obecny].surowce
        for i in range(5):
            self.surowce[i].setText(str(temp[i]))
        self.ranking_aktualizacja()

    def kartyAkcji_aktualizacja(self):
        temp=self.gracze[self.obecny].karty_akcji
        nazwy=["Rycerz","Budowa drog","Monopol","Wynalazek","Punkt zwyciestwa"]
        for i in range(5):
            self.przyciski_lewo[i].setText(nazwy[i])
            if temp[i]==0:
                self.przyciski_lewo[i].setDisabled(1)
            else:
                self.przyciski_lewo[i].setDisabled(0)
                self.przyciski_lewo[i].setText(self.przyciski_lewo[i].text()+"(%d)"%temp[i])

    def ranking_aktualizacja(self):
        temp=copy(self.gracze)
        temp.sort()
        for i in range(len(temp)):
            self.gracze_okna[i].setStyleSheet("background-color: black;  "
                                 "color:"+temp[i].kolor+";"
                                 "border-style: outset; "
                                 "border-width: 3px;  "
                                 "border-radius: 15px;   "
                                 "border-color: red;  ")
            self.gracze_okna[i].setText(str(i+1)+". "+temp[i].imie+
                                        "\nPunkty: "+str(temp[i].punkty)+
                                        "\nSurowce: "+str(sum(temp[i].surowce)))

    def handel_aktualizacja(self):
        temp=self.gracze[self.obecny].wymiany_specjalne
        for i in range(6):
            if temp[i]==1:
                self.przyciski_prawo[i].setDisabled(0)
            else:
                self.przyciski_prawo[i].setDisabled(1)


    def komunikat_aktualizacja(self):
        self.komunikat.setText("Teraz ruch wykonuje: " + self.gracze[self.obecny].imie)

    def wymiana_aktualizacja(self):
        for i in self.przyciski_zakupu_surowca+self.przyciski_wyboru_surowca:
            i.setStyleSheet("background: white")
            i.setDisabled(0)
        self.opcje[0].setText("")
        self.opcje[1].setText("")
        self.sur_lewy=-1
        self.sur_prawy=-1
        self.sur_lewy_liczba=4
        self.sur_prawy_liczba=1
        self.tekst_surowca[0].setText(str(4))
        self.tekst_surowca[1].setText(str(1))

    def polaczenia(self):
        self.przyciski_dol[0].clicked.connect(self.budowa_miasta)
        self.przyciski_dol[1].clicked.connect(self.ulepszenie_miasta)
        self.przyciski_dol[2].clicked.connect(self.budowa_drogi)
        self.przyciski_dol[3].clicked.connect(self.handel_z_wrogiem)
        self.przyciski_dol[4].clicked.connect(self.kup_karte_akcji)
        self.przyciski_dol[5].clicked.connect(self.handel_41)
        self.przyciski_dol[6].clicked.connect(self.koniec_tury)

        self.przyciski_lewo[0].clicked.connect(self.rycerz)
        self.przyciski_lewo[1].clicked.connect(self.budowa_drog)
        self.przyciski_lewo[2].clicked.connect(self.monopol)
        self.przyciski_lewo[3].clicked.connect(self.wynalazek)
        self.przyciski_lewo[4].clicked.connect(self.punkt_zwyciestwa)

    def odlaczenie(self):
        for j in concatenate(self.wierzcholki):
            try:
                j.s.c.disconnect()
            except Exception:
                pass
            j.setBrush(QColor(j.kolor))

        for i in self.surowceicon:
            try:
                i.clicked.disconnect()
            except Exception:
                pass

        for i in self.grupy:
            i.show()

        self.przycisk_anuluj.hide()
        self.komunikat.setText(choice(["Niezdecydowany?",
                                       "Lepiej zrobić lepszy ruch",
                                       "Przez przypadek wcisnales, prawda?",
                                       "Ale to naprawdę mógl byc dobry ruch",
                                       "Patrz, jak gre wydłużasz"]))


    def koniec_tury(self):
        if self.gracze[self.obecny].wygral()==True:
            self.komunikat.setText(self.gracze[self.obecny].imie+" zostal zwyciezca tej gry")
            for i in range(3):
                self.grupy[i].hide()
        else:
            self.obecny=(self.obecny+1)%len(self.gracze)
            self.komunikat.setStyleSheet("background: %s"%self.gracze[self.obecny].kolor)
            self.aktualizacja()
            temp=rzut()
            self.komunikat.setText("Wylosowana liczba: %d"%temp+"\n"+self.komunikat.text())
            if temp!=7:
                for i in self.gracze:
                    for j in range(len(i.surowce)):
                        i.surowce[j]+=i.przychod[temp][j]
                self.surowce_aktualizacja()
            else:
                self.zlodziej_zmiana()

    def budowa_miasta(self):
        temp = self.gracze[self.obecny].surowce
        if temp[0] >= 1 and temp[1] >= 1 and temp[2] >= 1 and temp[4] >= 1:

            self.komunikat.setText("Wybierz srodek do budowy miasta")
            #zdejmowanie z widoku przyciskow
            for i in range(3):
                self.grupy[i].hide()
            self.przycisk_anuluj.show()
            #na klikniecie srodka uruchamiana jest funkcja budujmy_miasto
            for j in concatenate(self.wierzcholki):
                j.s.c.connect(self.budujmy_miasto)
                if j.miasto=="" and self.jest_droga(j)==True:
                    j.setBrush(QColor("blue"))
        else:
            self.komunikat.setText("Nie stac Cie")


    def budujmy_miasto(self):
        if self.zaznaczony.miasto=="" and self.jest_droga(self.zaznaczony)==True:
            temp = self.gracze[self.obecny].surowce
            gracz= self.gracze[self.obecny]
            self.komunikat.setText("Miasto wybudowane")

            gracz.surowce[0]-=1
            gracz.surowce[1]-=1
            gracz.surowce[2]-=1
            gracz.surowce[4]-=1

            self.surowce_aktualizacja()
            self.zaznaczony.setBrush(QBrush(QColor(gracz.kolor)))
            self.zaznaczony.kolor=gracz.kolor
            self.zaznaczony.miasto=gracz.imie
            for i in self.zaznaczony.sas_wierz.keys():
                i.miasto="-1"

            #wzrost przychodu
            for i in self.zaznaczony.sas_hexy:
                if i.surowiec!=5 and i!=self.zlodziej:
                    gracz.przychod[i.numer][i.surowiec]+=1

            #dodanie ewentualnych portow
            if self.zaznaczony.handel!=-1:
                gracz.wymiany_specjalne[self.zaznaczony.handel]=1
                self.handel_aktualizacja()

            #dodanie punktow
            self.gracze[self.obecny].punkty+=1
            self.ranking_aktualizacja()

            #powrot okien
            for i in range(3):
                self.grupy[i].show()
            self.przycisk_anuluj.hide()
            for j in concatenate(self.wierzcholki):
                j.s.c.disconnect()

                j.setBrush(QColor(j.kolor))
        elif self.jest_droga(self.zaznaczony)==False:
            self.komunikat.setText("Brak polaczenia")
        else:
            self.komunikat.setText("Nie mozna wybudowac")

    def ulepszenie_miasta(self):
        temp = self.gracze[self.obecny].surowce
        if temp[2] >= 2 and temp[3] >= 2:
            self.komunikat.setText("Wybierz miasto do ulepszenia")
            # zdejmowanie z widoku przyciskow
            for i in range(3):
                self.grupy[i].hide()
            self.przycisk_anuluj.show()
            for i in self.wierzcholki:
                for j in i:
                    j.s.c.connect(self.ulepszmy_miasto)
        else:
            self.komunikat.setText("Nie stac Cie")

    def ulepszmy_miasto(self):
        temp = self.gracze[self.obecny].surowce
        gracz=self.gracze[self.obecny]
        if self.zaznaczony.miasto!="" and self.zaznaczony.miasto==gracz.imie and self.zaznaczony.ulepszone==False:
            self.komunikat.setText("Miasto ulepszone")
            temp[2]-=2
            temp[3]-=2
            self.surowce_aktualizacja()
            self.zaznaczony.ulepszenie()
            self.zaznaczony.ulepszone=True

            #dodanie punktow
            self.gracze[self.obecny].punkty+=1
            self.ranking_aktualizacja()

            #wzrost przychodu
            for i in self.zaznaczony.sas_hexy:
                if i.surowiec!=5 and i!=self.zlodziej:
                    gracz.przychod[i.numer][i.surowiec]+=1

            #powrot okien
            for i in range(3):
                self.grupy[i].show()
            self.przycisk_anuluj.hide()

            for i in self.wierzcholki:
                for j in i:
                    j.s.c.disconnect()
        else:
            self.komunikat.setText("Niepoprawne miejsce")

    def jest_droga(self, wierz):
        temp=wierz.sas_wierz
        for i in temp.keys():
            if temp[i]==self.gracze[self.obecny].imie:
                return True
        return False


    def budowa_drogi(self):
        temp = self.gracze[self.obecny].surowce
        self.drogowe=[]
        if temp[0] >= 1 and temp[4] >= 1:
            # zdejmowanie z widoku przyciskow
            for i in range(3):
                self.grupy[i].hide()
            self.przycisk_anuluj.show()
            self.komunikat.setText("Wybierz pierwszy srodek (z polaczeniem)")
            for i in self.wierzcholki:
                for j in i:
                    j.s.c.connect(self.buduj_droge1)
        else:
            self.komunikat.setText("Nie stac Cie")

    def buduj_droge1(self):
        if self.jest_droga(self.zaznaczony)==True:
            self.drogowe.append(self.zaznaczony)
            self.zaznaczony.setBrush(Qt.lightGray)
            self.komunikat.setText("Wybierz drugi srodek")
            for i in self.wierzcholki:
                for j in i:
                    j.s.c.disconnect()
                    j.s.c.connect(self.buduj_droge2)
        else:
            self.komunikat.setText("Brak polaczenia")

    def buduj_droge2(self):
        temp = self.gracze[self.obecny].surowce
        self.drogowe.append(self.zaznaczony)
        if (self.drogi_sasiaduja(self.drogowe[0],self.drogowe[1]) and self.wolne_drogi(self.drogowe[0],self.drogowe[1]))==True:
            temp[0] -= 1
            temp[4] -= 1
            self.komunikat.setText("Droga gotowa")
            self.wstawianie_drogi(self.drogowe, self.gracze[self.obecny])
            # powrot okien
            for i in range(3):
                self.grupy[i].show()
            self.przycisk_anuluj.hide()

            for i in self.wierzcholki:
                for j in i:
                    j.s.c.disconnect()
        else:
            self.komunikat.setText("Nie w porzadku drugi koniec")
            self.drogowe.pop()

    def wstawianie_drogi(self,drogowe, gracz):
        drogowe[0].sas_wierz[drogowe[1]]=gracz.imie
        drogowe[1].sas_wierz[drogowe[0]]=gracz.imie
        drogowe[0].setBrush(QColor(drogowe[0].kolor))
        self.surowce_aktualizacja()
        temp1=drogowe[0].pos()
        temp2=drogowe[1].pos()
        linia=QGraphicsLineItem()
        linia.setLine(temp1.x()+10*x,temp1.y()+10*y,temp2.x()+10*x,temp2.y()+10*y)
        pen=QPen(QColor(gracz.kolor))
        pen.setWidth(8)
        linia.setPen(pen)
        linia.setZValue(0)
        self.scene.addItem(linia)


    def handel_z_wrogiem(self):
        pass

    def kup_karte_akcji(self):
        temp = self.gracze[self.obecny].surowce
        gracz = self.gracze[self.obecny]
        if temp[1]>=1 and temp[2]>=1:
            temp[1]-=1
            temp[2]-=1
            wybor=[0,0,0,1,2,3,4]
            gracz.karty_akcji[choice(wybor)]+=1
            self.kartyAkcji_aktualizacja()
            self.surowce_aktualizacja()
            self.komunikat.setText("Karta zakupiona")
        else:
            self.komunikat.setText("Nie stac Cie")

    def monopol(self):
        gracz = self.gracze[self.obecny]
        self.komunikat.setText("Kliknij odpowiedni surowiec")
        for i in range(4):
            self.grupy[i].hide()
        self.grupy[5].hide()
        for ind, i in enumerate(self.surowceicon):
            i.clicked.connect(partial(self.monopol_akcja,ind))
        self.przycisk_anuluj.show()

    def rycerz(self):
        self.gracze[self.obecny].karty_akcji[0]-=1
        self.zlodziej_zmiana()
        self.kartyAkcji_aktualizacja()

    def monopol_akcja(self,wybor):
        self.gracze[self.obecny].karty_akcji[2]-=1
        self.ranking_aktualizacja()
        self.kartyAkcji_aktualizacja()
        self.surowiec_wybrany=wybor
        suma=0
        for i in self.gracze:
            if i!=self.gracze[self.obecny]:
                suma+=i.surowce[wybor]
                i.surowce[wybor]=0
        self.gracze[self.obecny].surowce[wybor]+=suma
        temp=["Dostałeś w prezencie od graczy {} surowcow",
              "{} surowce trafiają do twych rąk",
              "O ty niedobry, dostałem {} surowców",
              "Ale ich wkurzyles, stracili {} surowców",
              "Oni się jeszcze zemszczą za te {} surowców",
              "W twoim magazynie nagle pojawiło się {} dodatkowych surowców"
              ]
        self.komunikat.setText(choice(temp).format(suma))

        for i in self.surowceicon:
            i.clicked.disconnect()

        for i in self.grupy:
            i.show()
        self.przycisk_anuluj.hide()

        self.surowce_aktualizacja()

    def wynalazek(self):
        for i in range(4):
            self.grupy[i].hide()
        self.grupy[5].hide()
        self.przycisk_anuluj.show()
        self.komunikat.setText("Kliknij surowiec, ktory chcesz dostać 2 razy")
        for ind,i in enumerate(self.surowceicon):
            i.clicked.connect(partial(self.wynalazkuj,ind))

    def wynalazkuj(self, i):
        self.gracze[self.obecny].surowce[i]+=2
        self.gracze[self.obecny].karty_akcji[3]-=1
        self.surowce_aktualizacja()
        self.kartyAkcji_aktualizacja()
        temp=["Mamy to",
                     "Surowiec odebrany",
                     "Nowe surowce dodane do magazynu"
                     ]
        self.komunikat.setText(choice(temp))
        for i in self.surowceicon:
            i.clicked.disconnect()

        for i in self.grupy:
            i.show()
        self.przycisk_anuluj.hide()

    def punkt_zwyciestwa(self):
        gracz=self.gracze[self.obecny]
        gracz.karty_akcji[4]-=1
        gracz.punkty+=1
        self.komunikat.setText(choice(["Oto dodatkowy punkt","Jeszcze Ci mało punktów","I co, wygrałeś", "Zwyciestwo jest coraz blizej", "Ale jazda"]))
        self.ranking_aktualizacja()
        self.kartyAkcji_aktualizacja()

    def budowa_drog(self):
        pass


    def handel_41(self):
        self.wymiana_aktualizacja()
        for i in self.przyciski_wyboru_surowca:
            i.setDisabled(0)
        self.sur_lewy_liczba=4
        self.sur_prawy_liczba=1
        self.tekst_surowca[0].setText(str(4))
        self.tekst_surowca[1].setText(str(1))

    def handel_31(self):
        self.wymiana_aktualizacja()
        for i in self.przyciski_wyboru_surowca:
            i.setDisabled(0)
        self.sur_lewy_liczba=3
        self.sur_prawy_liczba=1
        self.tekst_surowca[0].setText(str(3))
        self.tekst_surowca[1].setText(str(1))
        

    def handel_21(self, wybor):
        self.wymiana_aktualizacja()
        for ind,i in enumerate(self.przyciski_wyboru_surowca):
            if ind!=wybor:
                i.setDisabled(1)
            else:
                i.setDisabled(0)
                self.wybor_surowca(ind)
        self.sur_lewy_liczba=2
        self.sur_prawy_liczba=1
        self.tekst_surowca[0].setText(str(2))
        self.tekst_surowca[1].setText(str(1))

    def wymiana(self):
        if self.opcje[0].text() in ["","0"]:
            self.komunikat.setText(choice(["W sumie nie ma co wymieniać","Bieda","Nie masz tyle surowca by wymienic"]))
        elif self.sur_prawy==-1:
            self.komunikat.setText("Nie wybrałeś co chcesz wybrać")
        elif self.sur_prawy==self.sur_lewy:
            self.komunikat.setText("Nie, nie ma wymiany tego samego na to samo")
        else:
            self.gracze[self.obecny].surowce[self.sur_lewy] -= int(self.opcje[0].text())
            self.gracze[self.obecny].surowce[self.sur_prawy] += int(self.opcje[1].text())
            temp=["Masz co chciałeś",
                  "I po tej wymianie może złodziej Cię nie dorwie",
                  "Wymiana udana"]
            self.komunikat.setText(choice(temp))
            self.surowce_aktualizacja()
            self.ranking_aktualizacja()
            self.opcje[0].setText("")
            self.opcje[1].setText("")
            if self.sur_lewy_liczba!=2:
                self.przyciski_wyboru_surowca[self.sur_lewy].setStyleSheet("background: white")
                self.sur_lewy = -1
            self.przyciski_zakupu_surowca[self.sur_prawy].setStyleSheet("background: white")
            self.sur_prawy = -1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Gra()
    window.show()
    sys.exit(app.exec_())