import sys
import os

path = r'c:\dev\Forkast\platform_ui\templates\platform_ui\index_v2.html'
print(f"Processing {path}")

new_code = """        // --- Firefly Logic (Healing Code) ---
        function startFireworks() { // Kept name for compatibility
            const container = document.getElementById('particles-container');
            container.innerHTML = ''; 

            // Initial population
            for(let i=0; i<15; i++) spawnFirefly(container);

            // Continuous spawning
            fireworkInterval = setInterval(() => {
                spawnFirefly(container);
            }, 600); // Gentle stream
        }

        function spawnFirefly(container) {
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
    
    start_idx = -1
    end_idx = -1
    
    # search for markers
    for i, line in enumerate(lines):
        if '// --- Fireworks Logic ---' in line:
            start_idx = i
        if 'function playLocalAudio()' in line:
            end_idx = i
            break
            
    if start_idx != -1 and end_idx != -1:
        print(f"Found block: {start_idx} to {end_idx}")
        # Replace the slice
        # We want to keep playLocalAudio line (end_idx), so slice up to end_idx
        # But we want to replace FROM start_idx (inclusive)
        
        # We need to construct the new list
        new_lines = lines[:start_idx] + [new_code] + lines[end_idx:]
        
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("Success")
    else:
        print(f"Markers not found. Start: {start_idx}, End: {end_idx}")
        sys.exit(1)

except Exception as e:
    print(e)
