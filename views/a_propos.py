import streamlit as st

def show():
    st.markdown("""
<div style="max-width: 800px; margin: 0 auto;">
    <h1 style="color: #1e293b; margin-bottom: 2rem;">À propos du projet</h1>
    
    <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 2rem; border: 1px solid #e2e8f0;">
        <h3 style="color: #10b981; margin-top: 0;">1. Objectif</h3>
        <p style="color: #475569; line-height: 1.7; font-size: 1.05rem;">
            Développer une application web moderne qui détecte automatiquement l’état de santé d’une plante à partir d’une 
            image. L'application identifie si la plante est saine ou malade, et précise la maladie probable pour aider les agriculteurs à agir vite.
        </p>
    </div>

    <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 2rem; border: 1px solid #e2e8f0;">
        <h3 style="color: #3b82f6; margin-top: 0;">2. Intelligence Artificielle & Sécurité (OOD)</h3>
        <p style="color: #475569; line-height: 1.7; font-size: 1.05rem; margin-bottom: 1rem;">
            Le projet utilise une architecture hybride à deux modèles pour garantir des prédictions robustes :
        </p>
        <ul style="color: #475569; line-height: 1.7; font-size: 1.05rem;">
            <li><b>Modèle de Diagnostic (CNN)</b> : Un réseau de neurones entraîné sur la base de données <i>PlantVillage</i> pour identifier finement les maladies.</li>
            <li><b>Filtre OOD (MobileNetV2)</b> : Utilisé comme barrière de sécurité (Out-Of-Distribution) pour rejeter les images non-végétales (visages, voitures, etc.) avant même l'analyse de maladie.</li>
        </ul>
    </div>

    <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
        <h3 style="color: #f59e0b; margin-top: 0;">3. Flux d'analyse</h3>
        <p style="color: #475569; line-height: 1.7; font-size: 1.05rem;">
            Toute image téléchargée passe d'abord par le filtre ImageNet. Si l'IA ne reconnaît pas de caractéristiques 
            liées aux plantes (mots-clés : leaf, plant, etc.), la prédiction est bloquée pour éviter les faux positifs et les recommandations hasardeuses. 
            Enfin, un seuil de confiance est appliqué sur le diagnostic final pour s'assurer que le modèle est certain de sa décision.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)