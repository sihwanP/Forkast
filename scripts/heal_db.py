import os
import django
from django.db import connection
from django.utils import timezone
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

def run_sql(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)

print("🚑 Starting DB Healing...")

# 1. DailySales
print("Fixing DailySales...")
run_sql("DROP TABLE IF EXISTS platform_ui_dailysales")
run_sql("""
    CREATE TABLE platform_ui_dailysales (
        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        date date NOT NULL UNIQUE,
        revenue decimal NOT NULL,
        predicted_revenue decimal NOT NULL,
        weather_impact varchar(100) NOT NULL,
        event_impact varchar(100) NOT NULL
    )
""")
# Insert Dummy
today = timezone.now().date().isoformat()
run_sql(f"INSERT INTO platform_ui_dailysales (date, revenue, predicted_revenue, weather_impact, event_impact) VALUES ('{today}', 1200000, 1500000, 'Rainy', 'None')")

# 2. Inventory
print("Fixing Inventory...")
run_sql("DROP TABLE IF EXISTS platform_ui_inventory")
run_sql("""
    CREATE TABLE platform_ui_inventory (
        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        item_name varchar(100) NOT NULL,
        current_stock integer NOT NULL,
        optimal_stock integer NOT NULL,
        status varchar(50) NOT NULL
    )
""")
run_sql("INSERT INTO platform_ui_inventory (item_name, current_stock, optimal_stock, status) VALUES ('Coffee Beans', 50, 100, 'LOW')")
run_sql("INSERT INTO platform_ui_inventory (item_name, current_stock, optimal_stock, status) VALUES ('Milk', 200, 150, 'GOOD')")
run_sql("INSERT INTO platform_ui_inventory (item_name, current_stock, optimal_stock, status) VALUES ('Syrup', 10, 20, 'LOW')")

# 3. Weather
print("Fixing Weather...")
run_sql("DROP TABLE IF EXISTS platform_ui_weather")
run_sql("""
    CREATE TABLE platform_ui_weather (
        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        date date NOT NULL,
        condition varchar(50) NOT NULL,
        temperature real NOT NULL
    )
""")
run_sql(f"INSERT INTO platform_ui_weather (date, condition, temperature) VALUES ('{today}', 'Sunny', 25.5)")

# 4. LocalEvent
print("Fixing LocalEvent...")
run_sql("DROP TABLE IF EXISTS platform_ui_localevent")
run_sql("""
    CREATE TABLE platform_ui_localevent (
        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        name varchar(200) NOT NULL,
        date date NOT NULL,
        impact_level varchar(50) NOT NULL
    )
""")
run_sql(f"INSERT INTO platform_ui_localevent (name, date, impact_level) VALUES ('Local Festival', '{today}', 'High')")

# 5. OwnerSentiment
print("Fixing OwnerSentiment...")
run_sql("DROP TABLE IF EXISTS platform_ui_ownersentiment")
run_sql("""
    CREATE TABLE platform_ui_ownersentiment (
        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        date date NOT NULL,
        mood_score integer NOT NULL,
        cheer_message text NOT NULL
    )
""")
run_sql(f"INSERT INTO platform_ui_ownersentiment (date, mood_score, cheer_message) VALUES ('{today}', 8, 'You are doing great!')")

# 6. CommunityPost
print("Fixing CommunityPost...")
run_sql("DROP TABLE IF EXISTS platform_ui_communitypost")
run_sql("""
    CREATE TABLE platform_ui_communitypost (
        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        author varchar(100) NOT NULL,
        content text NOT NULL,
        created_at datetime NOT NULL
    )
""")
run_sql("INSERT INTO platform_ui_communitypost (author, content, created_at) VALUES ('Admin', 'Welcome to Forkast Community!', datetime('now'))")

print("✅ DB Healing Complete. All tables reset and populated.")
