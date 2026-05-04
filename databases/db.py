import sqlite3
import os

DB_NAME = "phyto_diag.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Création des tables si elles n'existent pas (Essentiel pour le déploiement)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hash_password TEXT NOT NULL,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS champs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        localisation TEXT,
        superficie REAL,
        utilisateur_id INTEGER,
        FOREIGN KEY(utilisateur_id) REFERENCES utilisateurs(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cultures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_culture TEXT NOT NULL,
        date_plantation DATE,
        champ_id INTEGER,
        FOREIGN KEY(champ_id) REFERENCES champs(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        utilisateur_id INTEGER,
        culture_id INTEGER,
        image_path TEXT,
        prediction TEXT,
        confiance REAL,
        statut TEXT,
        date_analyse TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(utilisateur_id) REFERENCES utilisateurs(id),
        FOREIGN KEY(culture_id) REFERENCES cultures(id)
    )
    ''')
    
    conn.commit()
    conn.close()