import tkinter as tk

try:
    root = tk.Tk()
    root.title("Tkinter Test")
    root.geometry("250x100")
    tk.Label(root, text="✅ Tkinter düzgün çalışıyor!").pack(pady=20)
    root.mainloop()
except tk.TclError as e:
    print("❌ Tkinter hatası:", e)
