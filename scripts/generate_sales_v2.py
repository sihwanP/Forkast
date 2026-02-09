import csv
import random
import os
from datetime import date, timedelta
from django.utils import timezone
import sys
from pathlib import Path

# Setup Django (Optional/Encoding safe)
import django

# Configuration
ITEMS = [
    ("후라이드 치킨", 18000),
    ("양념 치킨", 19000),
    ("반반 치킨", 19000),
    ("간장 치킨", 19000),
    ("마늘 치킨", 20000),
    ("순살 치킨", 18000),
    ("치즈볼", 5000),
    ("감자튀김", 6000),
    ("생맥주 500cc", 4500),
    ("콜라 1.25L", 2500),
    ("소주", 5000)
]

def generate_daily_sales(sales_date):
    rows = []
    # Weekday logic: Fri/Sat/Sun busy
    is_weekend = sales_date.weekday() >= 4 # 4=Fri, 5=Sat, 6=Sun
    
    if is_weekend:
        num_orders = random.randint(30, 60)
    else:
        num_orders = random.randint(15, 35)
    
    for _ in range(num_orders):
        item_name, price = random.choice(ITEMS)
        
        # Time distribution
        hour = random.choices(
            [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0],
            weights=[1, 1, 1, 2, 4, 10, 15, 20, 15, 10, 8, 4, 1]
        )[0]
        mins = random.choice([0, 10, 20, 30, 40, 50])
        time_str = f"{hour:02d}:{mins:02d}"
        
        qty = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
        
        rows.append([sales_date, item_name, time_str, price, qty])
        
    return rows

def generate_period_csv(start_date, end_date, output_dir, filename_prefix):
    os.makedirs(output_dir, exist_ok=True)
    
    all_rows = []
    curr = start_date
    while curr <= end_date:
        # Occasionally skip a day (closed) - e.g. Mondays
        if curr.weekday() == 0 and random.random() < 0.8: # Close 80% of Mondays
            curr += timedelta(days=1)
            continue
            
        daily_rows = generate_daily_sales(curr)
        all_rows.extend(daily_rows)
        curr += timedelta(days=1)
        
    output_path = os.path.join(output_dir, f"{filename_prefix}.csv")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Order Date", "Item Name", "Time", "Price", "Quantity"])
        writer.writerows(all_rows)
        
    print(f"Generated {len(all_rows)} rows in {output_path}")

def main():
    # 1. Past Sales: 2024-01-01 ~ 2025-12-31
    past_start = date(2024, 1, 1)
    past_end = date(2025, 12, 31)
    generate_period_csv(past_start, past_end, 'sales_data/past', 'sales_history_2024_2025')
    
    # 2. Current Sales: 2026-01-01 ~ Today (2026-02-04)
    # Using hardcoded today based on context or reliable source if needed, 
    # but strictly user asked for "Today"
    current_start = date(2026, 1, 1)
    today = date(2026, 2, 4) # Fixed to User Context Time
    
    generate_period_csv(current_start, today, 'sales_data/current', 'sales_current_2026')

if __name__ == "__main__":
    main()
