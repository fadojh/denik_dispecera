from tkinter import Menu

def create_menu(root):
    menubar = Menu(root)
    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open", command=lambda: print("Open"))
    file_menu.add_command(label="Save", command=lambda: print("Save"))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menubar)