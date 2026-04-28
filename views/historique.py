import streamlit as st
import time
from utils.db_handler import get_user_analyses

def show():
    st.header("Historique des analyses")
    
    if st.session_state.get('user') and st.session_state['user'].get('id'):
        user_id = st.session_state['user']['id']
        data = get_user_analyses(user_id)
        
        if not data:
            st.write("Aucune analyse effectuée pour le moment.")
        else:
            for scan in data:
                # scan order (id, utilisateur_id, culture_id, image_path, prediction, confiance, statut, date_analyse)
                icon = "🌿" if scan[6] == "Saine" else "⚠️"
                st.markdown(f"""
                🕒 **{scan[7]}** | 📄 *{scan[3]}* | **{scan[4]}** | Confiance : **{float(scan[5])*100:.1f}%** | {icon} *{scan[6]}*
                """)
                st.divider()
    else:
        st.warning("Veuillez vous connecter pour voir votre historique.")