import tkinter as tk
from gui.home import HomeScreen
from db.database import crea_tabelle

if __name__ == "__main__":
    crea_tabelle()  # crea tabelle se non esistono

    root = tk.Tk()
    root.title("Gym Tracker")
    root.geometry("600x400")

    app = HomeScreen(root)
    root.mainloop()
