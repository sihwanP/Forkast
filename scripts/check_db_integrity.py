import sqlite3
import os

db_path = 'db.sqlite3'

if not os.path.exists(db_path):
    print("❌ db.sqlite3 files does not exist.")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(platform_ui_adminconfig)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"Columns in AdminConfig: {columns}")
    
    if 'master_key' in columns:
        print("✅ 'master_key' column FOUND.")
    else:
        print("❌ 'master_key' column MISSING.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
