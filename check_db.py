import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("SELECT id, name, uid FROM students")
data = cursor.fetchall()

print("Students Data:", data)

conn.close()