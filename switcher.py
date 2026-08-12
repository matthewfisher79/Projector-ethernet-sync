import tkinter as tk
from tkinter import ttk, messagebox
import requests

# Network configuration
PROJECTOR_IP = "10.209.0.54"
BASE_URL = f"http://{PROJECTOR_IP}/program/serial/network/com/open"

# Common Epson Input Commands / Source Codes
# Note: ESC/VP21 hex commands or standard URL payload formats
INPUT_SOURCES = {
    "HDMI 1": "30",
    "HDMI 2": "A0",
    "Computer / VGA 1": "11",
    "Computer / VGA 2": "21",
    "LAN / Network": "53",
    "USB Display": "52"
}

def send_projector_command(payload_data):
    """Helper function to execute the HTTP POST request."""
    try:
        # Standard headers often used by web control interfaces
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Epson-GUI-Controller/1.0"
        }
        
        # Send HTTP POST request to the projector endpoint
        response = requests.post(BASE_URL, data=payload_data, headers=headers, timeout=4)
        response.raise_for_status()
        
        messagebox.showinfo("Success", f"Command sent successfully!\nResponse: {response.status_code}")
    except requests.exceptions.Timeout:
        messagebox.showerror("Timeout Error", f"Could not reach projector at {PROJECTOR_IP}.\nCheck network connection.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("HTTP Error", f"Failed to send command:\n{e}")

def switch_input():
    """Switches input source based on dropdown selection."""
    selected_name = source_var.get()
    source_code = INPUT_SOURCES.get(selected_name)
    
    if not source_code:
        messagebox.showwarning("Selection Error", "Please select a valid input source.")
        return
        
    # Typical payload structure for Epson Web Control API
    payload = {"source": source_code}
    send_projector_command(payload)

def send_action(action_code):
    """Sends action/output control commands (Power, Mute, etc.)."""
    payload = {"cmd": action_code}
    send_projector_command(payload)

# ---------------------------------------------------------
# GUI Setup (Tkinter)
# ---------------------------------------------------------
root = tk.Tk()
root.title("Epson Projector Control")
root.geometry("380x320")
root.resizable(False, False)

# Set styling
style = ttk.Style()
style.theme_use('clam')

# Frame container
main_frame = ttk.Frame(root, padding="15")
main_frame.pack(fill=tk.BOTH, expand=True)

# Title Header
lbl_title = ttk.Label(main_frame, text="Projector Controller", font=("Helvetica", 14, "bold"))
lbl_title.pack(pady=(0, 15))

# Input Source Section
frame_input = ttk.LabelFrame(main_frame, text=" Select Input Source ", padding="10")
frame_input.pack(fill=tk.X, pady=5)

source_var = tk.StringVar(value="HDMI 1")
combo_sources = ttk.Combobox(frame_input, textvariable=source_var, values=list(INPUT_SOURCES.keys()), state="readonly")
combo_sources.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

btn_switch = ttk.Button(frame_input, text="Switch Input", command=switch_input)
btn_switch.pack(side=tk.RIGHT)

# Power & Output Controls Section
frame_output = ttk.LabelFrame(main_frame, text=" Power & Output Controls ", padding="10")
frame_output.pack(fill=tk.X, pady=10)

btn_pwr_on = ttk.Button(frame_output, text="Power ON", command=lambda: send_action("PWR ON"))
btn_pwr_on.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

btn_pwr_off = ttk.Button(frame_output, text="Standby / OFF", command=lambda: send_action("PWR OFF"))
btn_pwr_off.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

btn_mute = ttk.Button(frame_output, text="A/V Mute ON", command=lambda: send_action("MUTE ON"))
btn_mute.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

btn_unmute = ttk.Button(frame_output, text="A/V Mute OFF", command=lambda: send_action("MUTE OFF"))
btn_unmute.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

frame_output.columnconfigure(0, weight=1)
frame_output.columnconfigure(1, weight=1)

# Status Footer
lbl_status = ttk.Label(main_frame, text=f"Target IP: {PROJECTOR_IP}", font=("Helvetica", 9, "italic"), foreground="gray")
lbl_status.pack(side=tk.BOTTOM, pady=(10, 0))

# Run the Tkinter main loop
if __name__ == "__main__":
    root.mainloop()
