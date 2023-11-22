import requests as r
import sqlite3

res = r.get('http://cdn.dota2.com/apps/dota2/images/items/blink_lg.png')
print(res)

con = sqlite3.connect('dotastats.sqlite3')
cur = con.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS heroes (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL,
localized_name TEXT NOT NULL,
primary_attr TEXT NOT NULL,
attack_type TEXT NOT NULL,
roles TEXT NOT NULL,
legs INTEGER
)
''')

for i in res.json():
    cur.execute('INSERT INTO heroes (id, name, localized_name, primary_attr, attack_type, roles, legs)'
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (i['id'], i['name'], i['localized_name'], i['primary_attr'],
                 i['attack_type'], ', '.join(i['roles']), i['legs']))

cur.execute('''
CREATE TABLE IF NOT EXISTS rank (
id INTEGER PRIMARY KEY,
icon BLOB
)
''')

for i in range(0, 8):
    img = open(f'rank/rank_star_{i}.png', mode='rb')
    byt = img.read()
    cur.execute('INSERT INTO rank (id, icon) VALUES (?, ?)', (i, byt))
    img.close()

for i in range(0, 8):
    img = open(f'rank/rank_icon_{i}.png', mode='rb')
    byt = img.read()
    if not i:
        cur.execute('INSERT INTO rank (id, icon) VALUES (?, ?)', (100, byt))
    else:
        cur.execute('INSERT INTO rank (id, icon) VALUES (?, ?)', (i * 10, byt))
    img.close()

# Кусок кода отвечающий за таблицу heroesAvatar куда-то потерялся

con.commit()
con.close()
