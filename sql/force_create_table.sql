-- Force creation of the missing table
CREATE TABLE IF NOT EXISTS "platform_ui_order" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "quantity" integer NOT NULL,
    "status" varchar(20) NOT NULL,
    "created_at" datetime NOT NULL,
    "item_id" integer NOT NULL REFERENCES "platform_ui_inventory" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "platform_ui_order_item_id_idx" ON "platform_ui_order" ("item_id");

-- Fake the migration so Django doesn't try again
INSERT OR IGNORE INTO django_migrations (app, name, applied) 
VALUES ('platform_ui', '0005_order', datetime('now'));
