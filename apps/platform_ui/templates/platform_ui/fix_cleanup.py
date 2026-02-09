import sys
import os

path = r'c:\dev\Forkast\platform_ui\templates\platform_ui\index_v2.html'
print(f"Processing {path}")

try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 0-indexed
    # Line 1112 is index 1111
    target_idx = 1111
    
    # Check if we are looking at the right line
    if '/*' not in lines[target_idx]:
        print(f"Mismatch at {target_idx}: {lines[target_idx]}")
        # Search for it?
        for i, line in enumerate(lines):
            if '} /*' in line:
                print(f"Found target at index {i}")
                target_idx = i
                break
        else:
            print("Target not found")
            sys.exit(1)

    print(f"Replacing line {target_idx+1}")
    lines[target_idx] = '        }\n'
    
    # Check for the end of the zombie block (the next '}')
    # We expect it around 1150 (index 1149/1150?)
    # Line 1151 in view (index 1150) is '        }'
    end_idx = target_idx + 1
    found_end = False
    for i in range(target_idx + 1, len(lines)):
        if lines[i].strip() == '}' and lines[i+2].strip().startswith('function explode'):
            end_idx = i
            found_end = True
            break
            
    if found_end:
        print(f"Deleting from {target_idx+2} to {end_idx+1}")
        # Delete from target_idx+1 up to end_idx (inclusive of end_idx because that brace is the old closing brace which we don't need if we closed it at target_idx?)
        # Wait, if we closed `launchFirework` at `target_idx`, then the old `}` at `end_idx` is the closing brace of the *old* body. So we should delete it too.
        # Yes.
        del lines[target_idx+1 : end_idx+1]
        
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Success")
    else:
        print("Could not find end of block")
        sys.exit(1)

except Exception as e:
    print(e)
