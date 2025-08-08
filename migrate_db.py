import sqlite3

db_path = "data/jobs.db"  # Adjust path if needed
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    
    cursor.execute("ALTER TABLE job_applications ADD COLUMN location TEXT")  # ✅ Add this line
    print("✅ Columns added successfully.")
except sqlite3.OperationalError as e:
    print(f"⚠️ Already exists or error: {e}")

conn.commit()
conn.close()
