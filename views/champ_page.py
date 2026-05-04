import streamlit as st
from utils.db_handler import get_champs_by_user, create_champ

def show():
  st.markdown("<h1 style='color: #1e293b; margin-bottom: 1.5rem;'>Mes Champs 🌾</h1>", unsafe_allow_html=True)
  st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;'>Gérez vos différentes parcelles agricoles.</p>", unsafe_allow_html=True)
  
  cols = st.columns([1, 2])
  
  with cols[0]:
    with st.container(border=True):
        st.markdown("<h3 style='color: #10b981; margin-top: 0;'>Ajouter un champ</h3>", unsafe_allow_html=True)
        
        nom_champ = st.text_input("Nom du champ", placeholder="Ex: Champ Nord")
        if nom_champ and not nom_champ.replace(' ', '').isalpha():
          st.error("Le nom ne doit contenir que des lettres")
        
        superficie = st.text_input("Superficie (hectares)", placeholder="Ex: 2.5")
        if superficie and not superficie.replace('.', '', 1).isdigit():
          st.error("La superficie doit être un nombre valide")  
        
        localisation = st.text_input("Localisation", placeholder="Ex: Bretagne")
        if localisation and not localisation.replace(' ', '').isalpha():
          st.error("La localisation ne doit contenir que des lettres")  
        
        st.write("<br>", unsafe_allow_html=True)
        if st.button("Ajouter le champ", use_container_width=True):
          if nom_champ and superficie and localisation and nom_champ.replace(' ', '').isalpha() and superficie.replace('.', '', 1).isdigit() and localisation.replace(' ', '').isalpha():
            create_champ(nom_champ, localisation, float(superficie), st.session_state['user']['id'])
            st.success("✅ Champ ajouté avec succès !")
            st.rerun()
          else:
            st.error("Veuillez entrer des informations valides pour tous les champs.")

  with cols[1]:
    with st.container(border=True):
        st.markdown("<h3 style='color: #3b82f6; margin-top: 0;'>Liste de vos champs</h3>", unsafe_allow_html=True)
        
        champs_users = get_champs_by_user(st.session_state['user']['id'])
        if champs_users:
          import pandas as pd
          df = pd.DataFrame(champs_users, columns=["ID", "Nom", "Localisation", "Superficie (ha)"])
          df = df.drop(columns=["ID"])
          st.dataframe(df, hide_index=True, use_container_width=True)
        else:
          st.info("Vous n'avez ajouté aucun champ pour le moment.")