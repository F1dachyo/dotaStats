import requests as r
import sqlite3
from urllib.request import urlopen

from PyQt5.Qt import *
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QLabel
from PyQt5.QtGui import QPixmap


def creatTableInDb(self):
    self.cur.execute('''
    CREATE TABLE IF NOT EXISTS playerHeroesById (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    game INTEGER,
    wr REAL
    )
    ''')

    self.cur.execute('''
    CREATE TABLE IF NOT EXISTS playerMatchesById (
    id INTEGER PRIMARY KEY,
    hero TEXT NOT NULL,
    duration INTEGER,
    wl TEXT NOT NULL,
    kills INTEGER,
    deaths INTEGER,
    assists INTEGER
    )
    ''')

    self.cur.execute('''
    CREATE TABLE IF NOT EXISTS playerPeersById (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    game INTEGER,
    wr REAL,
    avatar BLOB,
    avatarfull BLOB
    )
    ''')

    self.cur.execute('''
    CREATE TABLE IF NOT EXISTS playerStatsById (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    rank_tier INTEGER,
    avatar BLOB,
    avatarmedium BLOB,
    avatarfull BLOB,
    win INTEGER,
    lose INTEGER,
    kills INTEGER,
    deaths INTEGER,
    assists INTEGER
    )
    ''')


def getRes(id):
    res1 = r.get(f'https://api.opendota.com/api/players/{id}')
    res2 = r.get(f'https://api.opendota.com/api/players/{id}/wl')
    res3 = r.get(f'https://api.opendota.com/api/players/{id}/heroes')
    res4 = r.get(f'https://api.opendota.com/api/players/{id}/matches', params={'limit': 5})
    res5 = r.get(f'https://api.opendota.com/api/players/{id}/peers')
    res6 = r.get(f'https://api.opendota.com/api/players/{id}/totals')
    return (res1, res2, res3, res4, res5, res6)


def clearDb(self):
    self.cur.execute(f'DELETE FROM playerStatsById')
    self.cur.execute(f'DELETE FROM playerPeersById')
    self.cur.execute(f'DELETE FROM playerHeroesById')
    self.cur.execute(f'DELETE FROM playerMatchesById')


def loadStatInDb(self, res1, res2, res3, res4, res5, res6):
    for i in res3.json():
        if i['games'] > 0:
            self.cur.execute('INSERT INTO playerHeroesById (id, name, game, wr)'
                             'VALUES (?, ?, ?, ?)',
                             (i['hero_id'],
                              str(self.cur.execute(f'SELECT localized_name FROM heroes WHERE id = "{i["hero_id"]}"')
                                  .fetchall()[0][0]),
                              i['games'], str(round((i['win'] / i['games']) * 100, 2)) + '%'))

    for i in res4.json():
        ww = ''
        if i['radiant_win'] and i['player_slot'] in list(range(0, 5)):
            ww = 'win'
        elif not i['radiant_win'] and i['player_slot'] in list(range(128, 133)):
            ww = 'win'
        elif not i['radiant_win'] and i['player_slot'] in list(range(0, 5)):
            ww = 'lose'
        elif i['radiant_win'] and i['player_slot'] in list(range(128, 133)):
            ww = 'lose'
        self.cur.execute('INSERT INTO playerMatchesById (id, hero, duration, wl, kills, deaths, assists)'
                         'VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (i['match_id'],
                          str(self.cur.execute(f'SELECT localized_name FROM heroes WHERE id = "{i["hero_id"]}"')
                              .fetchall()[0][0]),
                          i['duration'], ww, i['kills'], i['deaths'], i['assists']))

    for i in res5.json()[:5]:
        self.cur.execute('INSERT INTO playerPeersById (id, name, game, wr, avatar, avatarfull)'
                         'VALUES (?, ?, ?, ?, ?, ?)',
                         (i['account_id'], i['personaname'],
                          i['games'], str(round((i['win'] / i['games']) * 100, 2)) + '%',
                          urlopen(i['avatar']).read(), urlopen(i['avatarfull']).read()))

    self.cur.execute('INSERT INTO playerStatsById (id, name, url, rank_tier, avatar,'
                     'avatarmedium,avatarfull, win, lose, kills, deaths, assists)'
                     'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (res1.json()['profile']['account_id'], res1.json()['profile']['personaname'],
                      res1.json()['profile']['profileurl'], res1.json()['rank_tier'],
                      urlopen(res1.json()['profile']['avatar']).read(),
                      urlopen(res1.json()['profile']['avatarmedium']).read(),
                      urlopen(res1.json()['profile']['avatarfull']).read(), res2.json()['win'], res2.json()['lose'],
                      res6.json()[0]['sum'], res6.json()[1]['sum'], res6.json()[2]['sum']))


def loadStatById(self, id=0):
    if r.get('https://api.opendota.com/api/players/1141093430').status_code == 200:
        self.con = sqlite3.connect('dotastats.sqlite3')
        self.cur = self.con.cursor()
        if not id:
            id = self.cur.execute("SELECT * FROM playerStatsById").fetchall()[0][0]
        creatTableInDb(self)
        clearDb(self)
        res = getRes(id)
        loadStatInDb(self, res[0], res[1], res[2], res[3], res[4], res[5])
        self.con.commit()
        self.con.close()
    else:
        self.statusBar().showMessage('Api Error')


def statLoadById(self):
    self.con = sqlite3.connect('dotastats.sqlite3')
    self.cur = self.con.cursor()
    stats = self.cur.execute('SELECT * FROM playerStatsById').fetchall()[0]
    self.playerName2.setText(stats[1])
    self.playerId2.setText(str(stats[0]))
    self.wlZn2.setText(f'{stats[7]}-{stats[8]}')
    self.wrZn2.setText(str(round((stats[7] / (stats[7] + stats[8])) * 100, 2)) + '%')
    qp = QPixmap()
    qp.loadFromData(stats[5])
    self.playerAvatar2.setPixmap(qp)
    if type(stats[3]) == int:
        icon = stats[3] // 10 * 10
        star = stats[3] % 10
        qp = QPixmap()
        qp.loadFromData(self.cur.execute(f'SELECT icon FROM rank WHERE id = {icon}').fetchall()[0][0])
        qp1 = qp.scaled(64, 64)
        self.rankIcon2.setPixmap(qp1)
        qp = QPixmap()
        qp.loadFromData(self.cur.execute(f'SELECT icon FROM rank WHERE id = {star}').fetchall()[0][0])
        qp1 = qp.scaled(64, 64)
        self.rankStar2.setPixmap(qp1)
    elif not stats[3]:
        qp = QPixmap()
        qp.loadFromData(self.cur.execute(f'SELECT icon FROM rank WHERE id = 0').fetchall()[0][0])
        qp1 = qp.scaled(64, 64)
        self.rankIcon2.setPixmap(qp1)
        qp = QPixmap()
        qp.loadFromData(self.cur.execute(f'SELECT icon FROM rank WHERE id = 100').fetchall()[0][0])
        qp1 = qp.scaled(64, 64)
        self.rankStar2.setPixmap(qp1)


    result = self.cur.execute('SELECT * FROM playerHeroesById ORDER BY game DESC').fetchall()[:5]
    self.mostHero2.setRowCount(5)
    self.mostHero2.setColumnCount(4)
    self.mostHero2.setHorizontalHeaderLabels(['Hero', '', 'Matches', 'Win %'])
    self.mostHero2.setEditTriggers(QAbstractItemView.NoEditTriggers)
    header = self.mostHero2.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
    for i, row in enumerate(result):
        for j, elem in enumerate(row):
            if j == 0:
                res = self.cur.execute(f'SELECT avatar FROM heroesAvatar WHERE id = {elem}').fetchall()
                pixmap = QPixmap()
                pixmap.loadFromData(res[0][0])
                label = QLabel()
                label.setPixmap(pixmap.scaled(89, 50))
                label.setAlignment(Qt.AlignCenter)
                self.mostHero2.setCellWidget(i, j, label)
            else:
                self.mostHero2.setItem(i, j, QTableWidgetItem(str(elem)))

    result = self.cur.execute('SELECT * FROM playerMatchesById ORDER BY id DESC').fetchall()
    self.lastMatch2.setRowCount(5)
    self.lastMatch2.setColumnCount(5)
    self.lastMatch2.setHorizontalHeaderLabels(['Id', 'Hero', 'Result', 'Duration', 'KDA'])
    self.lastMatch2.setEditTriggers(QAbstractItemView.NoEditTriggers)
    header = self.lastMatch2.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
    result = [[self.cur.execute(f"SELECT id FROM heroes WHERE localized_name = '{i[1]}'").fetchall()[0][0], i[1], i[3],
               f'{i[2] // 60}:{i[2] % 60}', f'{i[4]}/{i[5]}/{i[6]}'] for i in result]
    for i, row in enumerate(result):
        for j, elem in enumerate(row):
            if j == 0:
                res = self.cur.execute(f'SELECT avatar FROM heroesAvatar WHERE id = {elem}').fetchall()
                pixmap = QPixmap()
                pixmap.loadFromData(res[0][0])
                label = QLabel()
                label.setPixmap(pixmap.scaled(89, 50))
                label.setAlignment(Qt.AlignCenter)
                self.lastMatch2.setCellWidget(i, j, label)
            else:
                self.lastMatch2.setItem(i, j, QTableWidgetItem(str(elem)))

    result = self.cur.execute('SELECT * FROM playerPeersById ORDER BY game DESC').fetchall()
    self.friends2.clear()
    self.friends2.setRowCount(5)
    self.friends2.setColumnCount(4)
    self.friends2.setHorizontalHeaderLabels(['Avatar', 'Name', 'Game', 'Wr'])
    self.friends2.setEditTriggers(QAbstractItemView.NoEditTriggers)
    header = self.friends2.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
    result = [[i[4], i[1], i[2], i[3]] for i in result]
    for i, row in enumerate(result):
        for j, elem in enumerate(row):
            if j == 0:
                pixmap = QPixmap()
                pixmap.loadFromData(elem)
                label = QLabel()
                label.setPixmap(pixmap.scaled(32, 32))
                label.setAlignment(Qt.AlignCenter)
                self.friends2.setCellWidget(i, j, label)
            else:
                self.friends2.setItem(i, j, QTableWidgetItem(str(elem)))

    self.con.commit()
    self.con.close()

