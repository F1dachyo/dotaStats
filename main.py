import sys
import requests as r
import sqlite3

from mainstat import statLoad, loadStat
from searchPlayerById import statLoadById, loadStatById

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import QtCore

import qdarktheme

# 1036324778
# 1141093430


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled.ui', self)
        self.setWindowTitle('DotaStats')
        self.con = sqlite3.connect('dotastats.sqlite3')
        self.cur = self.con.cursor()
        if open('theme.txt', mode='r').read() == 'Light':
            qdarktheme.setup_theme("auto")
        else:
            qdarktheme.setup_theme("dark")
        if r.get('https://api.opendota.com/api/players/1141093430').status_code == 200:
            loadStat(self)
        else:
            self.statusBar().showMessage('Api Error')
        statLoad(self)
        statLoadById(self)
        self.updateStat.clicked.connect(self.upSt)
        self.changeId2.clicked.connect(self.chId2)
        self.updateStat2.clicked.connect(self.upSt2)
        self.settings.clicked.connect(self.show_setting)

    def upSt(self):
        if r.get('https://api.opendota.com/api/players/1141093430').status_code == 200:
            loadStat(self)
            statLoad(self)
        else:
            self.statusBar().showMessage('Api Error')

    def chId2(self):
        if r.get('https://api.opendota.com/api/players/1141093430').status_code == 200:
            if r.get(f'https://api.opendota.com/api/players/{self.changeIdEdit2.text()}/wl').json() not in \
                    [{'win': 0, 'lose': 0}, {'error': 'invalid account id'}]:
                loadStatById(self, self.changeIdEdit2.text())
                statLoadById(self)
                self.changeIdEdit2.setText('')
            else:
                self.changeIdEdit.setText('')
                self.statusBar().showMessage('Id Error')
        else:
            self.changeIdEdit2.setText('')
            self.statusBar().showMessage('Api Error')

    def upSt2(self):
        if r.get('https://api.opendota.com/api/players/1141093430').status_code == 200:
            loadStatById(self)
            statLoadById(self)
        else:
            self.statusBar().showMessage('Api Error')

    def show_setting(self):
        self.con = sqlite3.connect('dotastats.sqlite3')
        self.cur = self.con.cursor()
        self.set = SettingWindow()
        self.set.setWindowModality(QtCore.Qt.ApplicationModal)
        self.set.show()


class SettingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled1.ui', self)
        self.setWindowTitle('Settings')
        self.con = sqlite3.connect('dotastats.sqlite3')
        self.cur = self.con.cursor()
        self.lineEdit.setText(str(self.cur.execute('SELECT id FROM playerStats').fetchall()[0][0]))
        if open('theme.txt', mode='r').read() == 'Light':
            self.comboBox.addItems(['Light', 'Dark'])
        else:
            self.comboBox.addItems(['Dark', 'Light'])
        self.cancel.clicked.connect(self.close)
        self.accept.clicked.connect(self.saveSetting)

    def saveSetting(self):
        valid = QMessageBox.question(self, '', 'Do you really want to accept the settings?',
                                     QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            old = self.cur.execute('SELECT id FROM playerStats').fetchall()[0][0]
            old1 = open('theme.txt', mode='r').read()
            if r.get('https://api.opendota.com/api/players/1141093430').status_code == 200:
                if r.get(f'https://api.opendota.com/api/players/{self.lineEdit.text()}/wl').json() not in \
                        [{'win': 0, 'lose': 0}, {'error': 'invalid account id'}]:
                    qw = self.cur.execute('SELECT * FROM playerStats').fetchall()
                    qw = list(qw[0])
                    qw[0] = self.lineEdit.text()
                    self.cur.execute(f'DELETE FROM playerStats')
                    self.cur.execute('INSERT INTO playerStats (id, name, url, rank_tier, avatar,'
                                     'avatarmedium,avatarfull, win, lose, kills, deaths, assists)'
                                     'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', qw)
                else:
                    ex.statusBar().showMessage('Id Error')
            else:
                ex.statusBar().showMessage('Api Error')
            open('theme.txt', mode='w').write(self.comboBox.currentText())
            if old != self.cur.execute('SELECT id FROM playerStats').fetchall()[0][0]:
                self.con.commit()
                self.con.close()
                statLoad(ex)
                ex.upSt()
            if old1 != open('theme.txt', mode='r').read():
                if open('theme.txt', mode='r').read() == 'Light':
                    qdarktheme.setup_theme("auto")
                else:
                    qdarktheme.setup_theme("dark")
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
