import streamlit as st
import time
from utils.db_handler import get_user_analyses

def show():
    st.markdown("<h1 style='color: #1e293b; margin-bottom: 1.5rem;'>Historique des analyses 📊</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;'>Retrouvez l'ensemble de vos diagnostics précédents.</p>", unsafe_allow_html=True)
    
    if st.session_state.get('user') and st.session_state['user'].get('id'):
        user_id = st.session_state['user']['id']
        data = get_user_analyses(user_id)
        
        if not data:
            st.info("Aucune analyse effectuée pour le moment. Allez dans l'onglet Reconnaissance pour commencer.")
        else:
            for scan in data:
                # scan: (id, utilisateur_id, culture_id, image_path, prediction, confiance, statut, date_analyse)
                is_saine = scan[6] == "Saine"
                icon = "🌿" if is_saine else "⚠️"
                color = "#10b981" if is_saine else "#ef4444"
                
                with st.container(border=True):
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col1:
                        st.markdown(f"<div style='font-size: 2.5rem; color: {color}; text-align: center; line-height: 1;'>{icon}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align: center; color: {color}; font-weight: bold;'>{scan[6]}</div>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<h4 style='margin:0; color: #1e293b;'>{scan[4].replace('_', ' ')}</h4>", unsafe_allow_html=True)
                        st.markdown(f"<p style='margin:0; color: #64748b; font-size: 0.9rem;'>Fichier : {scan[3]}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='margin:0; color: #64748b; font-size: 0.9rem;'>Date : {scan[7]}</p>", unsafe_allow_html=True)
                    with col3:
                        st.metric("Confiance", f"{float(scan[5])*100:.1f}%")
    else:
        st.warning("Veuillez vous connecter pour consulter votre historique personnel.")