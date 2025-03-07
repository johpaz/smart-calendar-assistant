import sqlite3
conn = sqlite3.connect("agenda.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM eventos")
print(cursor.fetchall())
conn.close()