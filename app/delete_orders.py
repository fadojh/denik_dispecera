import sqlite3
import tkinter as tk
from tkinter import messagebox

def delete_order(cursor, conn, tree, display_orders, clear_form):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Varování", "Není vybraná objednávka k vymazání")
        return
    
    item = tree.item(selected[0])
    order_number = item['values'][0]

    confirm = messagebox.askyesno("Potvrzení vymazání", f"Chcete vymazat objednávku {order_number}?")
    if confirm:
        cursor.execute("DELETE FROM orders WHERE order_number = ?", (order_number,))
        conn.commit()
        display_orders()  # Update the display after deletion
        clear_form()
        messagebox.showinfo("Hotovo", f"Objednávka {order_number} byla vymazána.")
