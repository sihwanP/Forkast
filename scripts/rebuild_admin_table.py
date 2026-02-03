import sqlite3

try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    print("--- 1. Dropping AdminConfig Table ---")
    cursor.execute("DROP TABLE IF EXISTS platform_ui_adminconfig")
    print("Dropped.")
    
    print("--- 2. Creating AdminConfig Table (Fresh) ---")
    # Manually creating table with BOTH key and master_key
    cursor.execute("""
        CREATE TABLE platform_ui_adminconfig (
            id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            key varchar(50) NOT NULL,
            master_key varchar(50), 
            updated_at datetime NOT NULL
        )
    """)
    print("Created.")
    
    print("--- 3. Inserting Default Values ---")
    cursor.execute("""
        INSERT INTO platform_ui_adminconfig (key, master_key, updated_at)
        VALUES ('admin', 'master', date('now'))
    """)
    print("Inserted defaults.")
    
    conn.commit()
    print("\n✅ SUCCESS: Table rebuilt with master_key.")
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
