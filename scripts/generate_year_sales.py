import csv
import random
from datetime import date, timedelta
import calendar

# Configuration
YEAR = 2025
OUTPUT_FILE = 'sales_data/past/chicken_sales_2025.csv'

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
    # Simple logic: evening peak
    # Random number of orders: 10 to 40
    num_orders = random.randint(10, 40)
    
    for _ in range(num_orders):
        # Pick Item
        item_name, price = random.choice(ITEMS)
        
        # Pick Time (12:00 - 00:00) weighted towards evening
        hour = random.choices(
            [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0],
            weights=[1, 1, 1, 1, 2, 4, 8, 10, 10, 8, 6, 4, 2]
        )[0]
        
        mins = random.choice([0, 15, 30, 45])
        time_str = f"{hour:02d}:{mins:02d}"
        
        qty = random.choices([1, 2, 3, 4, 5], weights=[60, 20, 10, 5, 5])[0]
        
        rows.append([sales_date, item_name, time_str, price, qty])
        
    return rows

def main():
    start_date = date(YEAR, 1, 1)
    end_date = date(YEAR, 12, 31)
    
    all_data = []
    
    # Iterate by week
    current_date = start_date
    while current_date <= end_date:
        # Determine the week range (Mon-Sun or partial week at year boundaries)
        # Actually easier to iterate days and keep track of "days off in current week"
        # But user said "randomly exclude 2 days per week"
        
        # We can pre-calculate off-days for each iso-week
        pass
        # Let's simple iterate year, split into weeks.
        
        # Logic: Get ISO calendar week
        year_num, week_num, weekday = current_date.isocalendar()
        
        # For this week, decide which 2 days are off (0=Mon, 6=Sun)
        # We need to do this decision once per week.
        # So we can group dates by week_num first?
        # Simpler: Iterate days, group by week, then filter?
        # Let's generate ALL dates first, then group by week.
        
        current_date += timedelta(days=1)
        
    # Re-loop with cleaner logic
    dates_by_week = {}
    curr = start_date
    while curr <= end_date:
        y, w, d = curr.isocalendar()
        key = (y, w)
        if key not in dates_by_week:
            dates_by_week[key] = []
        dates_by_week[key].append(curr)
        curr += timedelta(days=1)
        
    final_rows = []
    
    for key, week_dates in dates_by_week.items():
        # User wants 2 days excluded PER WEEK
        # If week is short (start/end of year), scale down? Or just random.
        # Assuming standard week logic.
        
        days_in_week = len(week_dates)
        if days_in_week <= 2:
            # Comparison week too short, keep all or drop 1?
            # Let's keep all.
            days_to_work = week_dates
        else:
            # Randomly sample (N-2) working days
            # e.g. 7 days -> sample 5
            num_work = days_in_week - 2
            days_to_work = sorted(random.sample(week_dates, num_work))
            
        for d in days_to_work:
            daily = generate_daily_sales(d)
            final_rows.extend(daily)
            
    # Write CSV
    # Create directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Order Date", "Item Name", "Time", "Price", "Quantity"])
        writer.writerows(final_rows)
        
    print(f"Generated {len(final_rows)} rows of sales data for {YEAR} in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
