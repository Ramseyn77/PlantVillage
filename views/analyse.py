import streamlit as st
from utils.db_handler import *


def show():
  st.title("Mes Analyses")
  cols = st.columns([1, 3])
  
  top_left_cell = cols[0].container(
    border=True, height="stretch", vertical_alignment="center"
  )
  top_right_cell = cols[1].container(
    border=True, height="stretch", vertical_alignment="top"
  ) 
  
  with top_left_cell:
    st.write("Ajoutez un champ")
    st.write("")
    nom_champ = st.text_input("Nom du champ : ")
    if nom_champ and not nom_champ.isalpha():
      st.error("Le nom ne doit contenir que des lettres")
    
    superficie = st.text_input("Superficie du champ (en hectares) : ")
    if superficie and not superficie.replace('.', '', 1).isdigit():
      st.error("La superficie doit être un nombre valide")  
    
    localisation = st.text_input("Localisation du champ : ")
    if localisation and not localisation.isalpha():
      st.error("La localisation ne doit contenir que des lettres")  
    
    if st.button("Ajouter le champ"):
      if nom_champ and superficie and localisation and nom_champ.isalpha() and superficie.replace('.', '', 1).isdigit() and localisation.isalpha():
        create_champ(nom_champ, float(superficie), localisation, st.session_state['user']['id'])
        st.success("Champ ajouté avec succès !")
        st.rerun()
      else:
        st.error("Veuillez entrer des informations valides pour tous les champs.")
    st.image("./home_image.jpg" )
  with top_right_cell: 
    st.write("")
    st.write("")
    st.write("Description des analyses")    
    
    st.write("Liste de vos analyses :")
    
    analyses_users = get_user_analyses(st.session_state['user']['id'])
    if analyses_users:
      st.table(analyses_users)
    else:
      st.write("Aucune analyse trouvée pour cet utilisateur.")