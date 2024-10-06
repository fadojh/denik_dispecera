
import sqlite3
import tkinter as tk
from tkinter import messagebox




def add_order(cursor, conn, entry_order,  entry_zpmtr, load_cal, unload_cal, entry_load_loc, entry_unload_loc,
              entry_pallets, entry_weight, entry_spz, entry_price, entry_carrier, entry_note,
              add_location_if_new, add_carrier_if_new, update_comboboxes, display_orders, clear_form):
    
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

    add_location_if_new(load_location, 'load_locations')
    add_location_if_new(unload_location, 'unload_locations')

    # Check for required fields
    if not (order_number and zpmtr and load_location and unload_location and price and carrier):
        messagebox.showwarning("Varování", "Vyplňte prosím všechna povinná pole: číslo objednávky, ZPMTR, místo nakládky, místo vykládky, cenu a dopravce..")
        return

    try:
        cursor.execute('''
            INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (order_number, zpmtr, load_date, unload_date, load_location, unload_location, pallets, weight, spz, price, carrier, note))
        conn.commit()
        add_carrier_if_new(carrier)
        update_comboboxes()  # Update ComboBoxes after adding a new order
        messagebox.showinfo("Hotovo", "Objednávka byla uložena")
        display_orders()  # Update the display after adding
        clear_form()
    except sqlite3.IntegrityError:
        messagebox.showerror("Chyba", "Objednávka existuje")