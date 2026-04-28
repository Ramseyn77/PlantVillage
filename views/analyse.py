import streamlit as st
from utils.db_handler import get_user_analyses

def show():
  st.title("Mes Analyses")
  
  st.write("Liste de vos historiques d'analyses sauvegardés :")
  
  analyses = get_user_analyses(st.session_state['user']['id'])
  if analyses:
    import pandas as pd
    df = pd.DataFrame(analyses, columns=["ID", "Utilisateur ID", "Culture ID", "Image", "Prédiction", "Confiance", "Statut", "Date d'Analyse"])
    df = df.drop(columns=["ID", "Utilisateur ID", "Culture ID", "Image"])
    df['Confiance'] = df['Confiance'].apply(lambda x: f"{float(x)*100:.2f}%" if pd.notnull(x) else "N/A")
    st.dataframe(df, hide_index=True, use_container_width=True)
  else:
    st.write("Aucune analyse trouvée pour cet utilisateur.")