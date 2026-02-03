import sqlite3
import os
import datetime

LOG_FILE = "c:/dev/Forkast/emergency.log"
DB_PATH = "c:/dev/Forkast/db.sqlite3"

def log(msg):
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(f"[{datetime.datetime.now()}] {msg}\n")
    print(msg)

def fix_db():
    log(f"Starting DB Fix. Target: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        log("❌ DB File NOT FOUND!")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Check for Table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='platform_ui_order';")
        if cursor.fetchone():
            log("✅ Table 'platform_ui_order' ALREADY EXISTS.")
        else:
            log("⚠️ Table 'platform_ui_order' MISSING. Attempting creation...")
            try:
                cursor.execute("""
                    CREATE TABLE "platform_ui_order" (
                        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        "quantity" integer NOT NULL,
                        "status" varchar(20) NOT NULL,
                        "created_at" datetime NOT NULL,
                        "item_id" integer NOT NULL REFERENCES "platform_ui_inventory" ("id") DEFERRABLE INITIALLY DEFERRED
                    );
                """)
                cursor.execute('CREATE INDEX "platform_ui_order_item_id_idx" ON "platform_ui_order" ("item_id");')
                conn.commit()
                log("✅ Table created successfully.")
            except Exception as e:
                log(f"❌ Failed to create table: {e}")
                
        # 2. Check for Migration Entry (Optional - just logging)
        try:
            cursor.execute("SELECT name FROM django_migrations WHERE app='platform_ui';")
            migrations = [row[0] for row in cursor.fetchall()]
            log(f"Current Migrations: {migrations}")
        except:
             log("Could not read migrations.")

        conn.close()
        
    except Exception as e:
        log(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    fix_db()
