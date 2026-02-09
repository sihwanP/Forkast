import http.server
import subprocess
import os
import sys
import json
import threading
import webbrowser
import socket
import time

PORT = 9999
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANAGE_PY = os.path.join(PROJECT_ROOT, "manage.py")

# Global Process Store
PROCS = {
    "server": None,
    "frontend": None,
    "db": None
}

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def is_port_open(port):
    try:
        result = subprocess.run(["nc", "-z", "localhost", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except:
        return False

class ReusableTCPServer(http.server.HTTPServer):
    allow_reuse_address = True

class ControlHandler(http.server.BaseHTTPRequestHandler):
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
        elif path_only == '/manifest.json':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(self.get_manifest().encode('utf-8'))
        elif path_only == '/status':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            
            # 프로세스 핸들 확인
            proc_running = PROCS["server"] is not None and PROCS["server"].poll() is None
            # 실제 포트 확인 (핸들을 잃었을 경우 대비)
            port_open = is_port_open(8000)
            
            db_port_open = is_port_open(1521)
            
            status = {
                "server": proc_running or port_open, 
                "server_ready": port_open,
                "db": db_port_open
            }
            self.wfile.write(json.dumps(status).encode('utf-8'))
        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length).decode('utf-8') if length > 0 else "{}"
        data = json.loads(body)
        action = data.get('action')
        target = data.get('target')
        params = data.get('params', {})

        try:
            if action == 'start':
                self.start_process(target, params)
            elif action == 'stop':
                self.stop_process(target)
            elif action == 'restart':
                self.restart_process(target, params)
            elif action == 'close_app':
                self.stop_process('server')
                self.stop_process('db')
                self.send_json({"status": "closing"})
                # 터미널 종료는 Wake Server가 처리하거나 사용자가 직접 종료
                def exit_now():
                    os._exit(0)
                threading.Timer(0.5, exit_now).start()
                return
            self.send_json({"status": "success"})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, 500)

    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def start_process(self, target, params=None):
        if target == "server":
            if PROCS["server"] and PROCS["server"].poll() is None: return
            
            # 1. Start Django Server
            print("Starting Django Server...")
            PROCS["server"] = subprocess.Popen(
                [sys.executable, MANAGE_PY, "runserver", "0.0.0.0:8000"],
                cwd=PROJECT_ROOT
            )
            
            # 2. Start Frontend (Vite) Server
            print("Starting Frontend (Vite)...")
            frontend_dir = os.path.join(PROJECT_ROOT, "forkast-web-ui")
            PROCS["frontend"] = subprocess.Popen(
                ["npm", "run", "dev", "--", "--host"],
                cwd=frontend_dir,
                stdout=subprocess.DEVNULL, # Suppress output to keep terminal clean-ish
                stderr=subprocess.DEVNULL
            )
            
            # 3. Open Browser Automatically (Smart Reuse)
            # User Request: Open localhost:8000/dashboard/
            dashboard_url = "http://localhost:8000/"
            print(f"Opening Browser at {dashboard_url}...")
            
            def open_browser():
                time.sleep(2)
                # Smart Open: Try to reuse existing tab in Chrome or Safari
                # 1. Google Chrome
                script_chrome = f'''
                tell application "Google Chrome"
                    if it is running then
                        repeat with w in windows
                            set i to 1
                            repeat with t in tabs of w
                                -- Check if tab looks like our Dashboard (localhost:8000)
                                if URL of t contains ":8000" then
                                    set active tab index of w to i
                                    set index of w to 1
                                    set URL of t to "{dashboard_url}"
                                    reload t
                                    activate
                                    return "Reused"
                                end if
                                set i to i + 1
                            end repeat
                        end repeat
                    end if
                    return "Not Found"
                end tell
                '''
                
                # 2. Safari
                script_safari = f'''
                tell application "Safari"
                    if it is running then
                        repeat with w in windows
                            repeat with t in tabs of w
                                if URL of t contains ":8000" then
                                    set current tab of w to t
                                    set index of w to 1
                                    set URL of t to "{dashboard_url}"
                                    activate
                                    return "Reused"
                                end if
                            end repeat
                        end repeat
                    end if
                    return "Not Found"
                end tell
                '''
                
                try:
                    # Try Chrome first
                    result = subprocess.run(["osascript", "-e", script_chrome], capture_output=True, text=True).stdout.strip()
                    if result == "Reused":
                        return

                    # Try Safari
                    result = subprocess.run(["osascript", "-e", script_safari], capture_output=True, text=True).stdout.strip()
                    if result == "Reused":
                        return
                    
                    # If no tab was reused, just open normally (creates new tab)
                    webbrowser.open(dashboard_url)
                    
                except Exception as e:
                    print(f"Smart open failed: {e}")
                    webbrowser.open(dashboard_url)
            
            threading.Thread(target=open_browser).start()

        elif target == "db":
            if is_port_open(1521): return
            print("Starting Oracle DB...")
            start_db_script = os.path.join(PROJECT_ROOT, "scripts", "start_db.sh")
            cmd = ["/bin/bash", start_db_script]
            connections = params.get('connections', []) if params else []
            if connections:
                cmd.extend(connections)
            subprocess.Popen(cmd, cwd=PROJECT_ROOT)

    def stop_process(self, target):
        if target == "server":
            if PROCS["server"]:
                print("Killing Server...")
                PROCS["server"].kill()
                PROCS["server"] = None
            
            if PROCS["frontend"]:
                print("Killing Frontend...")
                PROCS["frontend"].kill()
                PROCS["frontend"] = None
                
            # 혹시 남아있는 Django/Vite 프로세스도 죽이기
            subprocess.run(["pkill", "-9", "-f", "runserver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-9", "-f", "vite"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        elif target == "db":
            print("Stopping Oracle DB and DBeaver...")
            # DBeaver 즉시 강제 종료 (10초 이내 보장)
            subprocess.run(["killall", "-9", "dbeaver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["killall", "-9", "DBeaver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-9", "-f", "DBeaver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Docker 컨테이너 종료
            subprocess.run(["docker", "kill", "oracle-xe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["docker", "kill", "oracle"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def restart_process(self, target, params=None):
        print(f"Restarting {target}...")
        if target == "server":
            if PROCS["server"] or is_port_open(8000): 
                self.stop_process("server")
                time.sleep(1)
            self.start_process("server")
        
        elif target == "db":
            self.stop_process("db")
            time.sleep(2)
            self.start_process("db", params)

    def get_manifest(self):
        return json.dumps({
            "name": "Forkast Controller",
            "short_name": "Forkast",
            "description": "Control Forkast Server & DB",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#0f172a",
            "theme_color": "#3b82f6",
            "icons": [
                {"src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect fill='%233b82f6' width='100' height='100' rx='20'/><text x='50' y='65' font-size='50' text-anchor='middle' fill='white'>F</text></svg>", "sizes": "192x192", "type": "image/svg+xml"},
                {"src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect fill='%233b82f6' width='100' height='100' rx='20'/><text x='50' y='65' font-size='50' text-anchor='middle' fill='white'>F</text></svg>", "sizes": "512x512", "type": "image/svg+xml"}
            ]
        })

    def get_html(self):
        return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Forkast">
    <meta name="theme-color" content="#0f172a">
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect fill='%233b82f6' width='100' height='100' rx='20'/><text x='50' y='65' font-size='50' text-anchor='middle' fill='white'>F</text></svg>">
    <title>Forkast Controller</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        :root { --bg: #0f172a; --card: #1e293b; --primary: #3b82f6; --text: #f8fafc; --success: #10b981; --danger: #ef4444; --warning: #f59e0b; }
        html, body { height: 100%; margin: 0; padding: 0; }
        body { 
            background: var(--bg); 
            color: var(--text); 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            display: flex; 
            flex-direction: column;
            align-items: center; 
            justify-content: center; 
            min-height: 100vh;
            padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
        }
        .container { 
            background: var(--card); 
            padding: 30px 25px; 
            border-radius: 24px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.4); 
            width: 90%; 
            max-width: 380px; 
            text-align: center; 
            border: 1px solid rgba(255,255,255,0.1);
            position: relative;
        }
        h1 { 
            margin: 0 0 25px 0; 
            font-size: 1.6rem;
            font-weight: 800; 
            background: linear-gradient(to right, #60a5fa, #a78bfa); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
        }
        
        .control-group { 
            background: rgba(0,0,0,0.3); 
            padding: 18px 20px; 
            border-radius: 16px; 
            margin-bottom: 15px; 
            display: flex; 
            align-items: center; 
            justify-content: space-between; 
        }
        .label { font-weight: 800; font-size: 1.1rem; color: #ffffff; display: flex; align-items: center; gap: 12px; }
        
        .status-dot { 
            width: 14px; height: 14px; border-radius: 50%; 
            background: #475569; 
            box-shadow: 0 0 10px rgba(0,0,0,0.6); 
            transition: 0.3s; 
        }
        .status-dot.active { background: #10b981; box-shadow: 0 0 15px #10b981; }
        .status-dot.starting { background: #f59e0b; animation: pulse 1s infinite; box-shadow: 0 0 15px #f59e0b; }
        .status-dot.stopping, .status-dot.restarting { background: #f59e0b; animation: pulse 1s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.1); } }

        /* Toast Notification */
        #toast {
            position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%) translateY(100px);
            background: rgba(16, 185, 129, 0.98); color: white; padding: 14px 30px;
            border-radius: 50px; font-weight: 900; font-size: 1rem; z-index: 1000;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 15px 35px rgba(0,0,0,0.5);
            white-space: nowrap;
        }
        #toast.show { transform: translateX(-50%) translateY(0); }
        #toast.error { background: rgba(220, 38, 38, 0.98); }

        .btn-group { display: flex; gap: 10px; }
        button { 
            border: none; 
            width: 48px; height: 48px; 
            border-radius: 14px; 
            font-size: 1.2rem;
            cursor: pointer; 
            transition: 0.2s; 
            display: flex; align-items: center; justify-content: center;
        }
        button i { font-weight: 900 !important; }
        button:active { transform: scale(0.9); }
        
        .btn-start { background: #3b82f6; color: white; }
        .btn-start:disabled { background: #1e293b; color: #475569; border: 1px solid #334155; }
        .btn-stop { background: #ef4444; color: white; }
        .btn-stop:disabled { background: #1e293b; color: #475569; border: 1px solid #334155; }
        .btn-restart { background: #8b5cf6; color: white; }
        .btn-restart:disabled { background: #1e293b; color: #475569; border: 1px solid #334155; }
        
        button i { font-weight: 900 !important; }
        button:disabled i { color: #64748b !important; opacity: 0.8; } /* 비활성 상태에서도 아이콘 형태가 확실히 보이도록 보정 */

        .close-btn { 
            width: 100%; height: 55px;
            margin-top: 25px; 
            background: rgba(255,255,255,0.08); 
            border: 1px solid #475569; 
            color: #ffffff; 
            border-radius: 14px;
            font-size: 1.1rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }
        .close-btn:active { background: #334155; }

        /* Modal */
        .modal-overlay { 
            position: fixed; inset: 0; 
            background: rgba(0,0,0,0.85); 
            backdrop-filter: blur(8px);
            display: flex; align-items: center; justify-content: center; 
            z-index: 100; 
            opacity: 0; pointer-events: none; 
            transition: 0.25s; 
        }
        .modal-overlay.open { opacity: 1; pointer-events: auto; }
        .modal { 
            background: var(--card); 
            padding: 25px; 
            border-radius: 20px; 
            width: 85%; max-width: 320px;
            transform: scale(0.9); transition: 0.25s; 
        }
        .modal-overlay.open .modal { transform: scale(1); }
        .modal h3 { margin: 0 0 20px 0; font-size: 1.2rem; }
        .checkbox-group { display: flex; flex-direction: column; gap: 15px; margin-bottom: 25px; }
        .checkbox-label { 
            display: flex; align-items: center; gap: 12px; 
            font-size: 1rem; 
            padding: 12px 15px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
        }
        .checkbox-label input { width: 22px; height: 22px; accent-color: var(--primary); }
        .modal-actions { display: flex; gap: 12px; }
        .modal-actions button { flex: 1; height: 48px; font-size: 1rem; font-weight: 600; }
        .btn-confirm { background: var(--primary); color: white; }
        .btn-cancel { background: #e2e8f0; color: #0f172a; transition: 0.2s; }
        .btn-cancel:hover { background: #cbd5e1; }

        .back-btn {
            width: 100%;
            margin-bottom: 20px;
            background: #334155;
            border: none;
            color: #f1f5f9;
            padding: 14px 20px;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .back-btn:active { 
            background: #475569;
        }

        .install-hint {
            margin-top: 20px;
            padding: 15px;
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.4);
            border-radius: 12px;
            font-size: 0.85rem;
            color: #cbd5e1;
            display: none;
        }
        @media (display-mode: browser) {
            .install-hint { display: block; }
        }
    </style>
</head>
<body>
    <div class="container">
        <button class="back-btn" onclick="goBack()">Wake Station</button>
        <h1>🎮 Forkast Remote</h1>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: -15px; margin-bottom: 25px;">원격 제어 센터</p>
        
        <div class="control-group">
            <div class="label">
                <div id="status-server" class="status-dot"></div>
                Django Server
            </div>
            <div class="btn-group">
                <button id="btn-restart-server" class="btn-restart" onclick="action('restart', 'server')" title="재가동"><i class="fa-solid fa-rotate-right"></i></button>
                <button id="btn-start-server" class="btn-start" onclick="action('start', 'server')"><i class="fa-solid fa-play"></i></button>
                <button id="btn-stop-server" class="btn-stop" onclick="action('stop', 'server')"><i class="fa-solid fa-stop"></i></button>
            </div>
        </div>

        <div class="control-group">
            <div class="label">
                <div id="status-db" class="status-dot"></div>
                Oracle DB
            </div>
            <div class="btn-group">
                <button id="btn-restart-db" class="btn-restart" onclick="openDbModal('restart')" title="재가동"><i class="fa-solid fa-rotate-right"></i></button>
                <button id="btn-start-db" class="btn-start" onclick="openDbModal('start')"><i class="fa-solid fa-play"></i></button>
                <button id="btn-stop-db" class="btn-stop" onclick="action('stop', 'db')"><i class="fa-solid fa-stop"></i></button>
            </div>
        </div>

        <button class="close-btn" onclick="closeApp()">Close Launcher</button>

        <div class="install-hint">
            📱 <strong>앱으로 설치하려면:</strong><br>
            Safari 공유 버튼 → "홈 화면에 추가"
        </div>

        <div id="toast">서버가 성공적으로 가동되었습니다!</div>
    </div>

    <div id="db-modal" class="modal-overlay">
        <div class="modal">
            <h3 id="db-modal-title">Select DB Connection</h3>
            <div class="checkbox-group">
                <label class="checkbox-label">
                    <input type="checkbox" value="adminDB" checked> adminDB
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" value="super_admin"> super_admin
                </label>
            </div>
            <div class="modal-actions">
                <button class="btn-cancel" onclick="closeDbModal()">Cancel</button>
                <button class="btn-confirm" onclick="confirmDbStart()">Start</button>
            </div>
        </div>
    </div>

    <script>
        let pendingDbAction = 'start';

        async function updateStatus() {
            try {
                const res = await fetch('/status');
                const data = await res.json();
                toggleStatus('server', data.server);
                toggleStatus('db', data.db);
            } catch(e) {}
        }

        let stateTimestamps = { server: 0, db: 0 };

        function toggleStatus(target, data) {
            const isActive = typeof data === 'object' ? data.server : data;
            const isReady = typeof data === 'object' ? (target === 'server' ? data.server_ready : data.db) : false;
            
            const dot = document.getElementById(`status-${target}`);
            const now = Date.now();

            // 상태 타임아웃 체크 (가동/종료 중 15초 경과 시 강제 초기화)
            const isProcessing = dot.classList.contains('starting') || dot.classList.contains('stopping') || dot.classList.contains('restarting');
            if (isProcessing) {
                if (stateTimestamps[target] === 0) stateTimestamps[target] = now;
                if (now - stateTimestamps[target] > 15000) {
                    dot.className = 'status-dot';
                    stateTimestamps[target] = 0;
                }
            } else {
                stateTimestamps[target] = 0;
            }
            
            // UI 상태 업데이트
            if (dot.classList.contains('stopping') || dot.classList.contains('restarting') || dot.classList.contains('starting')) {
                if (isActive && !dot.classList.contains('stopping')) {
                    if (target === 'server') {
                        if (isReady) dot.className = 'status-dot active';
                    } else if (isActive) {
                        dot.className = 'status-dot active';
                    }
                } else if (!isActive && dot.classList.contains('stopping')) {
                    dot.className = 'status-dot';
                }
            } else {
                if (target === 'server') {
                    if (isReady) dot.className = 'status-dot active';
                    else if (isActive) dot.className = 'status-dot starting';
                    else dot.className = 'status-dot';
                } else {
                    dot.className = isActive ? 'status-dot active' : 'status-dot';
                }
            }
            
            // 버튼 상태 관리
            const btnStart = document.getElementById(`btn-start-${target}`);
            const btnStop = document.getElementById(`btn-stop-${target}`);
            const btnRestart = document.getElementById(`btn-restart-${target}`);

            const isStarting = dot.classList.contains('starting');
            const isWorking = dot.classList.contains('stopping') || dot.classList.contains('restarting');

            // 가동 중(starting)일 때는 시작 버튼만 비활성화 (중복 클릭 방지)
            btnStart.disabled = isActive || isProcessing;
            
            // 정지 버튼: 실행 중이거나 '가동 중(시작 시도)'일 때 활성화 (사용자 취소 허용)
            btnStop.disabled = (!isActive && !isStarting) || isWorking;
            
            // 재시작 버튼: 실행 중일 때만 활성화 (동작 중 제외)
            btnRestart.disabled = !isActive || isProcessing;
        }

        async function action(type, target, params = {}) {
            const dot = document.getElementById(`status-${target}`);
            dot.className = 'status-dot'; // Reset
            
            if (type === 'start') {
                dot.classList.add('starting');
                showToast(`${target === 'server' ? '서버' : '데이터베이스'} 가동을 시작합니다...`);
            } else if (type === 'stop') {
                dot.classList.add('stopping');
                showToast(`${target === 'server' ? '서버' : '데이터베이스'} 종료 중...`);
            } else if (type === 'restart') {
                dot.classList.add('restarting');
                showToast(`${target === 'server' ? '서버' : '데이터베이스'} 재가동 중...`);
            }

            try {
                const res = await fetch('/', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ action: type, target: target, params: params })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    if (type === 'start') showToast(`${target === 'server' ? '서버' : '데이터베이스'} 가동 요청 완료!`);
                } else {
                    showToast(`오류: ${data.message}`, true);
                }
            } catch(e) {
                showToast(`연결 실패`, true);
            }
            setTimeout(updateStatus, 1000);
        }

        function showToast(msg, isError = false) {
            const toast = document.getElementById('toast');
            toast.innerText = msg;
            toast.className = isError ? 'show error' : 'show';
            setTimeout(() => toast.classList.remove('show'), 3000);
        }

        const dbModal = document.getElementById('db-modal');
        function openDbModal(actionType) { 
            pendingDbAction = actionType;
            document.getElementById('db-modal-title').innerText = actionType === 'restart' ? 'Restart DB Connection' : 'Select DB Connection';
            
            // Restart일 경우에도 모달을 띄워 연결 옵션을 다시 확인
            dbModal.classList.add('open'); 
        }
        function closeDbModal() { dbModal.classList.remove('open'); }
        function confirmDbStart() {
            const checkboxes = dbModal.querySelectorAll('input[type="checkbox"]:checked');
            const selected = Array.from(checkboxes).map(cb => cb.value);
            if (selected.length === 0) { alert("Select at least one connection."); return; }
            
            // pendingDbAction이 'restart'이면 restart 액션 호출, 아니면 start 호출
            action(pendingDbAction, 'db', { connections: selected });
            closeDbModal();
        }

        async function closeApp() {
            if(confirm('Close launcher and stop all services?')) {
                await fetch('/', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ action: 'close_app' })
                });
            }
        }

        function goBack() {
            window.location.href = 'http://' + window.location.hostname + ':9998';
        }

        setInterval(updateStatus, 2000);
        updateStatus();
    </script>
</body>
</html>
"""

def run_server():
    local_ip = get_local_ip()
    # Listen on all interfaces (0.0.0.0) for network access
    server = ReusableTCPServer(('0.0.0.0', PORT), ControlHandler)
    print(f"")
    print(f"========================================")
    print(f"  Forkast Controller Started!")
    print(f"========================================")
    print(f"")
    print(f"  📱 Phone Access:")
    print(f"     http://{local_ip}:{PORT}")
    print(f"")
    print(f"  💻 Local Access:")
    print(f"     http://localhost:{PORT}")
    print(f"")
    print(f"========================================")
    
    # --no-browser 옵션이 없으면 브라우저 열기
    if "--no-browser" not in sys.argv:
        webbrowser.open(f"http://localhost:{PORT}")
    else:
        print("  (브라우저 없이 실행됨)")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run_server()
