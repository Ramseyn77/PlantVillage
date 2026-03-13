
import streamlit as st
from utils.db_handler import authenticate_user, get_user_by_email
import time

# Pages
def login_page(guest_mode=False):
    with st.empty().container(border=True):
        col1, _, col2 = st.columns([10,1,10])
        
        with col1:
            st.write("")
            st.write("")
            # st.video("data/demo.mp4", autoplay=True, loop=True, muted=True)
            st.image("home_image.jpg")
        
        with col2:
            st.title("Connexion")

            email = st.text_input("E-mail")
            password = st.text_input("Password", type="password")

            if st.button("Se connecter"):
                time.sleep(2)
                if not (email and password):
                    st.error("Entrez votre e-mail et mot de passe")
                elif authenticate_user(email, password):
                    st.session_state['authenticated'] = True
                    st.session_state['page'] = 'Accueil'
                    st.success("Connexion réussie ! Redirection...")
                    user = get_user_by_email(email)
                    print(user)                    
                    st.session_state['user'] = {
                        'id': user[0],  
                        'nom': user[1],
                        'prenom': user[2],
                        'email': user[3],
                    }    
                    st.session_state['user_email'] = email
                    st.rerun()
                else:
                    st.error("Email ou mot de passe incorrect")

            if st.button("s'inscrire"):
                st.session_state['page'] = 'signup'
                st.rerun()
                
            if guest_mode:
                if st.button("Continue as Guest"):
                    st.session_state['guest_mode'] = True
                    st.session_state['authenticated'] = True
                    st.session_state['page'] = 'app'
                    st.rerun()