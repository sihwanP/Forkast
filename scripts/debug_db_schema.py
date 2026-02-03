import sqlite3

try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    print("--- Table Info: platform_ui_adminconfig ---")
    cursor.execute("PRAGMA table_info(platform_ui_adminconfig)")
    columns = cursor.fetchall()
    
    found_master = False
    for col in columns:
        print(f"Column: {col[1]} (Type: {col[2]})")
        if col[1] == 'master_key':
            found_master = True
            
    if found_master:
        print("\n✅ SUCCESS: 'master_key' column exists.")
    else:
        print("\n❌ FAILURE: 'master_key' column is MISSING.")
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
