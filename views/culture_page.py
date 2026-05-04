import streamlit as st
from utils.db_handler import get_champs_by_user, create_culture, get_cultures_by_champ

def show():
  st.markdown("<h1 style='color: #1e293b; margin-bottom: 1.5rem;'>Mes Cultures 🌱</h1>", unsafe_allow_html=True)
  st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;'>Suivez les cultures plantées dans vos différents champs.</p>", unsafe_allow_html=True)
  
  cols = st.columns([1, 2])
  
  champs = get_champs_by_user(st.session_state['user']['id'])
  champ_dict = {f"{c[1]} ({c[2]})": c[0] for c in champs} if champs else {}
  
  with cols[0]:
    with st.container(border=True):
        st.markdown("<h3 style='color: #10b981; margin-top: 0;'>Ajouter une culture</h3>", unsafe_allow_html=True)
        
        if not champs:
          st.warning("Veuillez d'abord ajouter un champ dans l'onglet 'Champs'.")
        else:
          selected_champ_ajout = st.selectbox("Sélectionnez le champ", list(champ_dict.keys()), key="champ_ajout")
          
          type_culture = st.text_input("Type de culture", placeholder="Ex: Tomates")
          date_plantation = st.date_input("Date de plantation")
          
          st.write("<br>", unsafe_allow_html=True)
          if st.button("Ajouter la culture", use_container_width=True):
            if type_culture and type_culture.replace(' ', '').isalpha():
              create_culture(type_culture, str(date_plantation), champ_dict[selected_champ_ajout])
              st.success("✅ Culture ajoutée avec succès !")
              st.rerun()
            else:
              st.error("Le type de culture doit être valide (lettres uniquement).")
          
  with cols[1]:
    with st.container(border=True):
        st.markdown("<h3 style='color: #3b82f6; margin-top: 0;'>Liste de vos cultures</h3>", unsafe_allow_html=True)
        if not champs:
          st.info("Aucun champ trouvé.")
        else:
          selected_champ_liste = st.selectbox("Filtrer par champ", list(champ_dict.keys()), key="champ_liste")
          cultures = get_cultures_by_champ(champ_dict[selected_champ_liste])
          
          if cultures:
            import pandas as pd
            df = pd.DataFrame(cultures, columns=["ID", "Type de Culture", "Date Plantation", "Champ ID"])
            df = df.drop(columns=["ID", "Champ ID"])
            st.dataframe(df, hide_index=True, use_container_width=True)
          else:
            st.info("Aucune culture enregistrée pour ce champ.")