import sqlite3
import datetime
import os

# Ensuring we use the exact file Django uses
db_path = os.path.join(os.getcwd(), 'db.sqlite3')
print(f"Target DB: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- 1. DROPPING Table ---")
    cursor.execute("DROP TABLE IF EXISTS platform_ui_member")
    
    print("--- 2. CREATING Table ---")
    cursor.execute("""
        CREATE TABLE platform_ui_member (
            id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            name varchar(100) NOT NULL,
            master_key varchar(50) NOT NULL UNIQUE,
            created_at datetime NOT NULL
        )
    """)
    
    print("--- 3. INSERTING Data ---")
    now = datetime.datetime.now()
    cursor.execute("INSERT INTO platform_ui_member (name, master_key, created_at) VALUES (?, ?, ?)", 
                   ('Gangnam Store', '111111', now))
    cursor.execute("INSERT INTO platform_ui_member (name, master_key, created_at) VALUES (?, ?, ?)", 
                   ('Hongdae Store', '222222', now))
                   
    conn.commit()
    
    print("--- 4. VERIFYING Data ---")
    cursor.execute("SELECT * FROM platform_ui_member")
    rows = cursor.fetchall()
    for row in rows:
        print(f"   Row: {row}")
        
    print("\n✅ SUCCESS: Table rebuilt and populated.")
    conn.close()
    
except Exception as e:
    print(f"❌ FATAL ERROR: {e}")
