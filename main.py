import streamlit as st
import tensorflow as tf
import numpy as np
import time
from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2,
    decode_predictions,
    preprocess_input,
)

# --- CONFIGURATION ET CHARGEMENT DES MODÈLES ---

# Chargement du modèle de diagnostic des maladies (spécifique aux plantes)
DISEASE_MODEL = tf.keras.models.load_model('training_model.keras')

# Chargement du modèle MobileNetV2 pré-entraîné sur ImageNet pour le filtrage OOD (Out-of-Distribution)
# Ce modèle sert de "garde-fou" pour identifier si l'image contient bien une plante/feuille.
FILTER_MODEL = MobileNetV2(weights="imagenet")

# Mots-clés utilisés par le filtre ImageNet pour valider qu'une image ressemble à une plante
PLANT_KEYWORDS = {
    "plant", "leaf", "bell_pepper", "cucumber", "zucchini", 
    "broccoli", "cauliflower", "corn", "mushroom", "granny_smith", 
    "daisy", "pot", "greenhouse"
}

REJECT_MSG = "Désolé, je ne suis pas capable de prédire sur ce genre d'image. Assurez-vous qu'il s'agit d'une feuille de plante (Tomate, Pomme de terre ou Poivron)."

# --- FONCTIONS DE PRÉDICTION ---

def plant_gate(test_image):
    """
    Filtre OOD : Vérifie si l'image téléchargée ressemble à une plante 
    en utilisant un modèle généraliste (MobileNetV2).
    """
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=[224, 224])
    arr = tf.keras.preprocessing.image.img_to_array(image)
    arr = preprocess_input(np.array([arr]))
    
    # Prédiction avec le modèle généraliste
    preds = FILTER_MODEL.predict(arr, verbose=0)
    top5 = decode_predictions(preds, top=5)[0]
    
    # On vérifie si l'un des 5 meilleurs labels contient un mot-clé lié aux plantes
    is_plant = False
    for _, label, _ in top5:
        label_norm = label.lower()
        if any(keyword in label_norm for keyword in PLANT_KEYWORDS):
            is_plant = True
            break
    return is_plant, top5

def model_prediction(test_image):
    """
    Prédiction de la maladie avec le modèle spécifique aux cultures cibles.
    """
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=[128, 128])
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])  # Conversion en batch
    prediction = DISEASE_MODEL.predict(input_arr, verbose=0)
    probs = prediction[0]
    result_index = int(np.argmax(probs))
    confidence = float(np.max(probs))
    return result_index, probs, confidence

# --- DICTIONNAIRE DES CONSEILS AGRICOLES ---

dispositions_agricoles = {
    "Pepper__bell___Bacterial_spot": "Retirer les feuilles infectées, éviter l'arrosage par le haut pour ne pas propager les bactéries, et appliquer un fongicide à base de cuivre.",
    "Pepper__bell___healthy": "Le plant est en excellente santé. Continuez une surveillance régulière et assurez une bonne aération entre les plants.",
    "Potato___Early_blight": "Pratiquer la rotation des cultures, éliminer les débris de récolte et appliquer des fongicides protecteurs dès les premiers signes.",
    "Potato___Late_blight": "URGENT : Éliminer et détruire les plants infectés. Améliorer le drainage du sol et utiliser des variétés résistantes à l'avenir.",
    "Potato___healthy": "Votre culture de pommes de terre est saine. Maintenez une fertilisation équilibrée pour renforcer sa résistance naturelle.",
    "Tomato_Bacterial_spot": "Éviter de manipuler les plants quand ils sont mouillés. Utiliser des semences certifiées et appliquer des traitements cupriques.",
    "Tomato_Early_blight": "Taillez les feuilles inférieures pour améliorer la circulation d'air. Le paillage du sol aide à réduire les éclaboussures de spores.",
    "Tomato_Late_blight": "CRITIQUE : Retirer les parties atteintes immédiatement. Réduire l'humidité ambiante et appliquer des fongicides spécifiques sans tarder.",
    "Tomato_Leaf_Mold": "Augmenter l'espacement entre les plants et assurer une ventilation maximale, surtout en serre. Éviter l'humidité foliaire nocturne.",
    "Tomato_Septoria_leaf_spot": "Supprimer les premières feuilles infectées à la base. Pratiquer une rotation de 2-3 ans sans solanacées.",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Favoriser les prédateurs naturels. En cas de forte attaque, utiliser du savon noir ou des huiles horticoles biologiques.",
    "Tomato__Target_Spot": "Éliminer les débris végétaux. Assurer une nutrition potassique adéquate pour renforcer les tissus de la plante.",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Lutter contre les aleurodes (mouches blanches) via des pièges jaunes ou des filets. Arracher les plants virusés.",
    "Tomato__Tomato_mosaic_virus": "Hygiène stricte : désinfecter les outils, ne pas fumer près des plants. Éliminer les plants infectés pour stopper la propagation.",
    "Tomato_healthy": "Plante saine. Bravo ! Continuez vos bonnes pratiques culturales actuelles."
}

# --- ÉTAT DE LA SESSION (HISTORIQUE) ---

if 'history' not in st.session_state:
    st.session_state.history = []

# --- BARRE LATÉRALE (SIDEBAR) ---

st.sidebar.title("PhytoDiag IA")
app_mode = st.sidebar.selectbox('Sélectionner une page', ['Accueil', 'À propos', 'Reconnaissance des maladies', 'Historique'])

# Curseur pour ajuster le seuil de confiance minimal (OOD basé sur le score)
conf_threshold = st.sidebar.slider("Seuil de confiance min (%)", 10, 100, 70, 5) / 100

# --- PAGE D'ACCUEIL ---

if (app_mode == "Accueil") :
    st.header('PhytoDiag IA')
    image_path = "./home_image.JPG"
    st.image(image_path, use_container_width=True)
    st.markdown("""
    #### Bienvenue dans le système de reconnaissance des maladies des plantes

    Notre mission est d'aider à identifier efficacement les maladies des plantes. Téléversez une image d'une plante et notre système l'analysera 
    pour détecter tout signe de maladie. Ensemble, protégeons nos cultures et assurons un avenir plus sain.
""")

# --- PAGE À PROPOS ---

if(app_mode =='À propos') :
    st.header("À propos")
    st.markdown(f"""
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
        Un seuil de confiance de **{conf_threshold*100:.0f}%** est également appliqué sur le diagnostic final.
    """)

# --- PAGE RECONNAISSANCE DES MALADIES ---

if(app_mode == 'Reconnaissance des maladies') :
    st.header("Reconnaissance des maladies")
    test_image = st.file_uploader('Choisissez une image...', type=['jpg', 'jpeg', 'png'])
    
    if test_image is not None:
        if(st.button('Afficher l\'image')) :
            st.image(test_image, use_container_width=True)
        
        # Bouton de prédiction avec logique OOD
        if(st.button('Prédire')) :
            with st.spinner("Analyse en cours (Vérification et Diagnostic)...") :
                # ÉTAPE 1 : Filtre OOD (Garde-fou visuel)
                is_plant_like, top5_filter = plant_gate(test_image)
                
                if not is_plant_like:
                    # L'image ne ressemble pas à une plante selon MobileNetV2
                    st.error(REJECT_MSG)
                    with st.expander("Pourquoi ce rejet ? (Détails techniques OOD)"):
                        st.write("Le filtre de détection visuelle a identifié ces objets :")
                        st.write([f"• {label} ({score*100:.1f}%)" for _, label, score in top5_filter])
                else:
                    # ÉTAPE 2 : Diagnostic de la maladie
                    result_index, probs, confidence = model_prediction(test_image)
                    
                    # ÉTAPE 3 : Validation du seuil de confiance
                    if confidence < conf_threshold:
                        st.warning(f"Confiance trop faible ({confidence*100:.1f}%). {REJECT_MSG}")
                    else:
                        # Affichage du résultat réussi
                        class_names = [
                            "Pepper__bell___Bacterial_spot", "Pepper__bell___healthy", 
                            "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",       
                            "Tomato_Bacterial_spot", "Tomato_Early_blight", "Tomato_Late_blight", 
                            "Tomato_Leaf_Mold", "Tomato_Septoria_leaf_spot",      
                            "Tomato_Spider_mites_Two_spotted_spider_mite", "Tomato__Target_Spot", 
                            "Tomato__Tomato_YellowLeaf__Curl_Virus", "Tomato__Tomato_mosaic_virus",       
                            "Tomato_healthy"
                        ]
                        predicted_label = class_names[result_index]
                        is_healthy = "healthy" in predicted_label.lower()
                        status_color = "#2ecc71" if is_healthy else "#e74c3c"
                        status_text = "🌿 Plante saine" if is_healthy else "⚠️ Plante malade"

                        st.markdown(
                            f"""
                            <div style="padding: 1rem; border-radius: 10px; background-color: {status_color}22; border: 2px solid {status_color}; text-align: center;">
                                <h3 style="margin: 0; color: {status_color};">{status_text}</h3>
                                <p style="margin: 0.3rem 0 0; font-size: 1.1rem;">Catégorie : <b>{predicted_label}</b></p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.metric("Confiance du diagnostic", f"{confidence * 100:.2f}%")

                        # Affichage des conseils agricoles
                        st.info(f"**Dispositions à prendre :** {dispositions_agricoles[predicted_label]}")

                        # Enregistrement dans l'historique
                        st.session_state.history.append({
                            "time": time.strftime("%H:%M:%S"),
                            "file": test_image.name,
                            "label": predicted_label,
                            "confidence": f"{confidence * 100:.1f}%",
                            "status": "Saine" if is_healthy else "Malade"
                        })

                        # Graphique des probabilités
                        st.write("Top-5 des prédictions :")
                        top_k = min(5, len(class_names))
                        sorted_idx = np.argsort(probs)[::-1][:top_k]
                        st.bar_chart({class_names[i]: probs[i] for i in sorted_idx})

# --- PAGE HISTORIQUE ---

if(app_mode == 'Historique') :
    st.header("Historique des analyses")
    if not st.session_state.history:
        st.write("Aucune analyse effectuée pour le moment.")
    else:
        if st.button("Effacer l'historique"):
            st.session_state.history = []
            st.rerun()
            
        for scan in reversed(st.session_state.history):
            icon = "🌿" if scan['status'] == "Saine" else "⚠️"
            st.markdown(f"""
            🕒 **{scan['time']}** | 📄 *{scan['file']}* | **{scan['label']}** | Confiance : **{scan['confidence']}** | {icon} *{scan['status']}*
            """)
            st.divider()

