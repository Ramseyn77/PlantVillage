import streamlit as st
from utils.init_session import init_session, reset_session
from utils.navigate import sidebar_navigation
from views.app import app_page
from views.login import login_page
from views.signup import signup_page


if __name__ == "__main__":
  from databases.db import init_db
  init_db()  # Crée la BDD automatiquement en production
  
  init_session()
  
  st.set_page_config(
    page_title="PhytoDiag IA",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
  )
  
  from utils.style import load_css
  load_css()
  
  if st.session_state['authenticated']:
    app_page()
    print('utilisateur connecté : ', st.session_state.get('user_email', 'Guest'))
  else:
    if st.session_state['page'] == 'login':
      reset_session()
      login_page(guest_mode=True)
    elif st.session_state['page'] == 'signup':
      signup_page(
        extra_input_params=True,
        confirmPass = True
      )
      print('utilisateur inscrit : ', st.session_state.get('user_email', 'Guest'))

  
  

 