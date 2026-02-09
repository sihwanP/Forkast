$path = "c:\dev\Forkast\platform_ui\templates\platform_ui\index_v2.html"
$tempPath = "c:\dev\Forkast\platform_ui\templates\platform_ui\index_temp.html"
$spawnCode = @"
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

"@

# Get Head (First 1096 lines)
Get-Content -Path $path -TotalCount 1096 | Set-Content -Path $tempPath -Encoding UTF8

# Add Spawn Code
Add-Content -Path $tempPath -Value $spawnCode -Encoding UTF8

# Get Tail (Skip first 1176 lines)
# Calculating line count to support Select-Object -Skip
Get-Content -Path $path | Select-Object -Skip 1176 | Add-Content -Path $tempPath -Encoding UTF8

# Overwrite
Move-Item -Path $tempPath -Destination $path -Force

Write-Host "Success: File spliced with PowerShell"
