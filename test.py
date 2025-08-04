import sqlite3

conn = sqlite3.connect("data/jobs.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(job_applications);")
for column in cursor.fetchall():
    print(column)

conn.close()
