import streamlit as st
from utils.style import card

def show():
    # Hero Section
    st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-radius: 20px; color: white; margin-bottom: 3rem; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2); position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50%; left: -10%; width: 50%; height: 200%; background: radial-gradient(circle, rgba(16,185,129,0.15) 0%, rgba(0,0,0,0) 70%); transform: rotate(30deg);"></div>
            <h1 style="color: white; font-size: 3.5rem; font-weight: 800; margin-bottom: 1rem; position: relative; z-index: 1;">PhytoDiag IA <span style="color: #10b981;">🌿</span></h1>
            <p style="font-size: 1.2rem; max-width: 650px; margin: 0 auto; opacity: 0.9; line-height: 1.6; position: relative; z-index: 1;">
                L'intelligence artificielle au service de vos cultures. Détectez les maladies avec précision, obtenez des recommandations instantanées et protégez vos rendements.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem; color: #1e293b;'>Pourquoi choisir PhytoDiag ?</h2>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    with cols[0]:
        card("Analyse Instantanée", "Soumettez une photo d'une feuille et obtenez un diagnostic en quelques secondes grâce à notre réseau de neurones avancé.", "🚀")
    with cols[1]:
        card("Gestion des Champs", "Organisez vos cultures par champ et suivez l'historique des maladies pour prévenir les futures épidémies.", "📊")
    with cols[2]:
        card("Recommandations Expertes", "Recevez des conseils de traitement spécifiques et adaptés à chaque maladie identifiée pour agir rapidement.", "💊")

    st.write("<br><br>", unsafe_allow_html=True)
    
    # CTA Section
    st.markdown("""
        <div style="background-color: #ecfdf5; border: 1px solid #10b981; border-radius: 16px; padding: 2rem; text-align: center;">
            <h3 style="color: #065f46; margin-top: 0;">Prêt à commencer ?</h3>
            <p style="color: #047857; font-size: 1.1rem;">Utilisez le menu latéral pour naviguer vers l'outil de <b>Reconnaissance</b> ou gérez vos <b>Champs</b>.</p>
        </div>
    """, unsafe_allow_html=True)