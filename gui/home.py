import tkinter as tk
from db.database import connessione

class HomeScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="🏋️‍♂️ Gym Tracker", font=("Arial", 20)).pack(pady=20)

        # Verifica scheda attiva
        with connessione() as conn:
            c = conn.cursor()
            c.execute("SELECT nome FROM schede WHERE attiva = 1")
            attiva = c.fetchone()

        if attiva:
            nome_scheda = attiva[0]
            label_attiva = tk.Label(self.frame, text=f"📌 Scheda attiva: {nome_scheda}", fg="blue", font=("Arial", 12))
            label_attiva.pack(pady=5)
            label_attiva_bis = tk.Label(self.frame, text="Pronto per iniziare l’allenamento?", font=("Arial", 10))
            label_attiva_bis.pack()

        # Pulsanti di navigazione
        tk.Button(self.frame, text="➕ Crea Scheda", width=30, command=self.go_to_crea_scheda).pack(pady=10)
        tk.Button(self.frame, text="📋 Vai alla Scheda", width=30, command=self.go_to_workout).pack(pady=10)
        tk.Button(self.frame, text="📈 Progressi", width=30, command=self.go_to_progressi).pack(pady=10)

    def go_to_crea_scheda(self):
        self.frame.destroy()
        from gui.create_scheda import CreateSchedaScreen
        CreateSchedaScreen(self.root)

    def go_to_workout(self):
        self.frame.destroy()
        from gui.workout import WorkoutScreen
        WorkoutScreen(self.root)

    def go_to_progressi(self):
        self.frame.destroy()
        from gui.progress import ProgressScreen
        ProgressScreen(self.root)
