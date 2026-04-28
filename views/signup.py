import streamlit as st
import re
from utils.otp_handler import generate_otp, send_email
from utils.db_handler import create_user, verify_duplicate_user
import time

def is_valid_email(email):
    """Check if the provided email is valid using regex."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def input_field(input_param, type):
    """Render an input field based on the type and store the value in session state."""
    if type == 'text':
        st.session_state[input_param] = st.text_input(input_param)
    elif type == 'number':
        st.session_state[input_param] = st.number_input(input_param, step=1)

def verifyOTP(otp_input):
    """Verify the OTP input by the user."""
    if otp_input == st.session_state['otp']:
        st.success("OTP est vérifié avec succès ! Création du compte...")
        time.sleep(1)
        st.session_state['verifying'] = False
        st.session_state['otp'] = ""
        create_user(st.session_state['user']['nom'], 
                    st.session_state['user']['prenom'], 
                    st.session_state['user']['email'], 
                    st.session_state['password'])
        st.session_state['page'] = 'login'
        st.rerun()
    else:
        st.error("Invalid OTP")

def signup_page(extra_input_params=False, confirmPass=False):
    """Render the signup page with optional extra input parameters and password confirmation."""
    if st.session_state['verifying']:
        # Check if the user already exists
        if verify_duplicate_user(st.session_state['user']['email']):
            st.error("Ce compte existe déjà. Veuillez vous connecter.")
            time.sleep(1)
            st.session_state['verifying'] = False
            st.rerun()
        
        st.write("Verification OTP...")
        st.info(f"OTP a été envoyé à {st.session_state['user']['email']}")
        print(st.session_state['otp'])
        if st.session_state['otp'] == "":
            st.session_state['otp'] = generate_otp()
            print(st.session_state['otp'])
            send_email(st.session_state['user']['email'], st.session_state['otp'])
                
        with st.empty().container():
            otp_input = st.text_input(label="Enter OTP", placeholder="Enter OTP")
            if st.button("Valider OTP"):
                verifyOTP(otp_input)
                
            if st.button("Renvoyer OTP"):
                sent = False
                st.session_state['otp'] = generate_otp()
                send_email(st.session_state['user']['email'], st.session_state['otp'])
        
    else:
        if st.button("Back to Login"):
            st.session_state['page'] = 'login'
            st.rerun()
        
        with st.empty().container(border=True):
            st.title("S'inscrire")
            
            st.write("Veuillez remplir les champs suivants pour créer un compte.")
            
            st.session_state['user']['nom'] = st.text_input("Nom")
            if st.session_state['user']['nom'] and not st.session_state['user']['nom'].isalpha():
                st.error("Le nom ne doit contenir que des lettres")
            
            st.session_state['user']['prenom'] = st.text_input("Prénom")
            if st.session_state['user']['prenom'] and not st.session_state['user']['prenom'].isalpha():
                st.error("Le prénom ne doit contenir que des lettres")
            
            # Email input with validation
            st.session_state['user']['email'] = st.text_input("Email")
            if st.session_state['user']['email'] and not is_valid_email(st.session_state['user']['email']):
                st.error("Merci d'entrer une adresse e-mail valide")

            # Password input
            st.session_state['password'] = st.text_input("Password", type='password')
            
            # Confirm password if required
            if confirmPass:
                confirm_password = st.text_input("Confirm Password", type='password')
            
            # Extra input fields if any
            if extra_input_params:
                for input_param, type in st.session_state['extra_input_params'].items():
                    input_field(input_param, type)
            
            if st.button("S'inscrire"):
                if not (st.session_state['user']['nom'] and st.session_state['user']['prenom'] and st.session_state['user']['email'] and st.session_state['password']):
                    st.error("Merci de remplir tous les champs requis")
                elif confirmPass and st.session_state['password'] != confirm_password:
                    st.error("Les mots de passe ne correspondent pas")
                elif not is_valid_email(st.session_state['user']['email']):
                    st.error("Merci d'entrer une adresse e-mail valide")
                elif not (st.session_state['user']['nom'].isalpha() and st.session_state['user']['prenom'].isalpha()):
                    st.error("Le nom et le prénom ne doivent contenir que des lettres")
                else:
                    st.session_state['verifying'] = True
                    st.rerun()
