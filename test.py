import customtkinter

def button_callback():
    print("Button Clicked")


app = customtkinter.CTk()
app.title("CustomTkinter App")
app.geometry("500x500")

button = customtkinter.CTkButton(app, text="CTkButton", command=button_callback)
button.grid(row=0, column=0, padx=20, pady=20)


app.mainloop()