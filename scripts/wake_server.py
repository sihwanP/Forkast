#!/usr/bin/env python3
"""
Forkast Wake Server
- 맥북에서 항상 백그라운드로 실행
- 핸드폰에서 요청 시 런처 시작 (브라우저 없이 터미널만)
"""
import http.server
import subprocess
import os
import socket

WAKE_PORT = 9998
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

class WakeHandler(http.server.BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        path_only = self.path.split('?')[0]
        if path_only == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(self.get_html().encode('utf-8'))
        elif path_only == '/wake':
            self.wake_launcher()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"status": "launched"}')
        elif path_only == '/stop_launcher':
            self.stop_launcher()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"status": "stopped"}')
        elif path_only == '/status':
            # 런처가 실행 중인지 확인
            result = subprocess.run(["lsof", "-i", ":9999"], capture_output=True)
            running = result.returncode == 0
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            import json
            self.wfile.write(json.dumps({"launcher_running": running}).encode())
        else:
            self.send_error(404)
    
    def wake_launcher(self):
        """터미널에서 런처 시작 (브라우저 없이)"""
        # 이미 실행 중인지 확인
        result = subprocess.run(["lsof", "-i", ":9999"], capture_output=True)
        if result.returncode == 0:
            return
        
        launcher_script = os.path.join(PROJECT_ROOT, "scripts", "web_launcher.py")
        venv_python = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")
        
        # .venv가 있으면 사용, 없으면 시스템 python3
        if os.path.isfile(venv_python):
            python_cmd = venv_python
        else:
            python_cmd = "python3"
        
        applescript = f'''
        tell application "Terminal"
            activate
            do script "export PATH=/usr/local/bin:/opt/homebrew/bin:$PATH && cd {PROJECT_ROOT} && {python_cmd} {launcher_script} --no-browser"
        end tell
        '''
        subprocess.run(["osascript", "-e", applescript])

    def stop_launcher(self):
        """런처 및 터미널 종료 (확인창 자동 클릭 포함)"""
        # 1. 프로세스 정리
        subprocess.run(["pkill", "-9", "-f", "web_launcher.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-9", "-f", "runserver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-9", "-f", "DBeaver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-9", "-f", "dbeaver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 2. 터미널 창 폐쇄 및 팝업 자동 클릭
        # 'System Events'를 사용하여 '종료' 버튼을 자동으로 누릅니다.
        applescript = '''
        tell application "Terminal"
            set winList to every window whose name contains "Forkast" or name contains "web_launcher"
            repeat with win in winList
                try
                    close win saving no
                end try
            end repeat
        end tell

        -- 팝업창이 뜨면 '종료' 버튼 클릭 (1초 대기 후 시도)
        delay 1
        tell application "System Events"
            tell process "Terminal"
                set confirmWindow to (every window whose description contains "이 윈도우에서 실행 중인 프로세스를 종료")
                repeat with win in confirmWindow
                    if exists button "종료" of win then
                        click button "종료" of win
                    end if
                end repeat
            end tell
        end tell
        '''
        subprocess.Popen(["osascript", "-e", applescript], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    def log_message(self, format, *args):
        pass

    def get_html(self):
        local_ip = get_local_ip()
        return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>Forkast Wake Station</title>
    <style>
        * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        body {{ 
            background: #0f172a; color: #f8fafc; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            display: flex; flex-direction: column;
            align-items: center; justify-content: center; 
            min-height: 100vh; margin: 0;
            padding: env(safe-area-inset-top) 20px env(safe-area-inset-bottom) 20px;
        }}
        .container {{ 
            background: #1e293b; padding: 40px 30px; 
            border-radius: 30px; text-align: center;
            width: 100%; max-width: 400px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        h1 {{ 
            margin: 0 0 10px 0; font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(to right, #fbbf24, #f59e0b); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        }}
        .subtitle {{ color: #94a3b8; margin-bottom: 35px; font-size: 1rem; font-weight: 500; }}
        .status {{ 
            padding: 18px; border-radius: 16px; margin-bottom: 30px;
            background: rgba(0,0,0,0.3); font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        .status.running {{ border-left: 5px solid #10b981; color: #10b981; }}
        .status.stopped {{ border-left: 5px solid #ef4444; color: #ef4444; }}
        
        .btn {{
            width: 100%; padding: 20px; border: none; border-radius: 18px;
            font-size: 1.15rem; font-weight: 700; cursor: pointer;
            color: white; margin-bottom: 18px;
            transition: all 0.2s ease;
            display: flex; align-items: center; justify-content: center; gap: 10px;
        }}
        .btn:active {{ transform: scale(0.96); opacity: 0.9; }}
        
        .btn-start {{ background: linear-gradient(135deg, #fbbf24, #f59e0b); box-shadow: 0 10px 15px -3px rgba(245, 158, 11, 0.3); }}
        .btn-stop {{ background: linear-gradient(135deg, #475569, #334155); box-shadow: 0 10px 15px -3px rgba(51, 65, 85, 0.3); }}
        .btn-secondary {{ 
            background: #1e293b; color: #e2e8f0; border: 1px solid rgba(255, 255, 255, 0.1); 
            margin-top: 10px;
        }}
        
        .info {{ margin-top: 30px; font-size: 0.85rem; color: #64748b; line-height: 1.5; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Wake Station</h1>
        <p class="subtitle">맥북 런처 가동 스테이션</p>
        
        <div id="status" class="status stopped">상태 확인 중...</div>
        
        <button id="btn-wake" class="btn btn-start" onclick="wakeLauncher()">
            <span>⚡</span> 런처 가동
        </button>
        
        <button id="btn-stop" class="btn btn-stop" onclick="stopLauncher()">
            <span>⏹️</span> 런처 정지
        </button>
        
        <button class="btn btn-secondary" onclick="goToLauncher()">
            <span>📱</span> Remote Control 열기
        </button>
        
        <div class="info">
            <b>Forkast 가동 센터</b><br>
            여기서 런처를 가동한 후 Remote Control로 이동하세요.
        </div>
    </div>

    <script>
        async function checkStatus() {{
            try {{
                const res = await fetch('/status');
                const data = await res.json();
                const statusEl = document.getElementById('status');
                const btnWake = document.getElementById('btn-wake');
                const btnStop = document.getElementById('btn-stop');
                
                if (data.launcher_running) {{
                    statusEl.className = 'status running';
                    statusEl.innerHTML = '✅ 런처 실행 중';
                    btnWake.style.opacity = '0.5';
                    btnWake.disabled = true;
                    btnStop.disabled = false;
                    btnStop.style.opacity = '1';
                }} else {{
                    statusEl.className = 'status stopped';
                    statusEl.innerHTML = '⏹️ 런처 정지됨';
                    btnWake.style.opacity = '1';
                    btnWake.disabled = false;
                    btnStop.disabled = true;
                    btnStop.style.opacity = '0.5';
                }}
            }} catch(e) {{
                document.getElementById('status').innerHTML = '❌ 연결 오류';
            }}
        }}

        async function wakeLauncher() {{
            const statusEl = document.getElementById('status');
            statusEl.innerHTML = '⏳ 시작 요청 중...';
            try {{
                await fetch('/wake');
                setTimeout(checkStatus, 2000);
            }} catch(e) {{
                alert('시작 실패: ' + e);
                checkStatus();
            }}
        }}

        async function stopLauncher() {{
            if(!confirm('런처와 모든 서비스를 종료하시겠습니까?')) return;
            const statusEl = document.getElementById('status');
            statusEl.innerHTML = '⏳ 종료 요청 중...';
            try {{
                await fetch('/stop_launcher');
                setTimeout(checkStatus, 2000);
            }} catch(e) {{
                alert('종료 실패: ' + e);
                checkStatus();
            }}
        }}

        async function goToLauncher() {{
            const targetUrl = 'http://' + window.location.hostname + ':9999?t=' + new Date().getTime();
            const statusEl = document.getElementById('status');
            
            // 먼저 9999가 살아있는지 확인
            try {{
                const check = await fetch(targetUrl.split('?')[0] + '/status', {{ signal: AbortSignal.timeout(2000) }});
                if (check.ok) {{
                    window.location.href = targetUrl;
                    return;
                }}
            }} catch(e) {{
                // 9999가 꺼져있으면 wake 먼저
            }}
            
            statusEl.className = 'status stopped';
            statusEl.innerHTML = '⏳ 런처를 가동 중입니다...';
            
            try {{
                await fetch('/wake');
                // 런처가 뜰 때까지 대기 후 이동 (최대 8초)
                let tries = 0;
                const waitAndGo = setInterval(async () => {{
                    tries++;
                    try {{
                        const res = await fetch(targetUrl.split('?')[0] + '/status', {{ signal: AbortSignal.timeout(1500) }});
                        if (res.ok) {{
                            clearInterval(waitAndGo);
                            window.location.href = targetUrl;
                        }}
                    }} catch(e) {{}}
                    if (tries > 8) {{
                        clearInterval(waitAndGo);
                        statusEl.innerHTML = '⚠️ 런처 연결 실패. 다시 시도해 주세요.';
                        setTimeout(checkStatus, 2000);
                    }}
                }}, 1000);
            }} catch(e) {{
                statusEl.innerHTML = '❌ Wake 실패';
                setTimeout(checkStatus, 2000);
            }}
        }}

        checkStatus();
        setInterval(checkStatus, 3000);
    </script>
</body>
</html>
        """

def run():
    local_ip = get_local_ip()
    server = http.server.HTTPServer(('0.0.0.0', WAKE_PORT), WakeHandler)
    print(f"")
    print(f"========================================")
    print(f"  Forkast Wake Station Started!")
    print(f"========================================")
    print(f"  📱 Phone Access: http://{local_ip}:{WAKE_PORT}")
    print(f"========================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()
