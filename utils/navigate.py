import streamlit as st
from utils.init_session import reset_session

def sidebar_navigation():
    # Logo / Titre
    st.sidebar.markdown("""
        <div style="margin-bottom: 2rem; padding: 0.5rem 1rem;">
            <h2 style="color: #10b981; font-weight: 800; margin:0; font-size: 1.8rem;">🌿 PhytoDiag</h2>
            <p style="color: #64748b; font-size: 0.9rem; margin:0;">Diagnostic intelligent</p>
        </div>
    """, unsafe_allow_html=True)

    if 'page' not in st.session_state:
        st.session_state['page'] = 'Accueil'

    def nav_button(label, page_name):
        is_active = st.session_state['page'] == page_name
        # Add a subtle indicator if active
        prefix = "🟢" if is_active else "⬜"
        # We use a custom key
        if st.sidebar.button(f"{prefix} {label}", key=f"nav_{page_name}"):
            st.session_state['page'] = page_name
            st.rerun()

    st.sidebar.markdown("<p style='color: #94a3b8; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem; padding-left: 1rem;'>Principal</p>", unsafe_allow_html=True)
    nav_button("Accueil", "Accueil")
    nav_button("Reconnaissance", "Reconnaissance")
    nav_button("Historique", "Historique")
    
    st.sidebar.write("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='color: #94a3b8; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem; padding-left: 1rem;'>Gestion</p>", unsafe_allow_html=True)
    nav_button("Mes Champs", "Champs")
    nav_button("Mes Cultures", "Cultures")
    nav_button("Mes Analyses", "Analyses")

    st.sidebar.write("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='color: #94a3b8; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem; padding-left: 1rem;'>Application</p>", unsafe_allow_html=True)
    nav_button("Mon Compte", "Connexion")
    nav_button("À propos", "À propos")
    
    st.sidebar.write("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Se déconnecter", key="nav_logout"):
        reset_session()
        st.rerun()
        
    return st.session_state['page']