import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
path = r'c:\dev\Forkast\platform_ui\templates\platform_ui\index_v2.html'
new_path = r'c:\dev\Forkast\platform_ui\templates\platform_ui\index_v3.html'

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
    
    # Slice exactly as planned (0-1095, 1176-end)
    # But check indices again dynamically to be safe
    start_cut = -1
    end_cut = -1
    
    for i, line in enumerate(lines):
        if 'function startFireworks()' in line:
            # We want to keep startFireworks but cut AFTER it ends?
            # No, startFireworks ends at 1095.
            pass
        if 'function launchFirework' in line:
            start_cut = i
        if 'function playLocalAudio' in line:
            end_cut = i
            break
            
    if start_cut != -1 and end_cut != -1:
        print(f"Cutting from {start_cut} to {end_cut}")
        new_lines = lines[:start_cut] + [spawn_code] + lines[end_cut:]
        
        with open(new_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Created {new_path}")
    else:
        print("Markers not found")

except Exception as e:
    print(f"Error: {e}")
