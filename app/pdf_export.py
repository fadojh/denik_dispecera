# Export do PDF
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from tkinter import messagebox
from datetime import datetime
import os
import locale


# Nastavení české lokalizace
locale.setlocale(locale.LC_ALL, 'cs_CZ.UTF-8')

def register_fonts():
    font_path = os.path.join('other', 'DejaVuSans.ttf')
    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
    
# Export do PDF
def create_pdf(tree):
    try:
        # Registrace fontů
        register_fonts()

        # Vytvoření složky, pokud neexistuje
        export_dir = "export_obj"
        os.makedirs(export_dir, exist_ok=True)

        # Vytvoření jedinečného názvu souboru
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_file = os.path.join(export_dir, f"orders_report_{timestamp}.pdf")

        # Vytvoření plátna s orientací na šířku
        c = canvas.Canvas(pdf_file, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Definování okrajů
        left_margin = 10
        top_margin = 10
        bottom_margin = 10

        # Nastavení nadpisu PDF
        c.setFont("DejaVuSans", 10)
        c.drawString(left_margin, height - top_margin, "Seznam objednávek")

        # Počáteční Y pozice pro data
        y = height - top_margin - 40  # Adjust for title height
        
        # Počáteční X pozice pro data
        x_start = left_margin

        # Sloupce v Treeview a jejich šířky
        columns = ["číslo objednávky", "zpmtr", "datum nakládky", "datum vykládky", "nakládka", "vykládka", "palet", "váha", "spz", "cena", "dopravce", "poznámka"]
        column_widths = [80, 60, 80, 80, 60, 60, 30, 60, 80, 30, 60, 158]  # Šířky sloupců

        # Hlavičky tabulky v PDF
        c.setFont("DejaVuSans", 8)
        for col_idx, col in enumerate(columns):
            x_pos = x_start + sum(column_widths[:col_idx])
            c.drawString(x_pos, y, col)
            # Vykreslení obdélníku pro hlavičku
            c.rect(x_pos, y - 3, column_widths[col_idx], 10)  # (x, y, width, height)
        
        y -= 20  # Posun dolů pro data

        # Data z Treeview
        for row in tree.get_children():
            if y < bottom_margin:  # Pokud se blíží konec stránky, vytvořit novou
                c.showPage()
                y = height - top_margin - 40
                # Znovu vykreslit hlavičky na nové stránce
                c.setFont("DejaVuSans", 8)
                for col_idx, col in enumerate(columns):
                    x_pos = x_start + sum(column_widths[:col_idx])
                    c.drawString(x_pos, y, col)
                    c.rect(x_pos, y - 3, column_widths[col_idx], 10)
                y -= 20

            values = tree.item(row)["values"]
            c.setFont("DejaVuSans", 8)
            for col_idx, value in enumerate(values):
                x_pos = x_start + sum(column_widths[:col_idx])
                c.drawString(x_pos, y, str(value))
                # Vykreslení obdélníku pro buňku
                c.rect(x_pos, y - 3, column_widths[col_idx], 10)

            y -= 20  # Posun dolů pro další řádek

        # Uložit soubor
        c.save()

        messagebox.showinfo("Hotovo", f"PDF bylo vytvořeno: {pdf_file}")

        # Otevřít PDF
        if os.name == 'posix':  # Unix-based (Linux, macOS)
            subprocess.call(['open', pdf_file])
        elif os.name == 'nt':  # Windows
            os.startfile(pdf_file)
    except Exception as e:
        messagebox.showerror("Chyba", f"Chyba při vytváření PDF: {e}")