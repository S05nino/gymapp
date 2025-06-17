import tkinter as tk
from tkinter import messagebox
from db.database import connessione

class GestioneSchedeScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        tk.Label(self.frame, text="Gestione Schede Attive", font=("Arial", 16)).pack(pady=10)

        self.check_vars = []
        with connessione() as conn:
            c = conn.cursor()
            c.execute("SELECT id, nome, attiva FROM schede")
            self.schede = c.fetchall()

        for scheda_id, nome, attiva in self.schede:
            var = tk.IntVar(value=attiva)
            chk = tk.Checkbutton(self.frame, text=nome, variable=var)
            chk.pack(anchor="w")
            self.check_vars.append((scheda_id, var))

        tk.Button(self.frame, text="💾 Salva", command=self.salva).pack(pady=10)
        tk.Button(self.frame, text="🏠 Torna alla Home", command=self.torna_home).pack()

    def salva(self):
        with connessione() as conn:
            c = conn.cursor()
            for scheda_id, var in self.check_vars:
                c.execute("UPDATE schede SET attiva = ? WHERE id = ?", (var.get(), scheda_id))
            conn.commit()
        messagebox.showinfo("Salvato", "Schede attive aggiornate.")

    def torna_home(self):
        self.frame.destroy()
        from gui.home import HomeScreen
        HomeScreen(self.root)
