import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import os

# Funkce pro zobrazení dat z locations.db
def show_locations():
    # Připojení k databázi locations.db
    conn_locations = sqlite3.connect(os.path.join('db', 'locations.db'))
    cursor_locations = conn_locations.cursor()

    # Načtení dat z tabulek load_locations a unload_locations
    cursor_locations.execute("SELECT * FROM load_locations")
    load_data = cursor_locations.fetchall()

    cursor_locations.execute("SELECT * FROM unload_locations")
    unload_data = cursor_locations.fetchall()

     # Vytvoření okna
    window = tk.Tk()
    window.title("Správa míst")

    # Získání rozměrů obrazovky
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Nastavení rozměrů okna
    window_width = 1500
    window_height = 600

    # Výpočet souřadnic pro umístění okna do středu obrazovky
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Nastavení geometrie okna
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Rámec pro formulář
    form_frame = tk.Frame(window)
    form_frame.pack(fill=tk.X, padx=10, pady=10)

    # Pole pro jednotlivé vstupy
    fields = ['Název', 'Ulice', 'PSČ', 'Město', 'Prac. doba od', 'Prac. doba do', 'Kontaktní osoba', 'Mobil', 'Email', 'Poznámka']
    entries = {}

    # Rozdělení formuláře do dvou sloupců (dvou řádků)
    for i, field in enumerate(fields):
        label = tk.Label(form_frame, text=field)

        # První polovina do prvního sloupce (levého)
        if i < len(fields) // 2:
            label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = tk.Entry(form_frame)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)

        # Druhá polovina do druhého sloupce (pravého)
        else:
            label.grid(row=i - len(fields) // 2, column=2, padx=5, pady=5, sticky=tk.W)
            entry = tk.Entry(form_frame)
            entry.grid(row=i - len(fields) // 2, column=3, padx=5, pady=5, sticky=tk.W)

        entries[field] = entry

    # Rámec pro tlačítka
    button_frame = tk.Frame(window)
    button_frame.pack(fill=tk.X, padx=10, pady=10)

    # Funkce pro vložení dat do databáze
    def add_location():
        location_name = entries['Název'].get()
        
        # Kontrola duplicity
        cursor_locations.execute("SELECT COUNT(*) FROM load_locations WHERE location_name=?", (location_name,))
        exists = cursor_locations.fetchone()[0]
        
        if exists > 0:
            messagebox.showwarning("Varování", "Záznam s tímto názvem již existuje.")
            return
        
        data = tuple(entries[field].get() if entries[field].get() else "" for field in fields)

        cursor_locations.execute("""
            INSERT INTO load_locations (location_name, street, postal_code, city, working_hours_from, working_hours_to, 
                                        contact_person, mobile, email, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)

        cursor_locations.execute("""
            INSERT INTO unload_locations (location_name, street, postal_code, city, working_hours_from, working_hours_to, 
                                          contact_person, mobile, email, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)

        conn_locations.commit()

        # Přidání nového záznamu do Treeview
        tree.insert("", "end", values=data)

        for entry in entries.values():
            entry.delete(0, tk.END)

        messagebox.showinfo("Úspěch", f"Záznam {location_name} byl přidán.")

    

    # Tlačítka pro úpravu a smazání záznamu
    def update_location():
        selected_item = tree.selection()
        if selected_item:
            values = tuple(entries[field].get() for field in fields)
            item_id = tree.item(selected_item, "values")[0]

            # Aktualizace záznamu v load_locations
            cursor_locations.execute("""
                UPDATE load_locations
                SET location_name=?, street=?, postal_code=?, city=?, working_hours_from=?, working_hours_to=?, 
                    contact_person=?, mobile=?, email=?, note=?
                WHERE location_name=?
            """, values + (item_id,))

            # Aktualizace záznamu v unload_locations
            cursor_locations.execute("""
                UPDATE unload_locations
                SET location_name=?, street=?, postal_code=?, city=?, working_hours_from=?, working_hours_to=?, 
                    contact_person=?, mobile=?, email=?, note=?
                WHERE location_name=?
            """, values + (item_id,))

            conn_locations.commit()

            # Aktualizace záznamu v Treeview
            tree.item(selected_item, values=values)

            messagebox.showinfo("Úspěch", f"Záznam {item_id} byl aktualizovan.")

    

    def delete_location():
        selected_item = tree.selection()
        if selected_item:
            confirm = messagebox.askyesno("Potvrzení", "Opravdu chcete smazat vybraný záznam?")
            if confirm:
                item_id = tree.item(selected_item, "values")[0]
                
                # Smazání záznamu v load_locations
                cursor_locations.execute("DELETE FROM load_locations WHERE location_name=?", (item_id,))
                
                # Smazání záznamu v unload_locations
                cursor_locations.execute("DELETE FROM unload_locations WHERE location_name=?", (item_id,))
                
                conn_locations.commit()
                
                # Odstranění položky z Treeview
                tree.delete(selected_item)
                messagebox.showinfo("Úspěch", f"Záznam {item_id} byl smazán.")

    # Tlačítka
    add_button = tk.Button(button_frame, text="Přidat místo", command=add_location)
    add_button.grid(row=0, column=0, padx=5)

    update_button = tk.Button(button_frame, text="Upravit záznam", command=update_location)
    update_button.grid(row=0, column=1, padx=5)

    delete_button = tk.Button(button_frame, text="Vymazat záznam", command=delete_location)
    delete_button.grid(row=0, column=2, padx=5)

    close_button = tk.Button(button_frame, text="Zavřít okno", command=window.destroy)
    close_button.grid(row=0, column=3, padx=5)


    # Rámec pro Treeview a posuvník
    tree_frame = tk.Frame(window)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    # Vytvoření Treeview
    tree = ttk.Treeview(tree_frame, columns=("location_name", "street", "postal_code", "city", 
                                             "working_hours_from", "working_hours_to", 
                                             "contact_person", "mobile", "email", "note"), show='headings')

    # Nastavení šířek sloupců a povolení změny šířky
    tree.column("location_name", width=100, anchor='w', stretch=True)
    tree.column("street", width=100, anchor='w', stretch=True)
    tree.column("postal_code", width=50, anchor='w', stretch=True)
    tree.column("city", width=100, anchor='w', stretch=True)
    tree.column("working_hours_from", width=40, anchor='w', stretch=True)
    tree.column("working_hours_to", width=40, anchor='w', stretch=True)
    tree.column("contact_person", width=100, anchor='w', stretch=True)
    tree.column("mobile", width=100, anchor='w', stretch=True)
    tree.column("email", width=150, anchor='w', stretch=True)
    tree.column("note", width=200, anchor='w', stretch=True)

    # Nadpisy pro každý sloupec
    tree.heading("location_name", text="Název")
    tree.heading("street", text="Ulice")
    tree.heading("postal_code", text="PSČ")
    tree.heading("city", text="Město")
    tree.heading("working_hours_from", text="Prac. doba od")
    tree.heading("working_hours_to", text="Prac. doba do")
    tree.heading("contact_person", text="Kontaktní osoba")
    tree.heading("mobile", text="Mobil")
    tree.heading("email", text="Email")
    tree.heading("note", text="Poznámka")

    # Přidání Treeview do rámce
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Vytvoření posuvníku
    scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    # Umístění posuvníku vedle Treeview
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Vložení dat z load_locations
    for row in load_data:
        tree.insert("", "end", values=row)

    # Vložení dat z unload_locations
    for row in unload_data:
        tree.insert("", "end", values=row)
    
    # Funkce pro načtení vybraného řádku z Treeview do formuláře
    def load_from_treeview(event):
        selected_item = tree.selection()
        if selected_item:
            values = tree.item(selected_item, "values")
            for i, field in enumerate(fields):
                entries[field].delete(0, tk.END)
                entries[field].insert(0, values[i])

    tree.bind("<<TreeviewSelect>>", load_from_treeview)

    window.mainloop()

# Volání funkce pro zobrazení dat
show_locations()
