import streamlit as st
from utils.db_handler import authenticate_user, get_user_by_email
import time

def login_page(guest_mode=False):
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #10b981; font-size: 3rem; margin-bottom: 0;">🌿 PhytoDiag</h1>
            <p style="color: #64748b; font-size: 1.1rem;">Connectez-vous pour gérer vos cultures</p>
        </div>
        """, unsafe_allow_html=True)
        
        # We use a standard container here, CSS from style.py styles inputs nicely
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem;'>Bon retour !</h3>", unsafe_allow_html=True)
            
            email = st.text_input("Adresse E-mail", placeholder="agriculteur@domaine.com")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            
            st.write("<br>", unsafe_allow_html=True)
            
            if st.button("Se connecter", use_container_width=True):
                if not (email and password):
                    st.error("Veuillez remplir tous les champs.")
                else:
                    with st.spinner("Vérification des identifiants..."):
                        time.sleep(1)
                        if authenticate_user(email, password):
                            st.session_state['authenticated'] = True
                            st.session_state['page'] = 'Accueil'
                            user = get_user_by_email(email)
                            st.session_state['user'] = {
                                'id': user[0],  
                                'nom': user[1],
                                'prenom': user[2],
                                'email': user[3],
                            }    
                            st.session_state['user_email'] = email
                            st.rerun()
                        else:
                            st.error("Email ou mot de passe incorrect.")
            
            st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.5;'>", unsafe_allow_html=True)
            
            if st.button("Créer un compte", use_container_width=True):
                st.session_state['page'] = 'signup'
                st.rerun()
                
            if guest_mode:
                st.write("<div style='text-align: center; margin: 1rem 0; color: #94a3b8;'>ou</div>", unsafe_allow_html=True)
                if st.button("Continuer en tant qu'invité", use_container_width=True):
                    st.session_state['guest_mode'] = True
                    st.session_state['authenticated'] = True
                    st.session_state['page'] = 'Accueil'
                    st.rerun()