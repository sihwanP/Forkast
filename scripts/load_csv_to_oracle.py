import os
import sys
import csv
import glob
from pathlib import Path
from datetime import datetime

# Setup Django Environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forkast_project.settings')

# Configure Oracle Driver Shim
try:
    import oracledb
    import sys
    oracledb.version = "8.3.0"
    
    # Django compatibility fix
    if not isinstance(getattr(oracledb, 'Binary', None), type):
        class Binary(bytes): pass
        oracledb.Binary = Binary
    
    if not isinstance(getattr(oracledb, 'Timestamp', None), type):
        import datetime as dt
        oracledb.Timestamp = dt.datetime

    attr_map = {
        'DATETIME': 'DB_TYPE_DATE',
        'STRING': 'DB_TYPE_VARCHAR',
        'NUMBER': 'DB_TYPE_NUMBER',
        'CURSOR': 'DB_TYPE_CURSOR',
        'FIXED_CHAR': 'DB_TYPE_CHAR',
        'FIXED_UNICODE': 'DB_TYPE_NCHAR',
        'UNICODE': 'DB_TYPE_NVARCHAR',
        'LONG_STRING': 'DB_TYPE_LONG',
        'LONG_UNICODE': 'DB_TYPE_LONG_NVARCHAR',
        'NCLOB': 'DB_TYPE_NCLOB',
        'CLOB': 'DB_TYPE_CLOB',
        'BLOB': 'DB_TYPE_BLOB',
        'BFILE': 'DB_TYPE_BFILE',
        'ROWID': 'DB_TYPE_ROWID',
    }
    for old, new in attr_map.items():
        if not hasattr(oracledb, old) and hasattr(oracledb, new):
            setattr(oracledb, old, getattr(oracledb, new))

    sys.modules["cx_Oracle"] = oracledb
except ImportError:
    print("oracledb not found. Please pip install oracledb")
    sys.exit(1)

import django
django.setup()

from platform_ui.models import DailySales

def parse_date(date_str):
    for fmt in ('%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d'):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None

def load_data():
    csv_files = glob.glob(str(BASE_DIR / 'sales_data' / '**' / '*.csv'), recursive=True)
    print(f"Found {len(csv_files)} CSV files.")

    total_inserted = 0
    
    for csv_file in csv_files:
        print(f"Processing {csv_file}...")
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except UnicodeDecodeError:
            with open(csv_file, 'r', encoding='cp949') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

    # Clear existing data for a fresh granular load
    print("Clearing existing DailySales data...")
    DailySales.objects.all().delete()

    for csv_file in csv_files:
        print(f"Processing {csv_file}...")
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except UnicodeDecodeError:
            with open(csv_file, 'r', encoding='cp949') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

        # Aggregate per (day, item)
        daily_data = {}

        for row in rows:
            keys = list(row.keys())
            # Simple heuristic column matching
            date_key = next((k for k in keys if 'Date' in k or '날짜' in k), None)
            item_key = next((k for k in keys if 'Item' in k or '상품' in k or 'Menu' in k), None)
            price_key = next((k for k in keys if 'Price' in k or '가격' in k), None)
            qty_key = next((k for k in keys if 'Quantity' in k or '수량' in k), None)
            
            # Fallback for known structure (Order Date, Item Name, Time, Price, Qty)
            if not date_key and len(keys) >= 5: date_key = keys[0]
            if not item_key and len(keys) >= 5: item_key = keys[1]
            if not price_key and len(keys) >= 5: price_key = keys[3]
            if not qty_key and len(keys) >= 5: qty_key = keys[4]

            if not (date_key and price_key and qty_key):
                continue
            
            raw_date = row[date_key]
            d_obj = parse_date(raw_date)
            if not d_obj: continue

            item_name = row[item_key].strip() if item_key else "General"
            
            try:
                price = int(float(str(row[price_key]).replace(',','').strip()))
                qty = int(float(str(row[qty_key]).replace(',','').strip()))
                revenue = price * qty
            except:
                continue

            key = (d_obj, item_name)
            if key not in daily_data:
                daily_data[key] = 0
            daily_data[key] += revenue

        # Insert into DB
        for (d, item), rev in daily_data.items():
            obj, created = DailySales.objects.update_or_create(
                date=d,
                item_name=item,
                defaults={
                    'revenue': rev,
                    'predicted_revenue': rev * 1.1 # Dummy prediction
                }
            )
            total_inserted += 1
    
    print(f"Successfully loaded/updated {total_inserted} daily records.")

if __name__ == '__main__':
    try:
        load_data()
    except Exception as e:
        print(f"Error: {e}")
