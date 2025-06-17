import sqlite3
import os

DB_PATH = "data/gym.db"

def connessione():
    return sqlite3.connect(DB_PATH)

def crea_tabelle():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    with connessione() as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS esercizi (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            muscolo TEXT
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS schede (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            attiva BOOLEAN DEFAULT 0,
            ultimo_utilizzo DATE
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS scheda_esercizi (
            id INTEGER PRIMARY KEY,
            scheda_id INTEGER,
            esercizio_id INTEGER,
            serie INTEGER,
            ripetizioni INTEGER,
            peso_target REAL
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS progressi (
            id INTEGER PRIMARY KEY,
            esercizio_id INTEGER,
            data TEXT,
            serie_completate INTEGER,
            peso_utilizzato REAL,
            ripetizioni_effettive INTEGER,
            FOREIGN KEY (esercizio_id) REFERENCES esercizi(id)
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS impostazioni (
            chiave TEXT PRIMARY KEY,
            valore TEXT
        )""")

        conn.commit()
