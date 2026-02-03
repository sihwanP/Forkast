import sqlite3
import os

DB_PATH = r"C:\dev\Forkast\db.sqlite3"

def fix():
    print(f"Connecting to {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("❌ DB File missing!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create Table
    sql_create = """
    CREATE TABLE IF NOT EXISTS "platform_ui_order" (
        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        "quantity" integer NOT NULL,
        "status" varchar(20) NOT NULL,
        "created_at" datetime NOT NULL,
        "item_id" integer NOT NULL REFERENCES "platform_ui_inventory" ("id") DEFERRABLE INITIALLY DEFERRED
    );
    """
    try:
        cursor.execute(sql_create)
        print("✅ Executed CREATE TABLE.")
    except Exception as e:
        print(f"❌ Create Table Error: {e}")

    # 2. Create Index
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS "platform_ui_order_item_id_idx" ON "platform_ui_order" ("item_id");')
        print("✅ Executed CREATE INDEX.")
    except Exception as e:
        print(f"❌ Create Index Error: {e}")

    # 3. Fake Migration
    try:
        cursor.execute("INSERT OR IGNORE INTO django_migrations (app, name, applied) VALUES ('platform_ui', '0005_order', datetime('now'));")
        print("✅ Executed FAKE MIGRATION.")
    except Exception as e:
        print(f"❌ Migration Insert Error: {e}")

    conn.commit()

    # 4. Verify
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='platform_ui_order'")
    row = cursor.fetchone()
    if row:
        print(f"🎉 SUCCESS: Table '{row[0]}' now exists.")
    else:
        print("😱 FAILURE: Table still missing.")

    conn.close()

if __name__ == "__main__":
    fix()
