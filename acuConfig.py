import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
print("آیکون موجوده؟", os.path.exists("eshtad.ico"))
# تعریف فیلدها و محدودیت‌ها
fields = {
    "name": {"type": "text"},
    "tunerMode": {"type": "dropdown", "options": ["DVB", "Beacon"]},
    "lnbMode": {"type": "dropdown", "options": ["V_OFF", "H_OFF", "V_Low", "H_Low", "V_High", "H_High"]},
    "lnbLocal": {"type": "int", "min": 0, "max": 12300000},
    "tunerSymbolRate": {"type": "int", "min": 100000, "max": 500000000},
    "tunerFrequency": {"type": "int", "min": 9500000, "max": 21500000},
    "satlliteLon": {"type": "int", "min": -1800, "max": 1800}
}

ordered_keys = list(fields.keys())
entries = {}

csv_path = None
csv_data = []
selected_index = None

def load_csv_file():
    global csv_path, csv_data
    path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")],
        title="Select CSV Config File"
    )
    if not path:
        return

    csv_path = path
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_data = list(reader)

    update_treeview()
    config_status.config(text=f"{len(csv_data)} configs loaded from:\n{csv_path}")

def update_treeview():
    for i in tree.get_children():
        tree.delete(i)
    for idx, row in enumerate(csv_data):
        values = [row.get(key, "") for key in ordered_keys]
        tree.insert("", "end", iid=str(idx), values=values)

def on_tree_select(event):
    global selected_index
    selected = tree.focus()
    if not selected:
        return
    selected_index = int(selected)
    row = csv_data[selected_index]
    for key in fields:
        value = row.get(key, "")
        if isinstance(entries[key], tk.StringVar):
            entries[key].set(value)
        else:
            entries[key].delete(0, tk.END)
            entries[key].insert(0, str(value))

def save_changes_to_csv():
    if csv_path is None or selected_index is None:
        messagebox.showerror("Error", "Please load and select a config first.")
        return

    updated_row = {}
    for key, config in fields.items():
        value = entries[key].get()
        try:
            if config['type'] == 'int':
                value = int(value)
                if not (config["min"] <= value <= config["max"]):
                    raise ValueError
            elif config['type'] == 'dropdown':
                if value not in config['options']:
                    raise ValueError
            elif config['type'] == 'text' and not value.strip():
                raise ValueError
            updated_row[key] = str(value)
        except:
            messagebox.showerror("Error", f"Invalid value for {key}")
            return

    # بروزرسانی مقدار در لیست اصلی
    csv_data[selected_index] = updated_row

    # اطمینان از اینکه همه ردیف‌ها فقط کلیدهای استاندارد دارند
    for i, row in enumerate(csv_data):
        cleaned_row = {k: row.get(k, "") for k in ordered_keys}
        csv_data[i] = cleaned_row

    # بازنویسی فایل
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=ordered_keys)
        writer.writeheader()
        writer.writerows(csv_data)

    update_treeview()
    messagebox.showinfo("Saved", "Changes saved to CSV.")

# رابط کاربری
root = tk.Tk()
root.iconbitmap(r"d:\shokouhi\csvFile\eshtad.ico")
root.title("Acu Config")

# فرم فیلدها
for idx, (key, config) in enumerate(fields.items()):
    label = tk.Label(root, text=key)
    label.grid(row=idx, column=0, padx=5, pady=3, sticky="e")

    if config["type"] == "dropdown":
        var = tk.StringVar()
        combo = ttk.Combobox(root, textvariable=var, values=config["options"], state="readonly")
        combo.grid(row=idx, column=1, padx=5, pady=3)
        entries[key] = var
    else:
        entry = tk.Entry(root)
        entry.grid(row=idx, column=1, padx=5, pady=3)
        entries[key] = entry

# دکمه لود فایل
load_btn = tk.Button(root, text="Load Config File", command=load_csv_file)
load_btn.grid(row=0, column=2, padx=10, pady=5)

# دکمه ذخیره تغییرات
save_btn = tk.Button(root, text="Save Changes", command=save_changes_to_csv)
save_btn.grid(row=1, column=2, padx=10, pady=5)

# وضعیت فایل
config_status = tk.Label(root, text="No Config loaded", fg="green", wraplength=300, justify="left")
config_status.grid(row=2, column=2, padx=10, pady=5)

# اسم فایل 
config_status = tk.Label(root, text="The name of the config file should be \"config1.csv\"", fg="red", wraplength=300, justify="left")
config_status.grid(row=3, column=2, padx=10, pady=5)

# Treeview برای لیست کانفیگ‌ها
tree = ttk.Treeview(root, columns=ordered_keys, show="headings", height=10)
for col in ordered_keys:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor="center")
tree.grid(row=len(fields), column=0, columnspan=3, padx=10, pady=10)

tree.bind("<<TreeviewSelect>>", on_tree_select)

root.mainloop()
