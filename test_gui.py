import tkinter as tk
from tkinter import messagebox

# Simple GUI test
root = tk.Tk()
root.title("Test GUI")
root.geometry("400x300")

label = tk.Label(root, text="GUI Test - If you see this, tkinter works!")
label.pack(pady=20)

button = tk.Button(root, text="Click Me", command=lambda: messagebox.showinfo("Test", "GUI is working!"))
button.pack(pady=10)

root.mainloop()
