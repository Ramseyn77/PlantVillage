import streamlit as st
from utils.db_handler import get_champs_by_user, create_culture, get_cultures_by_champ

def show():
  st.title("Mes Cultures")
  cols = st.columns([1, 1])
  
  with cols[0]:
    st.subheader("Ajoutez une culture")
    
    champs = get_champs_by_user(st.session_state['user']['id'])
    
    if not champs:
      st.warning("Veuillez d'abord ajouter un champ.")
    else:
      champ_dict = {f"{c[1]} - {c[2]}": c[0] for c in champs}
      selected_champ_ajout = st.selectbox("Sélectionnez le champ", list(champ_dict.keys()), key="champ_ajout")
      
      type_culture = st.text_input("Type de culture (ex: Tomate) : ")
      date_plantation = st.date_input("Date de plantation :")
      
      if st.button("Ajouter la culture"):
        if type_culture and type_culture.isalpha():
          create_culture(type_culture, str(date_plantation), champ_dict[selected_champ_ajout])
          st.success("Culture ajoutée avec succès !")
          st.rerun()
        else:
          st.error("Le type de culture doit être alphabétique.")
          
  with cols[1]:
    st.subheader("Liste de vos cultures")
    if not champs:
      st.write("Aucun champ.")
    else:
      selected_champ_liste = st.selectbox("Sélectionnez le champ", list(champ_dict.keys()), key="champ_liste")
      cultures = get_cultures_by_champ(champ_dict[selected_champ_liste])
      
      if cultures:
        import pandas as pd
        df = pd.DataFrame(cultures, columns=["ID", "Type", "Date Plantation", "Champ ID"])
        df = df.drop(columns=["ID", "Champ ID"])
        st.dataframe(df, hide_index=True)
      else:
        st.info("Aucune culture pour ce champ.")