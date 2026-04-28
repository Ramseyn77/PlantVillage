import streamlit as st
from utils.init_session import reset_session

def show():
  st.header("Mon Compte")
  if st.session_state.get('authenticated'):
      user = st.session_state.get('user')
      if user:
          st.write(f"**Nom :** {user.get('nom')}")
          st.write(f"**Prénom :** {user.get('prenom')}")
          st.write(f"**Email :** {user.get('email')}")
      
      if st.button("Se déconnecter"):
          reset_session()
          st.rerun()
  else:
      st.write("Vous n'êtes pas connecté.")