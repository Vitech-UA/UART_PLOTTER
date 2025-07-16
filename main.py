import serial
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation

SERIAL_PORT = 'COM5'
BAUD_RATE = 230400
TIMEOUT = 1

data = []

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)

def parse_uart_line(line):
    try:
        nums = [int(x) for x in line.strip().split(',') if x.strip().isdigit()]
        return nums
    except Exception as e:
        print(f"Parse error: {e}")
        return []

def get_max_value():
    try:
        val = int(max_val_entry.get())
        return val if val > 0 else None
    except ValueError:
        return None

def update_plot(frame):
    global data
    while ser.in_waiting:
        line = ser.readline().decode(errors='ignore')
        nums = parse_uart_line(line)
        if nums:
            data = [(x / 4095.0) * 3.3 for x in nums]

    if not data:
        return

    v_max = max(data)
    v_min = min(data)
    vpp = v_max - v_min

    ax.clear()
    ax.plot(data, linewidth=0.9, color='blue')
    ax.set_title(f"Live UART Plot — Vpp: {vpp:.3f} V")
    ax.set_xlabel("Index")
    ax.set_ylabel("Voltage [V]")

    y_max = get_max_value()
    if y_max:
        ax.set_ylim(0, y_max)
    else:
        ax.set_ylim(0, 3.5)

root = tk.Tk()
root.title("UART Plotter - COM6")

fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

control_frame = ttk.Frame(root)
control_frame.pack(fill=tk.X, padx=10, pady=5)

ttk.Label(control_frame, text="Max Value:").pack(side=tk.LEFT)
max_val_entry = ttk.Entry(control_frame, width=10)
max_val_entry.pack(side=tk.LEFT)
max_val_entry.insert(0, "")

def on_close():
    ser.close()
    root.destroy()

exit_btn = ttk.Button(control_frame, text="Вийти", command=on_close)
exit_btn.pack(side=tk.RIGHT)

ani = animation.FuncAnimation(fig, update_plot, interval=50, cache_frame_data=True)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
