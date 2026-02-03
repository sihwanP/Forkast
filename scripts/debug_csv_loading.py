import csv
import os

FILE_PATH = 'sales_data/chicken_sales_2025.csv'

def test_parsing():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return

    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            decoded_file = content.splitlines()
            reader = csv.DictReader(decoded_file)
            
            print(f"Headers: {reader.fieldnames}")
            
            hourly_revenue = {} 
            item_sales = {} 
            total_items = 0
            row_count = 0
            
            for row in reader:
                row_count += 1
                row_keys = list(row.keys())
                
                time_key = next((k for k in row_keys if "Time" in k or "시간" in k), None)
                price_key = next((k for k in row_keys if "Price" in k or "가격" in k), None)
                qty_key = next((k for k in row_keys if "Quantity" in k or "수량" in k), None)
                item_key = next((k for k in row_keys if "Item" in k or "상품" in k), None)
                
                if not (time_key and price_key and qty_key and item_key):
                    # Fallback logic check
                    if len(row_keys) >= 5:
                         time_key = row_keys[2]
                         price_key = row_keys[3]
                         qty_key = row_keys[4]
                         item_key = row_keys[1]
                    else:
                        print(f"Row {row_count} skipped: {row}")
                        continue

                try:
                    raw_time = row[time_key].strip()
                    item_name = row[item_key].strip()
                    
                    import re
                    clean_price = re.sub(r'[^\d.]', '', row[price_key])
                    clean_qty = re.sub(r'[^\d.]', '', row[qty_key])
                    
                    price = int(float(clean_price))
                    qty = int(float(clean_qty))
                    
                    revenue = price * qty
                    total_items += qty
                    
                    # Item Aggregation
                    if item_name not in item_sales:
                        item_sales[item_name] = {'qty': 0, 'revenue': 0}
                    item_sales[item_name]['qty'] += qty
                    item_sales[item_name]['revenue'] += revenue
                    
                except Exception as e:
                    print(f"Row {row_count} Error: {e}")
                    continue
            
            print(f"Success! Processed {row_count} rows.")
            print(f"Total Items: {total_items}")
            print(f"Unique Items: {list(item_sales.keys())}")
            
    except Exception as e:
        print(f"File Read Error: {e}")

if __name__ == "__main__":
    test_parsing()
