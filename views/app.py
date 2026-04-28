import streamlit as st
from utils.db_handler import get_users
from utils.init_session import reset_session
from utils.navigate import sidebar_navigation
from views import (
  accueil_page,
  apropos_page,
  reconnaissance_page,
  historique_page,
  connexion_page,  
  champ_page,
  culture_page,
  analyse_page
)

 # --- SIDEBAR NAVIGATION ---
def app_page():
  page = sidebar_navigation()

  # --- ROUTEUR ---
  if page == "Accueil":
    accueil_page()

  elif page == "À propos":
    apropos_page()

  elif page == "Reconnaissance":
    reconnaissance_page()

  elif page == "Historique":
    historique_page()
    
  elif page == "Connexion":
    connexion_page()  
    
  elif page == "Champs":
    champ_page()

  elif page == "Cultures":
    culture_page()

  elif page == "Analyses":
    analyse_page()
