import sys

path = r'c:\dev\Forkast\platform_ui\templates\platform_ui\index_v2.html'
try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Target: Line 1112 (index 1111) is '} /*'
    # Target: Line 1151 (index 1150) is '        }'
    # Goal: Replace 1112 with '        }\n' and delete 1113-1151.
    
    # Check safety
    if 'launchFirework' not in lines[1093]: # Just a sanity check nearby
        print("Sanity check failed at 1094")
        # sys.exit(1) # Don't exit, file might have shifted slightly, but indices from view_file should be trusted relative to the view.
    
    if '} /*' not in lines[1111]:
        print(f"Index mismatch at 1112: {lines[1111]}")
        sys.exit(1)
        
    print(f"Replacing line 1112: {lines[1111].strip()}")
    print(f"Deleting lines 1113-1151")
    
    lines[1111] = '        }\n'
    # Delete indices 1112 to 1151 (1151 exclusive? No 1151 line number is index 1150).
    # We want to delete lines 1113 (index 1112) to 1151 (index 1150).
    # So slice is [1112 : 1151]. unique elements: 1112, ..., 1150. Count = 39.
    
    del lines[1112:1151] 
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Success")
except Exception as e:
    print(e)
