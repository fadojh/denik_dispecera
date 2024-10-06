import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import sys
import json
import locale
from tkinter import Menu
import os

# SQLite setup (dopravci)
try:
    conn_carriers = sqlite3.connect(os.path.join('db', 'carriers.db'))
    cursor_carriers = conn_carriers.cursor()
    print("Připojeno k databázi.")
except sqlite3.Error as e:
    print(f"Chyba při připojování k databázi: {e}")

# Pokus o přidání nových sloupců, pokud ještě neexistují
try:
    cursor_carriers.execute("ALTER TABLE carriers ADD COLUMN street TEXT")
    cursor_carriers.execute("ALTER TABLE carriers ADD COLUMN city TEXT")
    cursor_carriers.execute("ALTER TABLE carriers ADD COLUMN postal_code TEXT")
    cursor_carriers.execute("ALTER TABLE carriers ADD COLUMN ico TEXT")
    cursor_carriers.execute("ALTER TABLE carriers ADD COLUMN dic TEXT")
    cursor_carriers.execute("ALTER TABLE carriers ADD COLUMN dispatcher_name TEXT")
    cursor_carriers.execute("ALTER TABLE carriers ADD COLUMN mobile TEXT")
    cursor_carriers.execute("ALTER TABLE carriers ADD COLUMN email TEXT")
    cursor_carriers.execute("ALTER TABLE carriers ADD COLUMN pallet_exchange TEXT")
    cursor_carriers.execute("ALTER TABLE carriers ADD COLUMN notes TEXT")
except sqlite3.OperationalError:
    # Pokud sloupce již existují, chyba bude ignorována
    pass

conn_carriers.commit()

# Nastavení GUI
root = tk.Tk()
root.title("Adresář dopravců")

# Výchozí rozměry nového okna
default_width = 1650
default_height = 480

# Nastavení české lokalizace
locale.setlocale(locale.LC_ALL, 'cs_CZ.UTF-8')

# Funkce pro přidání dopravce
def add_carrier():
    carrier_name = entry_carrier_name.get().strip()
    street = entry_street.get().strip()
    city = entry_city.get().strip()
    postal_code = entry_postal_code.get().strip()
    ico = entry_ico.get().strip()
    dic = entry_dic.get().strip()
    dispatcher_name = entry_dispatcher_name.get().strip()
    mobile = entry_mobile.get().strip()
    email = entry_email.get().strip()
    pallet_exchange = pallet_exchange_var.get().strip()
    notes = entry_notes.get("1.0", tk.END).strip()

    if not carrier_name:
        messagebox.showwarning("Varování", "Zadejte název dopravce.")
        return

    try:
        cursor_carriers.execute('''
            INSERT INTO carriers (carrier_name, street, city, postal_code, ico, dic, dispatcher_name, mobile, email, pallet_exchange, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (carrier_name, street, city, postal_code, ico, dic, dispatcher_name, mobile, email, pallet_exchange, notes))
        conn_carriers.commit()
        messagebox.showinfo("Úspěch", f"Dopravce '{carrier_name}' byl přidán.")
        clear_form()
        display_carriers()
    except sqlite3.IntegrityError:
        messagebox.showerror("Chyba", "Dopravce již existuje.")


# Funkce pro úpravu dopravce
def update_carrier():
    carrier_name = entry_carrier_name.get().strip()
    street = entry_street.get().strip()
    city = entry_city.get().strip()
    postal_code = entry_postal_code.get().strip()
    ico = entry_ico.get().strip()
    dic = entry_dic.get().strip()
    dispatcher_name = entry_dispatcher_name.get().strip()
    mobile = entry_mobile.get().strip()
    email = entry_email.get().strip()
    notes = entry_notes.get("1.0", tk.END).strip()
    pallet_exchange = pallet_exchange_var.get().strip()  # Přidáno načtení hodnoty Výměna palet

    if not carrier_name:
        messagebox.showwarning("Varování", "Zadejte název dopravce.")
        return

    try:
        cursor_carriers.execute('''
            UPDATE carriers SET street=?, city=?, postal_code=?, ico=?, dic=?, dispatcher_name=?, mobile=?, email=?, pallet_exchange=?, notes=?
            WHERE carrier_name=?
        ''', (street, city, postal_code, ico, dic, dispatcher_name, mobile, email, pallet_exchange, notes, carrier_name))
        conn_carriers.commit()
        messagebox.showinfo("Úspěch", f"Dopravce '{carrier_name}' byl aktualizován.")
        clear_form()
        display_carriers()
        is_editing.set(False)
    except sqlite3.IntegrityError:
        messagebox.showerror("Chyba", "Dopravce již existuje.")

def clear_form():
    entry_carrier_name.delete(0, tk.END)
    entry_street.delete(0, tk.END)
    entry_city.delete(0, tk.END)
    entry_postal_code.delete(0, tk.END)
    entry_ico.delete(0, tk.END)
    entry_dic.delete(0, tk.END)
    entry_dispatcher_name.delete(0, tk.END)
    entry_mobile.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    entry_notes.delete("1.0", tk.END)

    # Aktualizace zobrazení v Treeview
    display_carriers()

def load_selected_carrier(event):
    selected_item = tree.selection()
    if not selected_item:
        return
    selected_item = selected_item[0]
    values = tree.item(selected_item, 'values')

    entry_carrier_name.delete(0, tk.END)
    entry_carrier_name.insert(0, values[0])

    entry_street.delete(0, tk.END)
    entry_street.insert(0, values[1])

    entry_city.delete(0, tk.END)
    entry_city.insert(0, values[2])

    entry_postal_code.delete(0, tk.END)
    entry_postal_code.insert(0, values[3])

    entry_ico.delete(0, tk.END)
    entry_ico.insert(0, values[4])

    entry_dic.delete(0, tk.END)
    entry_dic.insert(0, values[5])

    entry_dispatcher_name.delete(0, tk.END)
    entry_dispatcher_name.insert(0, values[6])

    entry_mobile.delete(0, tk.END)
    entry_mobile.insert(0, values[7])

    entry_email.delete(0, tk.END)
    entry_email.insert(0, values[8])

    pallet_exchange_var.set(values[9])  # Nastaví hodnotu pro Výměna palet 

    entry_notes.delete("1.0", tk.END)  # Vymaže celý text od začátku
    entry_notes.insert("1.0", values[10])  # Vloží text na začátek


def delete_carrier():
    selected_item = tree.selection()[0]
    carrier_name = tree.item(selected_item, 'values')[0]
    result = messagebox.askquestion("Smazat", f"Opravdu chcete smazat dopravce '{carrier_name}'?", icon='warning')
    if result == 'yes':
        cursor_carriers.execute("DELETE FROM carriers WHERE carrier_name=?", (carrier_name,))
        conn_carriers.commit()
        clear_form()
        display_carriers()

def display_carriers():
    # Vymazat stávající data v Treeview
    for row in tree.get_children():
        tree.delete(row)

    cursor_carriers.execute("SELECT * FROM carriers ORDER BY carrier_name ASC LIMIT 20")
    carriers = cursor_carriers.fetchall()
    
 # Seřadit výsledky podle české abecedy
    carriers.sort(key=lambda c: locale.strxfrm(c[0]))  # Předpokládám, že carrier_name je první sloupec (index 0)

    # Přidat data do Treeview
    for carrier in carriers:
        tree.insert("", tk.END, values=carrier)
    

# Funkce pro vyhledávání dopravce
def search_carrier():
    def execute_search():
        search_name = entry_search.get().strip().lower()

        if not search_name:
            # Zde pouze vymažeme pole a vrátíme fokus, bez varování
            entry_search.delete(0, tk.END)  # Vymazání obsahu vstupního pole
            entry_search.focus_set()  # Vrátí fokus na vstupní pole pro další hledání
            return

        cursor_carriers.execute("SELECT * FROM carriers WHERE lower(carrier_name) LIKE ?", (search_name + '%',))  # Použití LIKE
        result = cursor_carriers.fetchone()

        if result:
            search_window.destroy()  # Zavření vyhledávacího okna
            # Vymazání stávajících dat v Treeview
            for row in tree.get_children():
                tree.delete(row)
            # Přidání nalezeného dopravce do Treeview
            tree.insert("", tk.END, values=result)
        else:
            # Získání pozice vyhledávacího okna
            x = search_window.winfo_x()
            y = search_window.winfo_y()

            # Vytvoření chybového okna
            error_window = tk.Toplevel(root)
            error_window.title("Chyba")
            error_window.geometry(f"300x100+{x}+{y}")  # Nastavení pozice a velikosti
            tk.Label(error_window, text="Dopravce není v databázi.").pack(pady=20)
            tk.Button(error_window, text="OK", command=lambda: close_error_window(error_window)).pack(pady=5)
            
            # Aktivace chybového okna
            error_window.focus_force()  # Zajištění, že chybové okno je aktivní
            
            # Přidání funkce pro zavření okna při stisknutí klávesy Enter
            error_window.bind("<Return>", lambda event: close_error_window(error_window))


            entry_search.delete(0, tk.END)  # Vymazání obsahu vstupního pole
            entry_search.focus_set()  # Vrátí fokus na vstupní pole pro další hledání

    def close_error_window(window):
        window.destroy()  # Zavření chybového okna

    # Nové okno pro vyhledávání
    search_window = tk.Toplevel(root)
    search_window.title("Hledat dopravce")
    
    # Nastavení velikosti nového okna
    window_width = 300
    window_height = 150

    # Získání rozměrů a pozice hlavního okna
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    # Výpočet středu hlavního okna
    position_x = root_x + (root_width // 2) - (window_width // 2)
    position_y = root_y + (root_height // 2) - (window_height // 2)

    # Nastavení pozice nového okna uprostřed hlavního okna
    search_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
    
    tk.Label(search_window, text="Název dopravce:").pack(padx=10, pady=10)
    entry_search = tk.Entry(search_window)
    entry_search.pack(padx=10, pady=10)

    # Nastavení zaměření na vstupní pole po otevření okna
    entry_search.focus_set()

    # Bindování klávesy Enter pro spuštění funkce execute_search
    entry_search.bind("<Return>", lambda event: execute_search())

    tk.Button(search_window, text="Hledat", command=execute_search).pack(pady=10)

# Funkce pro ukončení aplikace
def close_application():
    root.destroy()

# Indikátor, zda probíhá úprava záznamu
is_editing = tk.BooleanVar(value=False)


# Hlavní rámec pro celé okno
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Rozdělení hlavního rámce na levý a pravý rámec
left_frame = tk.Frame(main_frame, width=700)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right_frame = tk.Frame(main_frame, width=900, bg="lightblue")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Přidání Treeview do pravého rámce
columns = ("Název", "Ulice", "Město", "PSČ", "IČO", "DIČ", "Jméno dispečera", "Mobil", "Email", "Výměna palet", "Poznámka")
tree = ttk.Treeview(right_frame, columns=columns, show='headings')

# Nastavení sloupců Treeview
column_widths = [150, 150, 100, 80, 80, 80, 100, 100, 200, 80, 200]
for col, width in zip(columns, column_widths):
    tree.heading(col, text=col.replace('_', ' ').capitalize())
    tree.column(col, width=width)

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Přidání posuvníku k Treeview
vsb = tk.Scrollbar(right_frame, orient="vertical", command=tree.yview)
vsb.pack(side='right', fill='y')
tree.configure(yscrollcommand=vsb.set)

# Bind události pro výběr řádku v Treeview
tree.bind("<ButtonRelease-1>", load_selected_carrier)

# Přidání formuláře do levého rámce
form_frame = tk.Frame(left_frame)
form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

tk.Label(form_frame, text="Název dopravce:").grid(row=0, column=0, sticky="w", padx=0, pady=5)
entry_carrier_name = tk.Entry(form_frame)
entry_carrier_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Ulice:").grid(row=1, column=0, sticky="w", padx=0, pady=5)
entry_street = tk.Entry(form_frame)
entry_street.grid(row=1, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Město:").grid(row=2, column=0, sticky="w", padx=0, pady=5)
entry_city = tk.Entry(form_frame)
entry_city.grid(row=2, column=1, padx=5, pady=5)

tk.Label(form_frame, text="PSČ:").grid(row=3, column=0, sticky="w", padx=0, pady=5)
entry_postal_code = tk.Entry(form_frame)
entry_postal_code.grid(row=3, column=1, padx=5, pady=5)

tk.Label(form_frame, text="IČO:").grid(row=4, column=0, sticky="w", padx=0, pady=5)
entry_ico = tk.Entry(form_frame)
entry_ico.grid(row=4, column=1, padx=5, pady=5)

tk.Label(form_frame, text="DIČ:").grid(row=5, column=0, sticky="w", padx=0, pady=5)
entry_dic = tk.Entry(form_frame)
entry_dic.grid(row=5, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Jméno dispečera:").grid(row=6, column=0, sticky="w", padx=0, pady=5)
entry_dispatcher_name = tk.Entry(form_frame)
entry_dispatcher_name.grid(row=6, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Mobil:").grid(row=7, column=0, sticky="w", padx=0, pady=5)
entry_mobile = tk.Entry(form_frame)
entry_mobile.grid(row=7, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Email:").grid(row=8, column=0, sticky="w", padx=0, pady=5)
entry_email = tk.Entry(form_frame)
entry_email.grid(row=8, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Výměna palet:").grid(row=9, column=0, sticky="w", padx=0, pady=5)
pallet_exchange_var = tk.StringVar(value="Ne")
pallet_exchange_menu = ttk.Combobox(form_frame, textvariable=pallet_exchange_var, values=["Ano", "Ne"], width=5)
pallet_exchange_menu.grid(row=9, column=1, sticky="w", padx=19, pady=5)

tk.Label(form_frame, text="Poznámka:").grid(row=10, column=0, sticky="w", padx=0, pady=5)
entry_notes = tk.Text(form_frame, height=3, width=15)
entry_notes.grid(row=10, column=1, padx=5, pady=5)

# Přidání tlačítek do levého rámce
button_frame = tk.Frame(form_frame)
button_frame.grid(row=11, columnspan=2, pady=5, padx=5)

tk.Button(button_frame, text="Přidat", command=add_carrier).grid(row=0, column=0,sticky="w", padx=0)
tk.Button(button_frame, text="Upravit", command=update_carrier).grid(row=0, column=1,sticky="w", padx=0)
tk.Button(button_frame, text="Vyčistit formulář", command=clear_form).grid(row=0, column=1, sticky="w", padx=62)
tk.Button(button_frame, text="Hledat", command=search_carrier).grid(row=1, column=1, padx=0)
tk.Button(button_frame, text="Vymazat", command=delete_carrier).grid(row=1, column=0, sticky="w", padx=0, pady=10)
tk.Button(button_frame, text="Zavřít okno", command=root.destroy).grid(row=1, column=1, padx=10, sticky="w", pady=10)



# Načtení dat do Treeview
display_carriers()


# Načtení pozice hlavního okna ze souboru
try:
    with open("window_position.json", "r") as f:
        position = json.load(f)
        main_x = position["x"]
        main_y = position["y"]
        main_width = position["width"]
        main_height = position["height"]

        # Výpočet pozice nového okna
        new_window_x = main_x + (main_width - default_width) // 2
        new_window_y = main_y + (main_height - default_height) // 2
        root.geometry(f"{default_width}x{default_height}+{new_window_x}+{new_window_y}")

except FileNotFoundError:
    print("Soubor s pozicí okna nebyl nalezen. Používá se výchozí umístění.")
    root.geometry(f"{default_width}x{default_height}")

# Vytvoření horní menu
menu_bar = Menu(root)

# Vytvoření nabídky "Soubor"
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Ukončit", command=root.quit)
menu_bar.add_cascade(label="Soubor", menu=file_menu)

# Vytvoření nabídky "Nástroje"
tools_menu = Menu(menu_bar, tearoff=0)
tools_menu.add_command(label="Hledat dopravce", command=search_carrier)
tools_menu.add_command(label="Vyčistit formulář", command=clear_form)
tools_menu.add_command(label="Vymazat dopravce", command=delete_carrier)
menu_bar.add_cascade(label="Nástroje", menu=tools_menu)


# Připojení menu k hlavnímu okno
root.config(menu=menu_bar)



root.mainloop()
