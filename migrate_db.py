import sqlite3

db_path = "data/jobs.db"  # Adjust if needed
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE job_applications ADD COLUMN description TEXT")
    cursor.execute("ALTER TABLE job_applications ADD COLUMN cover_letter_path TEXT")
    cursor.execute("ALTER TABLE job_applications ADD COLUMN cv_path TEXT")
    print("✅ Columns added successfully.")
except sqlite3.OperationalError as e:
    print(f"⚠️ Already exists or error: {e}")

conn.commit()
conn.close()
