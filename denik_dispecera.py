import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, Toplevel
from tkcalendar import DateEntry
import sqlite3
from datetime import date
import subprocess
import os
import json
from tkinter import Menu
import locale

# Načtení dat ze souboru
from app.connect import *
from app.pdf_export import create_pdf
from app.add_orders import add_order
from app.delete_orders import delete_order
from app.main_menu_orders import create_menu

# Create main window
root = tk.Tk()
root.title("Deník dispečera")

# Reverse mapping for search queries
reverse_column_mapping = {v: k for k, v in column_mapping.items()}



# Function to search orders based on user-selected column
def search_orders(*args):
    search_value = search_var.get()  # The text to search for
    search_column = column_combobox.get()  # The selected column from the combobox

    if search_value and search_column:
        column_name = reverse_column_mapping.get(search_column, None)
        if column_name:
            query = f"SELECT * FROM orders WHERE {column_name} LIKE ?"
            cursor.execute(query, ('%' + search_value + '%',))
            rows = cursor.fetchall()

            # Clear and display results
            for row in tree.get_children():
                tree.delete(row)
            
            for row in rows:
                tree.insert("", tk.END, values=row)
        else:
            messagebox.showwarning("Varování", "Vybrán neplatný sloupec.")
    else:
        display_orders()  # If no search value, display all orders

# Function to load selected order details into form
def load_selected_order(event):
    selected = tree.selection()
    if selected:
        item = tree.item(selected[0])
        order_data = item['values']
        
        # Populate form fields with selected order data
        entry_order.delete(0, tk.END)
        entry_order.insert(0, order_data[0])
        entry_zpmtr.delete(0, tk.END)
        entry_zpmtr.insert(0, order_data[1])
        load_cal.set_date(order_data[2])
        unload_cal.set_date(order_data[3])
        entry_load_loc.delete(0, tk.END)
        entry_load_loc.insert(0, order_data[4])
        entry_unload_loc.delete(0, tk.END)
        entry_unload_loc.insert(0, order_data[5])
        entry_pallets.delete(0, tk.END)
        entry_pallets.insert(0, order_data[6])
        entry_weight.delete(0, tk.END)
        entry_weight.insert(0, order_data[7])
        entry_spz.delete(0, tk.END)
        entry_spz.insert(0, order_data[8])
        entry_price.delete(0, tk.END)
        entry_price.insert(0, order_data[9])
        entry_carrier.delete(0, tk.END)
        entry_carrier.insert(0, order_data[10])
        entry_note.delete("1.0", tk.END)
        entry_note.insert("1.0", order_data[11])  # Load multi-line text

# Function to update the selected order
def update_order():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Varování", "K úpravě musíte vybrat objednávku")
        return
    
    order_number = entry_order.get()
    zpmtr = entry_zpmtr.get()
    load_date = load_cal.get()
    unload_date = unload_cal.get()
    load_location = entry_load_loc.get() or ''
    unload_location = entry_unload_loc.get() or ''
    pallets = entry_pallets.get()
    weight = entry_weight.get()
    spz = entry_spz.get()
    price = entry_price.get()
    carrier = entry_carrier.get()
    note = entry_note.get("1.0", tk.END).strip()  # Get text from Text widget

    cursor.execute('''
        UPDATE orders SET 
            zpmtr = ?, 
            load_date = ?, 
            unload_date = ?, 
            load_location = ?, 
            unload_location = ?, 
            pallets = ?, 
            weight = ?, 
            spz = ?,
            price = ?, 
            carrier = ?, 
            note = ?
        WHERE order_number = ?
    ''', (zpmtr, load_date, unload_date, load_location, unload_location, pallets, weight, spz, price, carrier, note, order_number))
    
    add_carrier_if_new(carrier)    
    add_location_if_new(load_location, 'load_locations')
    add_location_if_new(unload_location, 'unload_locations')
    conn.commit()
    update_comboboxes()  # Update ComboBoxes after adding a new order
    messagebox.showinfo("Hotovo", "Objednávka byla aktualizována")
    display_orders()  # Update the display after editing
    clear_form()

# Funkce pro přidání nového dopravce do databáze carriers
def add_carrier_if_new(carrier_name):
    if carrier_name:
        cursor_carriers.execute("SELECT * FROM carriers WHERE carrier_name = ?", (carrier_name,))
        if not cursor_carriers.fetchone():  # Pokud dopravce neexistuje, přidejte ho
            cursor_carriers.execute('''
                INSERT INTO carriers (carrier_name, street, city, postal_code, ico, dic, dispatcher_name, mobile, email, pallet_exchange, notes) 
                VALUES (?, '', '', '', '', '', '', '', '', '', '')
            ''', (carrier_name,))
            conn_carriers.commit()

# Funkce pro přidání nového místa do databáze locations
def add_location_if_new(location_name, table_name):
    if location_name:
        cursor_locations.execute(f"SELECT * FROM {table_name} WHERE location_name = ?", (location_name,))
        if not cursor_locations.fetchone():  # Pokud místo neexistuje, přidejte ho
            cursor_locations.execute(f"INSERT INTO {table_name} (location_name) VALUES (?)", (location_name,))
            conn_locations.commit()

# Funkce pro aktualizaci ComboBoxů a zajištění absence duplicit
def update_comboboxes():
    entry_carrier_combobox['values'] = load_carriers()
    entry_load_location_combobox['values'] = load_load_locations()
    entry_unload_location_combobox['values'] = load_unload_locations()

# Function to display orders in the Treeview
def display_orders():
    for row in tree.get_children():
        tree.delete(row)  # Clear the treeview
    
    cursor.execute("SELECT * FROM orders")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)

# Function to clear the form
def clear_form():
    entry_order.delete(0, tk.END)
    entry_zpmtr.delete(0, tk.END)
    load_cal.set_date(date.today())  # Reset to today's date
    unload_cal.set_date(date.today())  # Reset to today's date
    entry_load_loc.delete(0, tk.END)
    entry_unload_loc.delete(0, tk.END)
    entry_pallets.delete(0, tk.END)
    entry_weight.delete(0, tk.END)
    entry_spz.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_carrier.delete(0, tk.END)
    entry_note.delete("1.0", tk.END)
    search_entry.delete(0, tk.END)
    entry_load_location_combobox.set('Vyberte místo nakládky')
    entry_unload_location_combobox.set('Vyberte místo vykládky')
    entry_carrier_combobox.set('Vyberte dopravce')  
    
# Adjust spacing and padding
pad_x = 5
pad_y = 2

def open_manage_carriers():
    # Open manage_carriers.py
    try:
        save_main_window_position()

        # Dimensions for the new window
        new_window_width = 300
        new_window_height = 200

        # Open manage_carriers.py and pass the position arguments
        process = subprocess.Popen([
            "python", 
            os.path.join("app", "manage_carriers.py"),
            str(new_window_width),
            str(new_window_height)
        ])
        process.wait()  # Wait for the subprocess to finish
        update_comboboxes()  # Update the ComboBox after subprocess completes
    except Exception as e:
        print(f"Error opening manage_carriers.py: {e}")

def open_manage_locations():
    try:
        save_main_window_position()

        # Rozměry nového okna
        new_window_width = 300
        new_window_height = 400

        # Otevření manage_locations.py a předání argumentů
        process = subprocess.Popen([
            "python", 
            os.path.join("app", "manage_locations.py"),
            str(new_window_width),
            str(new_window_height),
            
        ])
        process.wait()  # Čekání na dokončení podprocesu
        update_comboboxes()  # Aktualizace comboboxů po dokončení podprocesu
    except Exception as e:
        print(f"Chyba při otevírání manage_locations.py: {e}")



# Funkce pro uložení pozice hlavního okna
def save_main_window_position():
    try:
        x = root.winfo_x()
        y = root.winfo_y()
        width = root.winfo_width()
        height = root.winfo_height()
        with open("window_position.json", "w") as f:
            json.dump({"x": x, "y": y, "width": width, "height": height}, f)
    except Exception as e:
        print(f"Error saving window position: {e}")
    


# Funkce pro uložení pozice hlavního okna
def save_main_window_position():
    try:
        x = root.winfo_x()
        y = root.winfo_y()
        width = root.winfo_width()
        height = root.winfo_height()
        with open("window_position.json", "w") as f:
            json.dump({"x": x, "y": y, "width": width, "height": height}, f)
    except Exception as e:
        print(f"Chyba při ukládání pozice okna: {e}")





# Function to handle arrow keys in Treeview
def handle_arrow_keys(event):
    selected = tree.selection()
    if not selected:
        return
    
    # Get the index of the currently selected row
    current_index = tree.index(selected[0])
    children = tree.get_children()  # List of all items in the Treeview

    # Calculate the new index based on the key pressed
    if event.keysym == "Up":
        new_index = max(0, current_index - 1)
    elif event.keysym == "Down":
        new_index = min(len(children) - 1, current_index + 1)
    else:
        return  # Ignore other keys

    # Update selection and load the selected order details
    tree.selection_set(children[new_index])
    load_selected_order(None)  # Load the details of the newly selected row

# Center the window on the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
width = 1280
height = 800
x = (screen_width / 2) - (width / 2)
y = (screen_height / 2) - (height / 2)
root.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

# Adjust spacing and padding
pad_x = 5
pad_y = 2

# Order number
tk.Label(root, text="Číslo objednávky:").grid(row=0, column=0, sticky="w", padx=pad_x, pady=pad_y)
entry_order = tk.Entry(root)
entry_order.grid(row=0, column=0, sticky="W", padx=105, pady=pad_y)

# ZPMTR
tk.Label(root, text="ZPMTR:").grid(row=1, column=0, sticky="W", padx=pad_x, pady=pad_y)
entry_zpmtr = tk.Entry(root)
entry_zpmtr.grid(row=1, column=0, sticky="w", padx=105, pady=pad_y)

# Load Date (with calendar)
tk.Label(root, text="Datum nakládky:").grid(row=2, column=0, sticky="w", padx=pad_x, pady=pad_y)
load_cal = DateEntry(root, date_pattern='dd-mm-yyyy')
load_cal.grid(row=2, column=0, sticky="w", padx=105, pady=pad_y)

# Unload Date (with calendar)
tk.Label(root, text="Datum vykládky:").grid(row=3, column=0, sticky="w", padx=pad_x, pady=pad_y)
unload_cal = DateEntry(root, date_pattern='dd-mm-yyyy')
unload_cal.grid(row=3, column=0, sticky="w", padx=105, pady=pad_y)

# Load Location
tk.Label(root, text="Místo naložení:").grid(row=4, column=0, sticky="w", padx=pad_x, pady=pad_y)
entry_load_loc = tk.Entry(root)
entry_load_loc.grid(row=4, column=0, sticky="w", padx=105, pady=pad_y)

# Unload Location
tk.Label(root, text="Místo vykládky").grid(row=5, column=0, sticky="w", padx=pad_x, pady=pad_y)
entry_unload_loc = tk.Entry(root)
entry_unload_loc.grid(row=5, column=0, sticky="w", padx=105, pady=pad_y)

# Pallets
tk.Label(root, text="Palet:").grid(row=6, column=0, sticky="w", padx=pad_x, pady=pad_y)
entry_pallets = tk.Entry(root)
entry_pallets.grid(row=6, column=0, sticky="w", padx=105, pady=pad_y)

# Weight
tk.Label(root, text="Váha(kg):").grid(row=7, column=0, sticky="w", padx=pad_x, pady=pad_y)
entry_weight = tk.Entry(root)
entry_weight.grid(row=7, column=0, sticky="w", padx=105, pady=pad_y)

# SPZ
tk.Label(root, text="SPZ:").grid(row=8, column=0, sticky="w", padx=pad_x, pady=pad_y)
entry_spz = tk.Entry(root)
entry_spz.grid(row=8, column=0, sticky="w", padx=105, pady=pad_y)

# Price
tk.Label(root, text="Cena €:").grid(row=9, column=0, sticky="w", padx=pad_x, pady=pad_y)
entry_price = tk.Entry(root)
entry_price.grid(row=9, column=0, sticky="w", padx=105, pady=pad_y)

# Carrier
tk.Label(root, text="Dopravce:").grid(row=10, column=0, sticky="w", padx=pad_x, pady=pad_y)
entry_carrier = tk.Entry(root)
entry_carrier.grid(row=10, column=0, sticky="w", padx=105, pady=pad_y)

# Note
tk.Label(root, text="Poznámka:").grid(row=11, column=0, sticky="w", padx=pad_x, pady=pad_y)
entry_note = tk.Text(root, height=5, width=40)  # Multi-line text widget
entry_note.grid(row=11, column=0, sticky="w", padx=105, pady=pad_y)

# Počáteční nastavení
entry_order.focus_set()

# Nastavení pořadí zaměřování (FUNKCE TAB)
entry_order.bind("<Tab>", lambda e: entry_zpmtr.focus_set())
entry_zpmtr.bind("<Tab>", lambda e: load_cal.focus_set())
load_cal.bind("<Tab>", lambda e: unload_cal.focus_set())
unload_cal.bind("<Tab>", lambda e: entry_load_loc.focus_set())
entry_load_loc.bind("<Tab>", lambda e: entry_unload_loc.focus_set())
entry_unload_loc.bind("<Tab>", lambda e: entry_pallets.focus_set())
entry_pallets.bind("<Tab>", lambda e: entry_weight.focus_set())
entry_weight.bind("<Tab>", lambda e: entry_spz.focus_set())
entry_spz.bind("<Tab>", lambda e: entry_price.focus_set())
entry_price.bind("<Tab>", lambda e: entry_carrier.focus_set())
entry_carrier.bind("<Tab>", lambda e: entry_note.focus_set())
entry_note.bind("<Tab>", lambda e: entry_order.focus_set())  # Cyklus zpět na první pole

# Buttons
tk.Button(root, text="Přidat", command=lambda: add_order(cursor, conn, entry_order, entry_zpmtr, load_cal, unload_cal, entry_load_loc,
                                                            entry_unload_loc, entry_pallets, entry_weight, entry_spz,
                                                            entry_price, entry_carrier, entry_note,
                                                            add_location_if_new, add_carrier_if_new,
                                                            update_comboboxes, display_orders, clear_form)).grid(row=12, column=0, sticky="w", padx=5, pady=pad_y)
tk.Button(root, text="Upravit", command=update_order).grid(row=12, column=0, sticky="w", padx=55, pady=pad_y)
tk.Button(root, text="Vymazat", command=lambda: delete_order(cursor, conn, tree, display_orders, clear_form)).grid(row=12, column=0, sticky="w", padx=110, pady=pad_y)
tk.Button(root, text="Vyčistit formulář", command=clear_form).grid(row=12, column=0, sticky="w", padx=175, pady=pad_y)
tk.Button(root, text="Vytvořit PDF", command=lambda: create_pdf(tree)).grid(row=12, column=1, sticky="w", padx=100, pady=pad_y)
tk.Button(root, text="Adresář dopravců", command=open_manage_carriers).grid(row=10, column=0, sticky="w", columnspan=2, padx=470, pady=0)
tk.Button(root, text="Adresář míst", command=open_manage_locations).grid(row=4, column=0, sticky="w", columnspan=2, padx=470, pady=0)


# Search
tk.Label(root, text="Hledat").grid(row=13, column=0, sticky="e", padx=pad_x, pady=pad_y)
search_var = tk.StringVar()
search_entry = tk.Entry(root, textvariable=search_var)
search_entry.grid(row=13, column=1, sticky="w", padx=pad_x, pady=pad_y)

column_combobox = ttk.Combobox(root, values=list(column_mapping.values()))
column_combobox.grid(row=13, column=1, sticky="w", padx=140, pady=pad_y)

search_var.trace_add("write", search_orders)

# Create a frame to hold the Treeview and scrollbar
tree_frame = tk.Frame(root)
tree_frame.grid(row=14, column=0, columnspan=4, sticky='nsew')

# Create the Treeview
columns = ["číslo objednávky", "zpmtr", "datum nakládky", "datum vykládky", "nakládka", "vykládka", "palet", "váha", "spz", "cena", "dopravce", "poznámka"]
tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=column_mapping.get(col, col))
    tree.column(col, width=100)

# Create the vertical scrollbar
scrollbar = tk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

# Pack Treeview and scrollbar
tree.pack(side='left', fill='both', expand=True)
scrollbar.pack(side='right', fill='y')

tree.bind("<ButtonRelease-1>", load_selected_order)  # Bind the selection event to load order
tree.bind("<Up>", handle_arrow_keys)  # Bind Up arrow key to handle_arrow_keys function
tree.bind("<Down>", handle_arrow_keys)  # Bind Down arrow key to handle_arrow_keys function



# Function to update the entry_carrier text box when a carrier is selected from the combobox
def update_carrier_entry(event):
    selected_carrier = entry_carrier_combobox.get()
    entry_carrier.delete(0, tk.END)  # Clear the entry field
    entry_carrier.insert(0, selected_carrier)  # Insert the selected carrier

# Create the text entry field for manual input (keep both entry and combobox for flexibility)
entry_carrier = tk.Entry(root)
entry_carrier.grid(row=10, column=0, sticky="w", padx=105, pady=pad_y)



# Function to load carriers from the carriers database
def load_carriers():
    cursor_carriers.execute("SELECT carrier_name FROM carriers ORDER BY carrier_name")
    carriers = {row[0] for row in cursor_carriers.fetchall()}  # Použijte množinu k zajištění unikátnosti
    return sorted(carriers, key=locale.strxfrm)  # Seřaďte seznam pro konzistentnost
    load_carrier_combobox['values'] = carrier_names

entry_carrier_combobox = ttk.Combobox(root, values=load_carriers(), width=30)
entry_carrier_combobox.grid(row=10, column=0, sticky="w", padx=250, pady=pad_y)
entry_carrier_combobox.set('Vyberte dopravce')  # Defaultní text
# Bind the function to the combobox selection event
entry_carrier_combobox.bind("<<ComboboxSelected>>", update_carrier_entry)

# Function to load locations from the locations database (nakládka a vykládka)
def load_load_locations():
    cursor_locations.execute("SELECT location_name FROM load_locations")
    locations = {row[0] for row in cursor_locations.fetchall()}  # Použijte množinu k zajištění unikátnosti
    return sorted(locations, key=locale.strxfrm)  # Seřaďte seznam pro konzistentnost

def load_unload_locations():
    cursor_locations.execute("SELECT location_name FROM unload_locations")
    locations = {row[0] for row in cursor_locations.fetchall()}  # Použijte množinu k zajištění unikátnosti
    return sorted(locations, key=locale.strxfrm)  # Seřaďte seznam pro konzistentnost


# Function to update the entry_load_location text box when a load location is selected from the combobox
def update_load_location_entry(event):
    selected_location = entry_load_location_combobox.get()
    entry_load_loc.delete(0, tk.END)  # Clear the entry field
    entry_load_loc.insert(0, selected_location)  # Insert the selected location

# Function to update the entry_unload_location text box when an unload location is selected from the combobox
def update_unload_location_entry(event):
    selected_location = entry_unload_location_combobox.get()
    entry_unload_loc.delete(0, tk.END)  # Clear the entry field
    entry_unload_loc.insert(0, selected_location)  # Insert the selected location

# Create the text entry fields for manual input (keep both entry and combobox for flexibility)
entry_load_loc = tk.Entry(root)
entry_load_loc.grid(row=4, column=0, sticky="w", padx=105, pady=pad_y)

entry_unload_loc = tk.Entry(root)
entry_unload_loc.grid(row=5, column=0, sticky="w", padx=105, pady=pad_y)

# Create the comboboxes for selecting locations
entry_load_location_combobox = ttk.Combobox(root, values=load_load_locations(), width=30)
entry_load_location_combobox.grid(row=4, column=0, sticky="w", padx=250, pady=pad_y)
entry_load_location_combobox.set('Vyberte místo nakládky')  # Defaultní text
entry_load_location_combobox.bind("<<ComboboxSelected>>", update_load_location_entry)

entry_unload_location_combobox = ttk.Combobox(root, values=load_unload_locations(), width=30)
entry_unload_location_combobox.grid(row=5, column=0, sticky="w", padx=250, pady=pad_y)
entry_unload_location_combobox.set('Vyberte místo vykládky')  # Defaultní text
entry_unload_location_combobox.bind("<<ComboboxSelected>>", update_unload_location_entry)

create_menu(root)

# Configure grid weights for expanding
root.grid_rowconfigure(14, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

# Display all orders on startup
display_orders()

# Start the main event loop
root.mainloop()

# Close the SQLite connection on exit
conn.close()