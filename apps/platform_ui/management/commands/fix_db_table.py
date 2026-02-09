from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix missing order table directly via Django connection'

    def handle(self, *args, **options):
        self.stdout.write("Checking database table status...")
        
        table_name = "platform_ui_order"
        
        with connection.cursor() as cursor:
            # 1. Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=%s", [table_name])
            row = cursor.fetchone()
            
            if row:
                self.stdout.write(self.style.SUCCESS(f"✅ Table '{table_name}' ALREADY EXISTS."))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Table '{table_name}' MISSING. Creating now..."))
                
                # 2. Force Create
                sql = """
                CREATE TABLE "platform_ui_order" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "quantity" integer NOT NULL,
                    "status" varchar(20) NOT NULL,
                    "created_at" datetime NOT NULL,
                    "item_id" integer NOT NULL REFERENCES "platform_ui_inventory" ("id") DEFERRABLE INITIALLY DEFERRED
                );
                """
                cursor.execute(sql)
                
                # Index
                cursor.execute('CREATE INDEX "platform_ui_order_item_id_idx" ON "platform_ui_order" ("item_id");')
                
                self.stdout.write(self.style.SUCCESS(f"✅ Executed CREATE TABLE for '{table_name}'."))
                
            # 3. Final Verification
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=%s", [table_name])
            final_row = cursor.fetchone()
            
            if final_row:
                self.stdout.write(self.style.SUCCESS(f"🎉 FINAL CONFIRMATION: {final_row[0]} exists."))
                
                # Verify columns
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                self.stdout.write(f"   Columns: {columns}")
            else:
                self.stdout.write(self.style.ERROR("❌ FAILED: Table still missing after creation attempt."))
