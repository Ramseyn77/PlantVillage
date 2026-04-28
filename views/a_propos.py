import streamlit as st

def show():
    st.header("À propos")
    st.markdown("""
    ### À propos du projet
    #### 1. Objectif
        Développer une application web qui détecte automatiquement l’état de santé d’une plante à partir d’une 
        image (saine ou malade) et identifie la maladie probable.
    #### 2. Intelligence Artificielle et OOD
        Le projet utilise deux modèles :
        - **Modèle de Diagnostic** : CNN entraîné sur PlantVillage.
        - **Filtre OOD (MobileNetV2)** : Utilisé comme barrière de sécurité pour rejeter les images non-végétales.
    #### 3. Fonctionnement du Filtre
        Toute image téléchargée passe d'abord par un filtre ImageNet. Si l'IA ne reconnaît pas de caractéristiques 
        liées aux plantes (mots-clés : leaf, plant, etc.), la prédiction est bloquée pour éviter les faux positifs.
        Un seuil de confiance est également appliqué sur le diagnostic final.
    """)