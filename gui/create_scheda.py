import tkinter as tk
from tkinter import messagebox
from db.database import connessione

class CreateSchedaScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.esercizi = []

        # Titolo
        tk.Label(self.frame, text="Crea Nuova Scheda", font=("Arial", 18)).pack(pady=10)

        # Nome scheda
        tk.Label(self.frame, text="Nome scheda:").pack()
        self.entry_nome = tk.Entry(self.frame)
        self.entry_nome.pack()

        # Esercizio - Nome
        tk.Label(self.frame, text="Nome esercizio:").pack()
        self.entry_es_nome = tk.Entry(self.frame)
        self.entry_es_nome.pack()

        # Muscolo
        tk.Label(self.frame, text="Muscolo target:").pack()
        self.entry_es_muscolo = tk.Entry(self.frame)
        self.entry_es_muscolo.pack()

        # Serie, ripetizioni, peso
        self.entry_serie = self._labeled_entry("Serie")
        self.entry_ripetizioni = self._labeled_entry("Ripetizioni")
        self.entry_peso = self._labeled_entry("Peso target (kg)")

        # Pulsanti
        tk.Button(self.frame, text="➕ Aggiungi esercizio", command=self.aggiungi_esercizio).pack(pady=5)
        tk.Button(self.frame, text="💾 Salva scheda", command=self.salva_scheda).pack(pady=10)

        # Lista esercizi aggiunti
        self.label_elenco = tk.Label(self.frame, text="Esercizi aggiunti: 0")
        self.label_elenco.pack(pady=5)

    def _labeled_entry(self, label):
        tk.Label(self.frame, text=label + ":").pack()
        entry = tk.Entry(self.frame)
        entry.pack()
        return entry

    def aggiungi_esercizio(self):
        nome = self.entry_es_nome.get()
        muscolo = self.entry_es_muscolo.get()
        serie = self.entry_serie.get()
        rip = self.entry_ripetizioni.get()
        peso = self.entry_peso.get()

        if not all([nome, muscolo, serie, rip, peso]):
            messagebox.showwarning("Attenzione", "Compila tutti i campi per aggiungere un esercizio.")
            return

        self.esercizi.append({
            "nome": nome,
            "muscolo": muscolo,
            "serie": int(serie),
            "ripetizioni": int(rip),
            "peso": float(peso)
        })
        self.label_elenco.config(text=f"Esercizi aggiunti: {len(self.esercizi)}")

        # Pulisci i campi
        self.entry_es_nome.delete(0, tk.END)
        self.entry_es_muscolo.delete(0, tk.END)
        self.entry_serie.delete(0, tk.END)
        self.entry_ripetizioni.delete(0, tk.END)
        self.entry_peso.delete(0, tk.END)

    def salva_scheda(self):
        nome_scheda = self.entry_nome.get()
        if not nome_scheda:
            messagebox.showwarning("Errore", "Inserisci il nome della scheda.")
            return

        if not self.esercizi:
            messagebox.showwarning("Errore", "Aggiungi almeno un esercizio.")
            return

        with connessione() as conn:
            c = conn.cursor()

            # Inserisci la scheda
            c.execute("INSERT INTO schede (nome) VALUES (?)", (nome_scheda,))
            scheda_id = c.lastrowid

            for es in self.esercizi:
                # Inserisci esercizio se non esiste
                c.execute("SELECT id FROM esercizi WHERE nome = ? AND muscolo = ?", (es["nome"], es["muscolo"]))
                result = c.fetchone()
                if result:
                    esercizio_id = result[0]
                else:
                    c.execute("INSERT INTO esercizi (nome, muscolo) VALUES (?, ?)", (es["nome"], es["muscolo"]))
                    esercizio_id = c.lastrowid

                # Inserisci nella tabella scheda_esercizi
                c.execute("""
                    INSERT INTO scheda_esercizi (scheda_id, esercizio_id, serie, ripetizioni, peso_target)
                    VALUES (?, ?, ?, ?, ?)
                """, (scheda_id, esercizio_id, es["serie"], es["ripetizioni"], es["peso"]))

            conn.commit()

        messagebox.showinfo("Successo", f"Scheda '{nome_scheda}' salvata con {len(self.esercizi)} esercizi.")
        self.frame.destroy()
        from gui.home import HomeScreen
        HomeScreen(self.root)
