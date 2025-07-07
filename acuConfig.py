import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os

print("آیکون موجوده؟", os.path.exists("eshtad.ico"))

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

def add_placeholder(entry, placeholder_text):
    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focus_out(event):
        if entry.get() == '':
            entry.insert(0, placeholder_text)
            entry.config(fg='gray')

    entry.insert(0, placeholder_text)
    entry.config(fg='gray')
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def load_csv_file():
    global csv_path, csv_data
    path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")],
        title="Select CSV Config File",
        parent=root
    )

    if path:
        csv_path = path
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            csv_data = list(reader)
        update_treeview()
        config_status.config(text=f"{len(csv_data)} configs loaded from:\n{csv_path}")
    else:
        create_new = messagebox.askyesno(
            "No File Selected",
            "No file was selected.\nWould you like to create a new config file named 'config1.csv'?",
            parent=root
        )
        if not create_new:
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="config1.csv",
            title="Save new config file as",
            parent=root
        )
        if not save_path:
            return

        csv_path = save_path
        csv_data = []
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=ordered_keys)
            writer.writeheader()
        update_treeview()
        config_status.config(text=f"New empty config file created:\n{csv_path}")

def save_new_config_file():
    global csv_path, csv_data
    dir_path = filedialog.askdirectory(title="Select Directory to Save config1.csv", parent=root)
    if not dir_path:
        return
    save_path = os.path.join(dir_path, "config1.csv")
    csv_path = save_path
    csv_data = []
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=ordered_keys)
        writer.writeheader()
    update_treeview()
    messagebox.showinfo("File Created", f"New config file created:\n{csv_path}", parent=root)
    config_status.config(text=f"New empty config file created:\n{csv_path}")

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
        widget = entries[key]
        placeholder = None
        if fields[key]['type'] == 'int':
            placeholder = f"{fields[key]['min']} - {fields[key]['max']}"
        if isinstance(widget, tk.StringVar):
            widget.set(value)
        else:
            widget.delete(0, tk.END)
            if value.strip() == "" and placeholder is not None:
                widget.insert(0, placeholder)
                widget.config(fg='gray')
            else:
                widget.insert(0, str(value))
                widget.config(fg='black')

def save_changes_to_csv():
    if csv_path is None or selected_index is None:
        messagebox.showerror("Error", "Please load and select a config first.", parent=root)
        return

    updated_row = {}
    for key, config in fields.items():
        widget = entries[key]
        value = widget.get()
        placeholder = None
        if config['type'] == 'int':
            placeholder = f"{config['min']} - {config['max']}"
        if value == placeholder:
            value = ''
        try:
            if config['type'] == 'int':
                value_int = int(value)
                if not (config["min"] <= value_int <= config["max"]):
                    raise ValueError
                value = value_int
            elif config['type'] == 'dropdown':
                if value not in config['options']:
                    raise ValueError
            elif config['type'] == 'text' and not value.strip():
                raise ValueError
            updated_row[key] = str(value)
        except:
            messagebox.showerror("Error", f"Invalid value for {key}", parent=root)
            return

    csv_data[selected_index] = updated_row
    for i, row in enumerate(csv_data):
        cleaned_row = {k: row.get(k, "") for k in ordered_keys}
        csv_data[i] = cleaned_row

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=ordered_keys)
        writer.writeheader()
        writer.writerows(csv_data)

    update_treeview()
    messagebox.showinfo("Saved", "Changes saved to CSV.", parent=root)

def add_new_config_row():
    global csv_data, csv_path
    if csv_path is None:
        messagebox.showerror("Error", "Please load or create a config file first.", parent=root)
        return

    new_row = {}
    for key, config in fields.items():
        widget = entries[key]
        value = widget.get()
        placeholder = None
        if config['type'] == 'int':
            placeholder = f"{config['min']} - {config['max']}"
        if value == placeholder:
            value = ''
        try:
            if config['type'] == 'int':
                value_int = int(value)
                if not (config["min"] <= value_int <= config["max"]):
                    raise ValueError
                value = value_int
            elif config['type'] == 'dropdown':
                if value not in config['options']:
                    raise ValueError
            elif config['type'] == 'text' and not value.strip():
                raise ValueError
            new_row[key] = str(value)
        except:
            messagebox.showerror("Error", f"Invalid value for {key}", parent=root)
            return

    csv_data.append(new_row)

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=ordered_keys)
        writer.writeheader()
        writer.writerows(csv_data)

    update_treeview()

    for key, widget in entries.items():
        if isinstance(widget, tk.StringVar):
            widget.set('')
        else:
            placeholder = None
            if fields[key]['type'] == 'int':
                placeholder = f"{fields[key]['min']} - {fields[key]['max']}"
            if placeholder is not None:
                widget.delete(0, tk.END)
                widget.insert(0, placeholder)
                widget.config(fg='gray')
            else:
                widget.delete(0, tk.END)

    messagebox.showinfo("Success", "New config row added and saved.", parent=root)

def delete_selected_config():
    global csv_data, csv_path, selected_index
    if csv_path is None or selected_index is None:
        messagebox.showerror("Error", "Please load and select a config to delete.", parent=root)
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected config?", parent=root)
    if not confirm:
        return

    del csv_data[selected_index]
    selected_index = None

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=ordered_keys)
        writer.writeheader()
        writer.writerows(csv_data)

    update_treeview()

    for key, widget in entries.items():
        if isinstance(widget, tk.StringVar):
            widget.set('')
        else:
            placeholder = None
            if fields[key]['type'] == 'int':
                placeholder = f"{fields[key]['min']} - {fields[key]['max']}"
            if placeholder is not None:
                widget.delete(0, tk.END)
                widget.insert(0, placeholder)
                widget.config(fg='gray')
            else:
                widget.delete(0, tk.END)

    messagebox.showinfo("Deleted", "Selected config has been deleted.", parent=root)
    

root = tk.Tk()
root.iconbitmap(r"d:\shokouhi\csvFile\eshtad.ico")
root.title("Acu Config")

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
        if config["type"] == "int":
            placeholder = f"{config['min']} - {config['max']}"
            add_placeholder(entry, placeholder)
        entries[key] = entry

load_btn = tk.Button(root, text="Load Config File", command=load_csv_file)
load_btn.grid(row=0, column=2, padx=10, pady=5)

save_btn = tk.Button(root, text="Save Changes", command=save_changes_to_csv)
save_btn.grid(row=1, column=2, padx=10, pady=5)

add_btn = tk.Button(root, text="Add New Config", command=add_new_config_row)
add_btn.grid(row=2, column=2, padx=10, pady=5)

delete_btn = tk.Button(root, text="Delete Selected Config", command=delete_selected_config)
delete_btn.grid(row=3, column=2, padx=10, pady=5)

save_file_btn = tk.Button(root, text="Create New config1.csv File", command=save_new_config_file)
save_file_btn.grid(row=4, column=2, padx=10, pady=5)

config_status = tk.Label(root, text="No Config loaded", fg="green", wraplength=300, justify="left")
config_status.grid(row=5, column=2, padx=10, pady=5)

config_status_filehint = tk.Label(root, text="The name of the config file should be \"config1.csv\"", fg="red", wraplength=300, justify="left")
config_status_filehint.grid(row=6, column=2, padx=10, pady=5)

tree = ttk.Treeview(root, columns=ordered_keys, show="headings", height=10)
for col in ordered_keys:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor="center")
tree.grid(row=len(fields), column=0, columnspan=3, padx=10, pady=10)

tree.bind("<<TreeviewSelect>>", on_tree_select)

root.mainloop()
