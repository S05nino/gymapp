import tkinter as tk
from tkinter import messagebox
from db.database import connessione
from datetime import datetime

class WorkoutScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Allenamento", font=("Arial", 16)).pack(pady=10)

        with connessione() as conn:
            c = conn.cursor()
            c.execute("SELECT id, nome FROM schede")
            self.schede = c.fetchall()

        if not self.schede:
            tk.Label(self.frame, text="Nessuna scheda trovata. Crea una scheda prima!").pack(pady=20)
            return

        self.scheda_vars = {}
        tk.Label(self.frame, text="Seleziona le schede attive:").pack()

        for scheda_id, nome in self.schede:
            var = tk.IntVar()
            self.scheda_vars[scheda_id] = var
            cb = tk.Checkbutton(self.frame, text=nome, variable=var)
            cb.pack(anchor="w", padx=20)

        tk.Button(self.frame, text="💾 Salva schede attive", command=self.salva_schede_attive).pack(pady=10)
        tk.Button(self.frame, text="▶️ Inizia allenamento", command=self.inizia_allenamento_con_scheda_in_rotazione).pack(pady=5)
        tk.Button(self.frame, text="🏠 Torna alla Home", command=self.torna_home).pack(pady=20)

    def salva_schede_attive(self):
        with connessione() as conn:
            c = conn.cursor()
            c.execute("UPDATE schede SET attiva = 0")
            for scheda_id, var in self.scheda_vars.items():
                if var.get() == 1:
                    c.execute("UPDATE schede SET attiva = 1 WHERE id = ?", (scheda_id,))
            conn.commit()
        messagebox.showinfo("Salvato", "Schede attive aggiornate.")

    def inizia_allenamento_con_scheda_in_rotazione(self):
        with connessione() as conn:
            c = conn.cursor()
            c.execute("SELECT id, nome FROM schede WHERE attiva = 1 ORDER BY id")
            schede_attive = c.fetchall()

            if not schede_attive:
                messagebox.showwarning("Attenzione", "Nessuna scheda attiva selezionata.")
                return

            c.execute("SELECT valore FROM impostazioni WHERE chiave = 'ultima_scheda_usata'")
            ultima = c.fetchone()
            ultima_id = int(ultima[0]) if ultima else None

            prossima = None
            for i, (sid, _) in enumerate(schede_attive):
                if sid == ultima_id:
                    prossima = schede_attive[(i + 1) % len(schede_attive)]
                    break

            if not prossima:
                prossima = schede_attive[0]

            if messagebox.askyesno("Allenamento", f"Oggi tocca a: {prossima[1]}\nVuoi iniziare?"):
                c.execute("INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES (?, ?)",
                        ('ultima_scheda_usata', str(prossima[0])))
                conn.commit()
                self.mostra_scheda(prossima[0])

    def torna_home(self):
        self.frame.destroy()
        from gui.home import HomeScreen
        HomeScreen(self.root)

    def mostra_scheda(self, scheda_id):
        self.frame.destroy()
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        with connessione() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT e.nome, se.serie, se.ripetizioni, se.peso_target
                FROM scheda_esercizi se
                JOIN esercizi e ON se.esercizio_id = e.id
                WHERE se.scheda_id = ?
            """, (scheda_id,))
            esercizi = c.fetchall()

        tk.Label(self.frame, text="Allenamento in corso", font=("Arial", 16)).pack(pady=10)

        if not esercizi:
            tk.Label(self.frame, text="Questa scheda non ha esercizi.").pack()
            return

        self.esercizi = esercizi
        self.indice = 0
        self.serie_attuale = 1
        self.timer_serie_seconds = 60
        self.timer_serie_active = False
        self.timer_inter_esercizio_seconds = 90
        self.timer_inter_esercizio_active = False

        self.label_nome = tk.Label(self.frame, font=("Arial", 14))
        self.label_serie = tk.Label(self.frame, font=("Arial", 12))
        self.label_timer = tk.Label(self.frame, font=("Arial", 12), fg="green")

        self.label_nome.pack(pady=5)
        self.label_serie.pack(pady=5)
        self.label_timer.pack(pady=5)

        self.peso_entry = tk.Entry(self.frame, width=10, justify="center")
        self.rip_entry = tk.Entry(self.frame, width=10, justify="center")

        tk.Label(self.frame, text="Peso effettivo:").pack()
        self.peso_entry.pack()
        tk.Label(self.frame, text="Ripetizioni eseguite:").pack()
        self.rip_entry.pack()

        self.btn_completa = tk.Button(self.frame, text="✔️ Serie completata", command=self.completa_serie)
        self.btn_completa.pack(pady=10)

        tk.Button(self.frame, text="🏠 Torna alla Home", command=self.torna_home).pack(pady=10)

        self.mostra_esercizio_corrente()

    def mostra_esercizio_corrente(self):
        if self.indice >= len(self.esercizi):
            messagebox.showinfo("Fine", "Hai completato tutta la scheda! 💪")
            self.frame.destroy()
            from gui.home import HomeScreen
            HomeScreen(self.root)
            return

        nome, serie_totali, ripetizioni, peso = self.esercizi[self.indice]
        self.nome_corrente = nome
        self.serie_totali = serie_totali
        self.ripetizioni_correnti = ripetizioni
        self.peso_corrente = peso
        self.serie_attuale = 1

        self.label_nome.config(text=f"Esercizio: {nome}")
        self.aggiorna_interfaccia_serie()

    def aggiorna_interfaccia_serie(self):
        self.label_serie.config(text=f"Serie {self.serie_attuale} di {self.serie_totali}")
        self.peso_entry.delete(0, tk.END)
        self.peso_entry.insert(0, str(self.peso_corrente))
        self.rip_entry.delete(0, tk.END)
        self.rip_entry.insert(0, str(self.ripetizioni_correnti))
        self.label_timer.config(text="")

    def completa_serie(self):
        if self.timer_serie_active or self.timer_inter_esercizio_active:
            return

        try:
            peso_effettivo = float(self.peso_entry.get())
            rip_effettive = int(self.rip_entry.get())
        except ValueError:
            messagebox.showerror("Errore", "Inserisci valori validi per peso e ripetizioni.")
            return

        with connessione() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM esercizi WHERE nome = ?", (self.nome_corrente,))
            result = c.fetchone()
            if result:
                esercizio_id = result[0]
                oggi = datetime.now().strftime("%Y-%m-%d")
                c.execute("""
                    INSERT INTO progressi (esercizio_id, data, serie_completate, peso_utilizzato, ripetizioni_effettive)
                    VALUES (?, ?, ?, ?, ?)
                """, (esercizio_id, oggi, 1, peso_effettivo, rip_effettive))
                conn.commit()

        self.peso_corrente = peso_effettivo
        self.ripetizioni_correnti = rip_effettive

        if self.serie_attuale < self.serie_totali:
            self.serie_attuale += 1
            self.start_timer_serie()
        else:
            self.start_timer_inter_esercizio()

    def start_timer_serie(self):
        self.timer_serie_active = True
        self.seconds_left = self.timer_serie_seconds
        self.label_timer.config(text=f"⏱️ Riposo tra serie: {self.seconds_left} sec")
        self.btn_completa.config(state="disabled")
        self.countdown_serie()

    def countdown_serie(self):
        if self.seconds_left > 0:
            self.label_timer.config(text=f"⏱️ Riposo tra serie: {self.seconds_left} sec")
            self.seconds_left -= 1
            self.frame.after(1000, self.countdown_serie)
        else:
            self.label_timer.config(text="Inizia la prossima serie!")
            self.btn_completa.config(state="normal")
            self.timer_serie_active = False
            self.aggiorna_interfaccia_serie()

    def start_timer_inter_esercizio(self):
        self.timer_inter_esercizio_active = True
        self.seconds_left = self.timer_inter_esercizio_seconds
        self.label_timer.config(text=f"⏱️ Riposo tra esercizi: {self.seconds_left} sec")
        self.btn_completa.config(state="disabled")
        self.countdown_inter_esercizio()

    def countdown_inter_esercizio(self):
        if self.seconds_left > 0:
            self.label_timer.config(text=f"⏱️ Riposo tra esercizi: {self.seconds_left} sec")
            self.seconds_left -= 1
            self.frame.after(1000, self.countdown_inter_esercizio)
        else:
            self.label_timer.config(text="Inizia il prossimo esercizio!")
            self.btn_completa.config(state="normal")
            self.timer_inter_esercizio_active = False
            self.indice += 1
            self.mostra_esercizio_corrente()