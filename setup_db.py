import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# 🔴 NEW TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    faculty TEXT,
    status TEXT,
    date TEXT
)
""")

conn.commit()
conn.close()

print("Attendance Session Table Ready ✅")