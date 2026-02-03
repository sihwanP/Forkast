import sqlite3
import os

db_path = r"c:\dev\Forkast\db.sqlite3"
print(f"Target DB: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='platform_ui_order';")
    if cursor.fetchone():
        print("✅ Table 'platform_ui_order' already exists.")
    else:
        print("⚠️ Table missing. Creating now...")
        
        # 2. Create Table
        cursor.execute("""
            CREATE TABLE "platform_ui_order" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "quantity" integer NOT NULL,
                "status" varchar(20) NOT NULL,
                "created_at" datetime NOT NULL,
                "item_id" integer NOT NULL REFERENCES "platform_ui_inventory" ("id") DEFERRABLE INITIALLY DEFERRED
            );
        """)
        
        # 3. Create Index
        cursor.execute("""
            CREATE INDEX "platform_ui_order_item_id_idx" ON "platform_ui_order" ("item_id");
        """)
        
        print("✅ Table 'platform_ui_order' created successfully via Raw SQL.")
        conn.commit()

    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
