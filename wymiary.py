import tkinter as tk


root = tk.Tk()
x = root.winfo_screenwidth()/1920
y = root.winfo_screenheight()/1080
min=min(x,y)
max=max(x,y)