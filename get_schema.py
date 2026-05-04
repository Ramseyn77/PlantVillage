import sqlite3

c = sqlite3.connect('phyto_diag.db')
for row in c.execute("SELECT sql FROM sqlite_master WHERE type='table'"):
    if row[0]:
        print(row[0])
