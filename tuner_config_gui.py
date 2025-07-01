import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os

# Fields and their constraints
fields = {
    "name": {"type": "text"},
    "tunerMode": {"type": "dropdown", "options": ["DVB", "Beacon"]},
    "lnbMode": {"type": "dropdown", "options": ["V_OFF", "H_OFF", "V_Low", "H_Low", "V_High", "H_High"]},
    "lnbLocal": {"type": "int", "min": 0, "max": 12300000},
    "tunerSymbolRate": {"type": "int", "min": 100000, "max": 500000000},
    "tunerFrequency": {"type": "int", "min": 9500000, "max": 21500000},
    "satlliteLon": {"type": "int", "min": -1800, "max": 1800}
}

# Order to save fields
ordered_keys = [
    "name",
    "tunerMode",
    "lnbMode",
    "lnbLocal",
    "tunerSymbolRate",
    "tunerFrequency",
    "satlliteLon"
]

entries = {}
csv_path = None

def choose_csv_path():
    global csv_path
    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Select the location to save the CSV file"
    )
    if path:
        csv_path = path
        path_label.config(text=f"Selected Path:\n{csv_path}")

def save_to_csv():
    global csv_path
    if not csv_path:
        messagebox.showwarning("Warning", "Please select the file save location first.")
        return

    row = []
    for key, config in fields.items():
        value = entries[key].get()

        if config["type"] == "int":
            try:
                num = int(value)
                if not (config["min"] <= num <= config["max"]):
                    raise ValueError
                row.append(num)
            except ValueError:
                messagebox.showerror("Error", f"Value for '{key}' must be a number between {config['min']} and {config['max']}.")
                return
        elif config["type"] == "text":
            if not value.strip():
                messagebox.showerror("Error", f"Field '{key}' cannot be empty.")
                return
            row.append(value.strip())
        elif config["type"] == "dropdown":
            if value not in config["options"]:
                messagebox.showerror("Error", f"Invalid selection for '{key}'.")
                return
            row.append(value)

    entry_map = dict(zip(fields.keys(), row))

    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(ordered_keys)
        writer.writerow([entry_map[k] for k in ordered_keys])

    messagebox.showinfo("Success", "Data saved successfully.")
    for widget in entries.values():
        if isinstance(widget, tk.Entry):
            widget.delete(0, tk.END)
        else:
            widget.set('')

root = tk.Tk()
root.title("ACU Config")

for idx, (key, config) in enumerate(fields.items()):
    label = tk.Label(root, text=key)
    label.grid(row=idx, column=0, padx=10, pady=5, sticky="e")

    if config["type"] == "dropdown":
        var = tk.StringVar()
        combo = ttk.Combobox(root, textvariable=var, values=config["options"], state="readonly")
        combo.grid(row=idx, column=1, padx=10, pady=5)
        entries[key] = var
    else:
        entry = tk.Entry(root)
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entries[key] = entry

choose_btn = tk.Button(root, text="Select CSV Save Location", command=choose_csv_path)
choose_btn.grid(row=len(fields), column=0, pady=10)

path_label = tk.Label(root, text="No path selected yet", fg="blue", wraplength=300, justify="left")
path_label.grid(row=len(fields), column=1, pady=10)

btn = tk.Button(root, text="Save to CSV File", command=save_to_csv)
btn.grid(row=len(fields)+1, columnspan=2, pady=15)

root.mainloop()
