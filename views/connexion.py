import streamlit as st
from utils.init_session import reset_session

def show():
  st.markdown("<h1 style='color: #1e293b; margin-bottom: 1.5rem;'>Mon Compte 👤</h1>", unsafe_allow_html=True)
  
  if st.session_state.get('authenticated'):
      user = st.session_state.get('user')
      if user:
          col1, col2, col3 = st.columns([1, 2, 1])
          with col2:
              with st.container(border=True):
                  st.markdown("<div style='text-align: center; font-size: 4rem; color: #10b981;'>👨‍🌾</div>", unsafe_allow_html=True)
                  st.markdown(f"<h2 style='text-align: center; color: #1e293b; margin-top: 0;'>{user.get('prenom')} {user.get('nom')}</h2>", unsafe_allow_html=True)
                  st.markdown(f"<p style='text-align: center; color: #64748b; font-size: 1.1rem;'>{user.get('email')}</p>", unsafe_allow_html=True)
                  
                  st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.5;'>", unsafe_allow_html=True)
                  
                  st.write("**Statut du compte :** Actif ✅")
                  
                  st.write("<br>", unsafe_allow_html=True)
                  if st.button("Se déconnecter", use_container_width=True):
                      reset_session()
                      st.rerun()
  else:
      st.warning("Vous n'êtes pas connecté.")