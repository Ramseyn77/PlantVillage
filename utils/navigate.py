import streamlit as st

from utils.init_session import reset_session


def sidebar_navigation():

    # Logo / Titre
    st.sidebar.title("🌿 PhytoDiag IA")
    st.sidebar.caption("Diagnostic intelligent des maladies des plantes")

    st.sidebar.divider()

    # -------- Navigation principale --------
    st.sidebar.subheader("📍 Navigation")

    page = st.sidebar.radio(
        "Choisissez une page",
        [
            "🏠 Accueil",
            "Champs",
            "Cultures",
            "Analyses",
            "🔎 Reconnaissance",
            "📊 Historique",
        ]
    )

    st.sidebar.divider()

    # -------- Informations --------
    st.sidebar.subheader("ℹ️ Informations")

    info_page = st.sidebar.radio(
        "À propos du projet",
        [
            "📘 À propos",
        ]
    )

    st.sidebar.divider()

    # -------- Compte utilisateur --------
    st.sidebar.subheader("👤 Compte")
    if st.sidebar.button("Logout"):
        reset_session()
        st.rerun()
    user_page = st.sidebar.radio(
        "Gestion du compte",
        [
            "🔐 Connexion",
        ]
    )

    st.sidebar.divider()

    # -------- Footer --------
    st.sidebar.caption("Version 1.0")
    st.sidebar.caption("© 2026 PhytoDiag IA")

    # Gestion de la page active
    if "Accueil" in page:
        return "Accueil"
    elif "Reconnaissance" in page:
        return "Reconnaissance"
    elif "Historique" in page:
        return "Historique"
    elif "Champs" in page:
        return "Champs"
    elif "À propos" in info_page:
        return "À propos"
    elif "Connexion" in user_page:
        return "Connexion"