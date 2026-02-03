import os
import datetime

db_path = r"c:\dev\Forkast\db.sqlite3"

if os.path.exists(db_path):
    stat = os.stat(db_path)
    print(f"File: {db_path}")
    print(f"Size: {stat.st_size} bytes")
    print(f"Modified: {datetime.datetime.fromtimestamp(stat.st_mtime)}")
    
    # Check absolute path
    abs_path = os.path.abspath(db_path)
    print(f"Abs Path: {abs_path}")
else:
    print("File not found via python os.path")
