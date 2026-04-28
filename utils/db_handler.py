
import bcrypt
import streamlit as st
from databases.db import get_connection


def get_user_by_email(email):
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute(
      "SELECT * FROM utilisateurs WHERE email=?",
      (email,)
  )

  user = cursor.fetchone()
  conn.close()

  return user

def get_user_name_by_email(email):
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute(
      "SELECT nom FROM utilisateurs WHERE email=?",
      (email,)
  )

  user = cursor.fetchone()
  conn.close()

  return user["nom"] if user else None

def authenticate_user(email, password):
    conn = get_connection()
    cur = conn.cursor()
    
    # Retrieve the stored hashed password for the user
    cur.execute("SELECT hash_password FROM utilisateurs WHERE email = ?", (email,))
    stored_hashed_password = cur.fetchone()
    
    cur.close()
    conn.close()

    # Check if a user with the given email was found
    if stored_hashed_password is None:
        return False
    
    stored_hashed_password = stored_hashed_password[0]  # Extract the hash from the tuple

    # Compare the provided password with the stored hashed password
    return bcrypt.checkpw(password.encode(), stored_hashed_password.encode())

def create_user(nom, prenom, email, password):
  conn = get_connection()
  cursor = conn.cursor()
  hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

  cursor.execute("""
    INSERT INTO utilisateurs (nom, prenom, email, hash_password)
    VALUES (?, ?, ?, ?)
    """, (nom, prenom, email, hashed_password))

  conn.commit()
  conn.close()

def verify_duplicate_user(email):
  conn = get_connection()

  cur = conn.cursor()
  
  cur.execute("SELECT COUNT(*) FROM utilisateurs WHERE email = ?", (email,))
  count = cur.fetchone()[0]
  
  cur.close()
  conn.close()
  
  return count > 0


def get_users():

  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("SELECT * FROM utilisateurs")

  users = cursor.fetchall()

  conn.close()

  return users
  
def update_user(user_id, nom, email):

  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  UPDATE utilisateurs
  SET nom=?, email=?
  WHERE id=?
  """, (nom, email, user_id))

  conn.commit()
  conn.close()

  
  
#Champs
def create_champ(nom, localisation, superficie, utilisateur_id):
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  INSERT INTO champs (nom, localisation, superficie, utilisateur_id)
  VALUES (?, ?, ?, ?)
  """, (nom, localisation, superficie, utilisateur_id))

  conn.commit()
  conn.close()
    
def get_champs_by_user(user_id):
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  SELECT id, nom, localisation, superficie FROM champs
  WHERE utilisateur_id = ?
  """, (user_id,))

  champs = cursor.fetchall()
  conn.close()

  return champs

def update_champ(champ_id, nom, localisation):

  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  UPDATE champs
  SET nom=?, localisation=?
  WHERE id=?
  """, (nom, localisation, champ_id))

  conn.commit()
  conn.close()
  
#Cultures
def create_culture(type_culture, date_plantation, champ_id):  
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  INSERT INTO cultures (type_culture, date_plantation, champ_id)
  VALUES (?, ?, ?)
  """, (type_culture, date_plantation, champ_id))

  conn.commit()
  conn.close()

def get_cultures_by_champ(champ_id):

  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  SELECT * FROM cultures
  WHERE champ_id=?
  """, (champ_id,))

  cultures = cursor.fetchall()

  conn.close()

  return cultures

def update_culture(culture_id, nom_culture):

  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  UPDATE cultures
  SET nom_culture=?
  WHERE id=?
  """, (nom_culture, culture_id))

  conn.commit()
  conn.close()
    
#Analyses
def get_user_analyses(user_id):

  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  SELECT *
  FROM analyses
  WHERE utilisateur_id = ?
  ORDER BY date_analyse DESC
  """, (user_id,))

  data = cursor.fetchall()
  conn.close()

  return data

def save_analysis(utilisateur_id, culture_id, image_path, prediction, confiance, statut):

  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  INSERT INTO analyses (
      utilisateur_id,
      culture_id,
      image_path,
      prediction,
      confiance,
      statut
  )
  VALUES (?, ?, ?, ?, ?, ?)
  """, (
      utilisateur_id,
      culture_id,
      image_path,
      prediction,
      confiance,
      statut
  ))

  conn.commit()
  conn.close()

def update_analysis(analysis_id, prediction, confiance, statut):

  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  UPDATE analyses
  SET prediction=?, confiance=?, statut=?
  WHERE id=?
  """, (prediction, confiance, statut, analysis_id))

  conn.commit()
  conn.close()
  
def get_analyses_by_culture(culture_id):
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
  SELECT *
  FROM analyses
  WHERE culture_id=?
  """, (culture_id,))

  data = cursor.fetchall()

  conn.close()

  return data
