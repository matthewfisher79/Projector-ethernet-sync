import tkinter as tk
from tkinter import ttk, messagebox
import requests
import paramiko
import threading

# Network configuration
PROJECTOR_IP = "10.209.0.54"
BASE_URL = f"http://{PROJECTOR_IP}/program/serial/network/com/open"

# Common Epson Input Commands
INPUT_SOURCES = {
    "HDMI 1": "30",
    "HDMI 2": "A0",
    "Computer / VGA 1": "11",
    "Computer / VGA 2": "21",
    "LAN / Network": "53",
    "USB Display": "52"
}

# ---------------------------------------------------------
# HTTP Projector Helper Functions
# ---------------------------------------------------------
def send_projector_command(payload_data):
    try:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Epson-GUI-Controller/1.0"
        }
        response = requests.post(BASE_URL, data=payload_data, headers=headers, timeout=4)
        response.raise_for_status()
        messagebox.showinfo("Success", f"Projector command sent!\nStatus: {response.status_code}")
    except requests.exceptions.Timeout:
        messagebox.showerror("Timeout Error", f"Could not reach projector at {PROJECTOR_IP}.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("HTTP Error", f"Failed to send command:\n{e}")

def switch_input():
    source_code = INPUT_SOURCES.get(source_var.get())
    if source_code:
        send_projector_command({"source": source_code})

def send_action(action_code):
    send_projector_command({"cmd": action_code})

# ---------------------------------------------------------
# SSH Remote Linux Execution Helper Functions
# ---------------------------------------------------------
def run_ssh_command_thread(ip, user, pwd, command):
    """Executes SSH command in a background thread to prevent GUI freezing."""
    def worker():
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, username=user, password=pwd, timeout=5)
            
            # DISPLAY=:0 is required to launch graphical apps on the target display
            full_cmd = f"export DISPLAY=:0; {command}"
            stdin, stdout, stderr = client.exec_command(full_cmd)
            
            err = stderr.read().decode('utf-8')
            out = stdout.read().decode('utf-8')
            client.close()
            
            if err and "warning" not in err.lower():
                root.after(0, lambda: messagebox.showwarning("SSH Exec Notice", f"Output/Error:\n{err}"))
            else:
                root.after(0, lambda: messagebox.showinfo("SSH Success", f"Executed successfully:\n{command}"))
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("SSH Connection Error", str(e)))

    threading.Thread(target=worker, daemon=True).start()

def launch_presentation():
    host_ip = ssh_ip_entry.get().strip()
    user = ssh_user_entry.get().strip()
    pwd = ssh_pass_entry.get().strip()
    cmd = ssh_cmd_entry.get().strip()
    
    if not host_ip or not user:
        messagebox.showwarning("Missing Info", "Please enter the SSH IP address and Username.")
        return
        
    run_ssh_command_thread(host_ip, user, pwd, cmd)

# ---------------------------------------------------------
# GUI Setup
# ---------------------------------------------------------
root = tk.Tk()
root.title("Epson & Media Source Controller")
root.geometry("450x440")
root.resizable(False, False)

style = ttk.Style()
style.theme_use('clam')

# Tab Control (Notebook)
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# TAB 1: Projector Controls
tab_proj = ttk.Frame(notebook, padding="10")
notebook.add(tab_proj, text="Projector Hardware")

lbl_title = ttk.Label(tab_proj, text="Epson Hardware Control", font=("Helvetica", 12, "bold"))
lbl_title.pack(pady=(0, 10))

# Input Source Frame
frame_input = ttk.LabelFrame(tab_proj, text=" Select Input Source ", padding="10")
frame_input.pack(fill=tk.X, pady=5)

source_var = tk.StringVar(value="HDMI 1")
combo_sources = ttk.Combobox(frame_input, textvariable=source_var, values=list(INPUT_SOURCES.keys()), state="readonly")
combo_sources.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

btn_switch = ttk.Button(frame_input, text="Switch Input", command=switch_input)
btn_switch.pack(side=tk.RIGHT)

# Power & Mute Frame
frame_output = ttk.LabelFrame(tab_proj, text=" Power & A/V Controls ", padding="10")
frame_output.pack(fill=tk.X, pady=10)

ttk.Button(frame_output, text="Power ON", command=lambda: send_action("PWR ON")).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
ttk.Button(frame_output, text="Standby / OFF", command=lambda: send_action("PWR OFF")).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
ttk.Button(frame_output, text="A/V Mute ON", command=lambda: send_action("MUTE ON")).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
ttk.Button(frame_output, text="A/V Mute OFF", command=lambda: send_action("MUTE OFF")).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

frame_output.columnconfigure(0, weight=1)
frame_output.columnconfigure(1, weight=1)

# TAB 2: Linux Media Host (SSH)
tab_ssh = ttk.Frame(notebook, padding="10")
notebook.add(tab_ssh, text="Remote Presentation Host")

lbl_ssh_title = ttk.Label(tab_ssh, text="Linux Source Host (SSH)", font=("Helvetica", 12, "bold"))
lbl_ssh_title.pack(pady=(0, 10))

frame_ssh = ttk.LabelFrame(tab_ssh, text=" SSH Credentials ", padding="10")
frame_ssh.pack(fill=tk.X, pady=5)

ttk.Label(frame_ssh, text="Host IP:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
ssh_ip_entry = ttk.Entry(frame_ssh)
ssh_ip_entry.insert(0, "10.209.0.55")  # Example IP of the Linux PC/Raspberry Pi connected to HDMI
ssh_ip_entry.grid(row=0, column=1, fill=tk.X, expand=True, pady=2)

ttk.Label(frame_ssh, text="Username:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
ssh_user_entry = ttk.Entry(frame_ssh)
ssh_user_entry.insert(0, "pi")
ssh_user_entry.grid(row=1, column=1, fill=tk.X, expand=True, pady=2)

ttk.Label(frame_ssh, text="Password:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
ssh_pass_entry = ttk.Entry(frame_ssh, show="*")
ssh_pass_entry.grid(row=2, column=1, fill=tk.X, expand=True, pady=2)

frame_cmd = ttk.LabelFrame(tab_ssh, text=" Launch Presentation Software ", padding="10")
frame_cmd.pack(fill=tk.X, pady=10)

ttk.Label(frame_cmd, text="Command:").pack(anchor="w")
ssh_cmd_entry = ttk.Entry(frame_cmd)
ssh_cmd_entry.insert(0, "libreoffice --impress --show /path/to/presentation.pptx &")
ssh_cmd_entry.pack(fill=tk.X, pady=5)

btn_launch = ttk.Button(frame_cmd, text="Launch Remotely", command=launch_presentation)
btn_launch.pack(pady=5)

# Status Footer
lbl_status = ttk.Label(root, text=f"Target Projector IP: {PROJECTOR_IP}", font=("Helvetica", 9, "italic"), foreground="gray")
lbl_status.pack(side=tk.BOTTOM, pady=5)

if __name__ == "__main__":
    root.mainloop()
