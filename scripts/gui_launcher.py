import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import signal
import sys

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Forkast Launcher")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Style
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 12), padding=10)
        style.configure('TLabel', font=('Helvetica', 14))

        # State
        self.selected_target = tk.StringVar(value="server") # 'server' or 'db'
        self.server_process = None
        self.db_process = None

        # UI Layout
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = ttk.Label(self.root, text="Forkast System Launcher", font=('Helvetica', 16, 'bold'))
        header.pack(pady=20)

        # Selection Frame
        select_frame = ttk.LabelFrame(self.root, text="Select Target", padding=15)
        select_frame.pack(fill="x", padx=20, pady=10)

        self.btn_select_server = ttk.Radiobutton(
            select_frame, 
            text="Django Server", 
            variable=self.selected_target, 
            value="server",
            command=self.update_status
        )
        self.btn_select_server.pack(side="left", expand=True)

        self.btn_select_db = ttk.Radiobutton(
            select_frame, 
            text="Oracle DB", 
            variable=self.selected_target, 
            value="db",
            command=self.update_status
        )
        self.btn_select_db.pack(side="right", expand=True)

        # Control Frame
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=20, pady=20)

        self.btn_start = ttk.Button(control_frame, text="▶ START", command=self.start_service)
        self.btn_start.pack(side="left", expand=True, fill="x", padx=5)

        self.btn_stop = ttk.Button(control_frame, text="⏹ STOP", command=self.stop_service)
        self.btn_stop.pack(side="left", expand=True, fill="x", padx=5)

        # Status Label
        self.status_label = ttk.Label(self.root, text="Ready", font=('Helvetica', 10), foreground="gray")
        self.status_label.pack(side="top", pady=5)

        # Footer
        btn_close = ttk.Button(self.root, text="Close Launcher", command=self.on_close)
        btn_close.pack(side="bottom", pady=20, fill="x", padx=50)
        
        # Initial Status Update
        self.update_status()

    def update_status(self):
        target = self.selected_target.get()
        is_running = False
        if target == "server" and self.server_process and self.server_process.poll() is None:
            is_running = True
        elif target == "db" and self.db_process and self.db_process.poll() is None:
            is_running = True
            
        status_text = f"Target: {target.upper()} | Status: {'RUNNING' if is_running else 'STOPPED'}"
        self.status_label.config(text=status_text, foreground="green" if is_running else "red")

    def start_service(self):
        target = self.selected_target.get()
        
        if target == "server":
            if self.server_process and self.server_process.poll() is None:
                messagebox.showinfo("Info", "Django Server is already running.")
                return

            try:
                # Assuming run from project root or scripts folder
                # Adjust path to manage.py
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                manage_py = os.path.join(project_root, "manage.py")
                
                print(f"Starting server: {manage_py}")
                self.server_process = subprocess.Popen(
                    [sys.executable, manage_py, "runserver", "0.0.0.0:8000"],
                    cwd=project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.status_label.config(text="Django Server Started", foreground="green")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start server: {e}")

        elif target == "db":
            if self.db_process and self.db_process.poll() is None:
                messagebox.showinfo("Info", "Oracle DB is already running.")
                return
            
            try:
                # TODO: Replace with ACTUAL Oracle start command
                # For example: docker start oracle-xe OR brew services start oracledb
                # Here we simulate a process for demonstration
                print("Starting Oracle DB (Simulation/Command)")
                # Using 'tail -f' as a dummy persistent process for simulation if real command unknown
                # The user should edit this line with their actual DB start logic
                self.db_process = subprocess.Popen(
                    ["docker", "start", "oracle-xe"], # Example command
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.status_label.config(text="Oracle DB Started (Command Sent)", foreground="green")
            except FileNotFoundError:
                 messagebox.showwarning("Warning", "Oracle start command not found (e.g. docker). Please edit the script.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start DB: {e}")

        self.update_status()

    def stop_service(self):
        target = self.selected_target.get()
        
        if target == "server":
            if self.server_process:
                self.server_process.terminate()
                self.server_process = None
                self.status_label.config(text="Django Server Stopped", foreground="red")
            else:
                messagebox.showinfo("Info", "Django Server is not running.")
        
        elif target == "db":
            if self.db_process:
                self.db_process.terminate() # Or use a stop command
                self.db_process = None
                self.status_label.config(text="Oracle DB Stopped", foreground="red")
            else:
                messagebox.showinfo("Info", "Oracle DB is not running.")

        self.update_status()

    def on_close(self):
        if self.server_process:
            self.server_process.terminate()
        if self.db_process:
            self.db_process.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    
    # Handle window close button (X)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    
    root.mainloop()
