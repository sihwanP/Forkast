import sqlite3
import datetime

try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    print("--- Checking Member Table ---")
    try:
        cursor.execute("SELECT * FROM platform_ui_member LIMIT 1")
        print("✅ Table 'platform_ui_member' already exists.")
    except sqlite3.OperationalError:
        print("⚠️ Table 'platform_ui_member' missing. Creating it now...")
        
        # Create Table
        cursor.execute("""
            CREATE TABLE platform_ui_member (
                id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                name varchar(100) NOT NULL,
                master_key varchar(50) NOT NULL UNIQUE,
                created_at datetime NOT NULL
            )
        """)
        print("✅ Created 'platform_ui_member' table.")
        
        # Optional: Add a default test member
        try:
             cursor.execute("""
                INSERT INTO platform_ui_member (name, master_key, created_at)
                VALUES ('Test Branch', '123456', ?)
            """, (datetime.datetime.now(),))
             print("✅ Added default member: Test Branch (Key: 123456)")
        except Exception as insert_err:
             print(f"ℹ️ Could not insert default member (might exist): {insert_err}")

    conn.commit()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
