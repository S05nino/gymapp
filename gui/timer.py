import tkinter as tk
import threading
import time

def avvia_timer_popup(root, secondi):
    popup = tk.Toplevel(root)
    popup.title("Timer Recupero")
    label = tk.Label(popup, text=f"{secondi} secondi di recupero")
    label.pack(pady=10)

    def countdown():
        for i in range(secondi, 0, -1):
            label.config(text=f"{i} secondi restanti")
            time.sleep(1)
        label.config(text="Tempo scaduto!")
        time.sleep(1)
        popup.destroy()

    threading.Thread(target=countdown).start()
