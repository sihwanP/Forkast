#!/bin/bash
cd "$(dirname "$0")"

# 1. Setup Environment Variables
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

echo "Starting Forkast Launcher..."
echo "Work Directory: $(pwd)"

# 2. Select Python Interpreter
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
    echo "Using Virtual Environment: $PYTHON_CMD"
elif [ -f ".venv/bin/python3" ]; then
    PYTHON_CMD=".venv/bin/python3"
    echo "Using Virtual Environment: $PYTHON_CMD"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "Using System Python: $PYTHON_CMD"
else
    PYTHON_CMD="/usr/bin/python3"
    echo "Using Security Fallback Python: $PYTHON_CMD"
fi

# 3. Start Wake Server (port 9998) if not already running
if ! lsof -i :9998 -sTCP:LISTEN > /dev/null 2>&1; then
    echo "Starting Wake Server (port 9998)..."
    "$PYTHON_CMD" scripts/wake_server.py &
    WAKE_PID=$!
    echo "Wake Server started (PID: $WAKE_PID)"
else
    echo "Wake Server already running on port 9998"
fi

# 4. Run the Web Launcher (port 9999) - Foreground
"$PYTHON_CMD" scripts/web_launcher.py

echo "Launcher exited with code $?"
read -p "Press any key to close..."
