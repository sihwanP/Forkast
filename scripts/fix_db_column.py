import sqlite3

try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    print("--- Attempting to add column 'master_key' ---")
    try:
        # Check if column exists first to avoid error
        cursor.execute("SELECT master_key FROM platform_ui_adminconfig LIMIT 1")
        print("Column already exists.")
    except sqlite3.OperationalError:
        # Column doesn't exist, so add it
        print("Column missing. Adding it now...")
        cursor.execute("ALTER TABLE platform_ui_adminconfig ADD COLUMN master_key varchar(50) DEFAULT 'master'")
        conn.commit()
        print("✅ SUCCESS: Added 'master_key' column.")
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
