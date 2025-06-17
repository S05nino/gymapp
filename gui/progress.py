import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from db.database import connessione

class ProgressScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="📊 Visualizza Progressi", font=("Arial", 16)).pack(pady=10)

        # Carica tutti i muscoli unici
        with connessione() as conn:
            c = conn.cursor()
            c.execute("SELECT DISTINCT muscolo FROM esercizi ORDER BY muscolo")
            self.muscoli = [r[0] for r in c.fetchall()]

        self.selected_muscolo = tk.StringVar()
        self.selected_esercizio = tk.StringVar()

        # Menu muscolo
        tk.Label(self.frame, text="Scegli muscolo:").pack()
        self.muscolo_menu = tk.OptionMenu(self.frame, self.selected_muscolo, *self.muscoli, command=self.aggiorna_esercizi)
        self.muscolo_menu.pack(pady=5)

        # Menu esercizi (popolato dopo scelta muscolo)
        tk.Label(self.frame, text="Scegli esercizio:").pack()
        self.esercizio_menu = tk.OptionMenu(self.frame, self.selected_esercizio, "")
        self.esercizio_menu.pack(pady=5)

        self.esercizi_by_nome = {}

        # Pulsante grafico
        tk.Button(self.frame, text="📈 Mostra Andamento", command=self.mostra_grafico).pack(pady=10)

        # Pulsante per tornare alla home durante allenamento
        tk.Button(self.frame, text="🏠 Torna alla Home", command=self.torna_home).pack(pady=10)

    def torna_home(self):
        self.frame.destroy()
        from gui.home import HomeScreen
        HomeScreen(self.root)
    
    def aggiorna_esercizi(self, muscolo):
        # Recupera esercizi relativi a quel muscolo
        with connessione() as conn:
            c = conn.cursor()
            c.execute("SELECT id, nome FROM esercizi WHERE muscolo = ? ORDER BY nome", (muscolo,))
            esercizi = c.fetchall()

        # Popola dizionario e menu
        self.esercizi_by_nome = {nome: id for id, nome in esercizi}

        menu = self.esercizio_menu["menu"]
        menu.delete(0, "end")

        for nome in self.esercizi_by_nome:
            menu.add_command(label=nome, command=lambda value=nome: self.selected_esercizio.set(value))

        # Seleziona il primo esercizio
        if esercizi:
            primo_nome = esercizi[0][1]
            self.selected_esercizio.set(primo_nome)

    def mostra_grafico(self):
        nome_es = self.selected_esercizio.get()
        if not nome_es:
            messagebox.showwarning("Attenzione", "Seleziona un esercizio.")
            return

        esercizio_id = self.esercizi_by_nome.get(nome_es)

        with connessione() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT data, peso_utilizzato
                FROM progressi
                WHERE esercizio_id = ?
                ORDER BY data
            """, (esercizio_id,))
            dati = c.fetchall()

        if not dati:
            messagebox.showinfo("Nessun dato", f"Nessun progresso registrato per {nome_es}")
            return

        date = [d[0] for d in dati]
        peso = [d[1] for d in dati]

        plt.figure(figsize=(8, 5))
        plt.plot(date, peso, marker='o', linestyle='-', color='blue')
        plt.title(f"Progresso peso - {nome_es}")
        plt.xlabel("Data")
        plt.ylabel("Peso utilizzato (kg)")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
