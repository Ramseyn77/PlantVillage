import streamlit as st
import re
from utils.otp_handler import generate_otp, send_email
from utils.db_handler import create_user, verify_duplicate_user
import time

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def verifyOTP(otp_input):
    if otp_input == st.session_state['otp']:
        st.success("Code vérifié avec succès ! Création du compte en cours...")
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
        st.error("Code de vérification invalide.")

def signup_page(extra_input_params=False, confirmPass=False):
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        if st.session_state['verifying']:
            with st.container(border=True):
                st.markdown("<h2 style='text-align: center; color: #10b981;'>Vérification de l'E-mail</h2>", unsafe_allow_html=True)
                st.info(f"Un code de sécurité (OTP) a été envoyé à **{st.session_state['user']['email']}**.")
                
                if st.session_state['otp'] == "":
                    st.session_state['otp'] = generate_otp()
                    send_email(st.session_state['user']['email'], st.session_state['otp'])
                
                otp_input = st.text_input("Code de vérification", placeholder="Entrez le code à 6 chiffres")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Valider le code", use_container_width=True):
                        verifyOTP(otp_input)
                with col_btn2:
                    if st.button("Renvoyer le code", use_container_width=True):
                        st.session_state['otp'] = generate_otp()
                        send_email(st.session_state['user']['email'], st.session_state['otp'])
                        st.success("Un nouveau code a été envoyé.")
        else:
            with st.container(border=True):
                st.markdown("<h2 style='text-align: center; color: #1e293b; margin-bottom: 1.5rem;'>Créer un compte</h2>", unsafe_allow_html=True)
                
                col_nom, col_prenom = st.columns(2)
                with col_nom:
                    st.session_state['user']['nom'] = st.text_input("Nom", placeholder="Doe")
                with col_prenom:
                    st.session_state['user']['prenom'] = st.text_input("Prénom", placeholder="John")
                
                st.session_state['user']['email'] = st.text_input("E-mail", placeholder="john.doe@example.com")
                st.session_state['password'] = st.text_input("Mot de passe", type='password', placeholder="••••••••")
                
                if confirmPass:
                    confirm_password = st.text_input("Confirmer le mot de passe", type='password', placeholder="••••••••")
                
                st.write("<br>", unsafe_allow_html=True)
                
                if st.button("S'inscrire", use_container_width=True):
                    if not (st.session_state['user']['nom'] and st.session_state['user']['prenom'] and st.session_state['user']['email'] and st.session_state['password']):
                        st.error("Merci de remplir tous les champs requis.")
                    elif confirmPass and st.session_state['password'] != confirm_password:
                        st.error("Les mots de passe ne correspondent pas.")
                    elif not is_valid_email(st.session_state['user']['email']):
                        st.error("L'adresse e-mail n'est pas valide.")
                    elif not (st.session_state['user']['nom'].isalpha() and st.session_state['user']['prenom'].isalpha()):
                        st.error("Le nom et le prénom ne doivent contenir que des lettres.")
                    elif verify_duplicate_user(st.session_state['user']['email']):
                        st.error("Un compte existe déjà avec cette adresse e-mail.")
                    else:
                        st.session_state['verifying'] = True
                        st.rerun()
                        
                st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.5;'>", unsafe_allow_html=True)
                
                if st.button("Retour à la connexion", use_container_width=True):
                    st.session_state['page'] = 'login'
                    st.rerun()
