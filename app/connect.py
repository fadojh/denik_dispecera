import sqlite3
import os

# Vytvoření složky "db", pokud neexistuje
if not os.path.exists('db'):
    os.makedirs('db')

# Připojení k SQLite databázi ve složce "db"
try:
    conn = sqlite3.connect(os.path.join('db', 'freight_orders.db'))
    cursor = conn.cursor()
    print("Připojeno k databázi freight_orders.")
except sqlite3.Error as e:
    print(f"Chyba při připojování k databázi: {e}")


# SQLite setup (dopravci)
try:
    conn_carriers = sqlite3.connect(os.path.join('db', 'carriers.db'))
    cursor_carriers = conn_carriers.cursor()
    print("Připojeno k databázi dopravci.")
except sqlite3.Error as e:
    print(f"Chyba při připojování k databázi: {e}")

# Create carriers table if not exists
cursor_carriers.execute('''
    CREATE TABLE IF NOT EXISTS carriers (
        carrier_name TEXT PRIMARY KEY
    )
''')
conn_carriers.commit()

# SQLite setup (nakládky a vykládky)
try:
    conn_locations = sqlite3.connect(os.path.join('db', 'locations.db'))
    cursor_locations = conn_locations.cursor()
    print("Připojeno k databázi místa.")
except sqlite3.Error as e:
    print(f"Chyba při připojování k databázi: {e}")

# Vytvoření tabulek pro nakládku a vykládku s dalšími sloupci, pokud neexistují
cursor_locations.execute('''
    CREATE TABLE IF NOT EXISTS load_locations (
        location_name TEXT PRIMARY KEY,
        street TEXT,
        postal_code TEXT,
        city TEXT KEY,
        working_hours_from TEXT,
        working_hours_to TEXT,
        contact_person TEXT,
        mobile TEXT,
        email TEXT,
        note TEXT
    )
''')

cursor_locations.execute('''
    CREATE TABLE IF NOT EXISTS unload_locations (
        location_name TEXT PRIMARY KEY,
        street TEXT,
        postal_code TEXT,
        city TEXT,
        working_hours_from TEXT,
        working_hours_to TEXT,
        contact_person TEXT,
        mobile TEXT,
        email TEXT,
        note TEXT
    )
''')

conn_locations.commit()

# Create the table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_number TEXT PRIMARY KEY,
        zpmtr TEXT,
        load_date TEXT,
        unload_date TEXT,
        load_location TEXT,
        unload_location TEXT,
        pallets INTEGER,
        weight REAL,
        spz TEXT,
        price REAL,
        carrier TEXT,
        note TEXT
    )
''')
conn.commit()

# Column mapping for the GUI
column_mapping = {
    "order_number": "Číslo objednávky",
    "zpmtr": "ZPMTR",
    "load_location": "Nakládka",
    "unload_location": "Vykládka",
    "carrier": "Dopravce"
}
