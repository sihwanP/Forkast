import sys
import os

# Force usage of utf-8 for stdout checks
sys.stdout.reconfigure(encoding='utf-8')

path = r'c:\dev\Forkast\platform_ui\templates\platform_ui\index_v2.html'
print(f"Processing {path}")

# The new content to insert
spawn_code = """        function spawnFirefly(container) {
            const fly = document.createElement('div');
            fly.className = 'absolute rounded-full pointer-events-none';
            
            // Visuals: Tiny, Yellow-Green Glow
            const size = Math.random() * 3 + 2; // 2px - 5px
            fly.style.width = `${size}px`;
            fly.style.height = `${size}px`;
            fly.style.backgroundColor = '#ccff00'; // Neon Lime/Yellow
            fly.style.boxShadow = `0 0 ${size + 4}px #ccff00`;
            fly.style.opacity = '0'; // Start hidden

            // Position: Random Screen
            const startX = Math.random() * 100;
            const startY = Math.random() * 100;
            fly.style.left = `${startX}%`;
            fly.style.top = `${startY}%`;
            
            container.appendChild(fly);

            // 1. Blinking Animation (Respiration)
            fly.animate([
                { opacity: 0 },
                { opacity: 0.8, offset: 0.5 },
                { opacity: 0 }
            ], {
                duration: 2000 + Math.random() * 3000, 
                iterations: Infinity,
                direction: 'normal',
                easing: 'ease-in-out'
            });

            // 2. Floating Animation (Drift)
            const moveX = (Math.random() - 0.5) * 200; 
            const moveY = (Math.random() - 0.5) * 150; 

            const floatAnim = fly.animate([
                { transform: 'translate(0, 0)' },
                { transform: `translate(${moveX}px, ${moveY}px)` }
            ], {
                duration: 10000 + Math.random() * 10000, // 10s-20s
                fill: 'forwards',
                easing: 'linear'
            });

            floatAnim.onfinish = () => fly.remove();
        }

"""

try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    
    # 0-indexed
    # Keep 0 to 1095 (Line 1 to 1096)
    head = lines[:1096]
    
    # Keep 1176 to end (Line 1177 to end)
    tail = lines[1176:]
    
    # Verify split point consistency if possible (optional but good for debugging)
    print(f"Head last line: {head[-1].strip()}")
    print(f"Tail first line: {tail[0].strip()}")
    
    if 'function playLocalAudio' not in tail[0]:
        print("WARNING: Tail start mismatch. Updating index...")
        # Search for it in the whole file to be safe
        found_idx = -1
        for i, line in enumerate(lines):
            if 'function playLocalAudio' in line:
                found_idx = i
                break
        if found_idx != -1:
            print(f"Found playLocalAudio at {found_idx}")
            tail = lines[found_idx:]
        else:
            print("ERROR: Could not find playLocalAudio")
            sys.exit(1)
            
    new_lines = head + [spawn_code] + tail
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Success: File spliced")

except Exception as e:
    print(f"Error: {e}")
