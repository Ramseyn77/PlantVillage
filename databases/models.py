from databases.db import get_connection


def create_tables():
  conn = get_connection()
  cursor = conn.cursor()

  # TABLE UTILISATEURS
  cursor.execute("""
  CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hash_password TEXT NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
  """)
  print("Table 'utilisateurs' created successfully.")

  # TABLE CHAMPS
  cursor.execute("""
  CREATE TABLE IF NOT EXISTS champs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    localisation TEXT,
    superficie REAL,
    utilisateur_id INTEGER,
    FOREIGN KEY(utilisateur_id) REFERENCES utilisateurs(id)
  )
  """)
  print("Table 'champs' created successfully.")

  # TABLE CULTURES
  cursor.execute("""
  CREATE TABLE IF NOT EXISTS cultures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_culture TEXT NOT NULL,
    date_plantation DATE,
    champ_id INTEGER,
    FOREIGN KEY(champ_id) REFERENCES champs(id)
  )
  """)
  print("Table 'cultures' created successfully.")
  
  # TABLE ANALYSES
  cursor.execute("""
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
  """)
  print("Table 'analyses' created successfully.")

  conn.commit()
  conn.close()
    
    
if __name__ == "__main__":
  create_tables()
