import streamlit as st
import tensorflow as tf
import numpy as np
import time
import cv2
import pandas as pd
import io
from PIL import Image
from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2,
    decode_predictions,
    preprocess_input,
)

# --- CONFIGURATION ET CHARGEMENT DES MODELES ---

DISEASE_MODEL = tf.keras.models.load_model('training_model.keras')
FILTER_MODEL = MobileNetV2(weights="imagenet")

# "tomato" et "potato" ajoutés (absents dans main.py)
PLANT_KEYWORDS = {
    "plant", "leaf", "bell_pepper", "cucumber", "zucchini",
    "broccoli", "cauliflower", "corn", "mushroom", "granny_smith",
    "daisy", "pot", "greenhouse", "tomato", "potato"
}

REJECT_MSG = "Désolé, je ne suis pas capable de prédire sur ce genre d'image. Assurez-vous qu'il s'agit d'une feuille de plante (Tomate, Pomme de terre ou Poivron)."

CLASS_NAMES = [
    "Pepper__bell___Bacterial_spot", "Pepper__bell___healthy",
    "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
    "Tomato_Bacterial_spot", "Tomato_Early_blight", "Tomato_Late_blight",
    "Tomato_Leaf_Mold", "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite", "Tomato__Target_Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus", "Tomato__Tomato_mosaic_virus",
    "Tomato_healthy"
]

# --- NIVEAUX DE SEVERITE PAR MALADIE ---

SEVERITY = {
    "Pepper__bell___Bacterial_spot": "Moyen",
    "Pepper__bell___healthy": None,
    "Potato___Early_blight": "Moyen",
    "Potato___Late_blight": "Eleve",
    "Potato___healthy": None,
    "Tomato_Bacterial_spot": "Moyen",
    "Tomato_Early_blight": "Moyen",
    "Tomato_Late_blight": "Critique",
    "Tomato_Leaf_Mold": "Faible",
    "Tomato_Septoria_leaf_spot": "Moyen",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Moyen",
    "Tomato__Target_Spot": "Moyen",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Eleve",
    "Tomato__Tomato_mosaic_virus": "Eleve",
    "Tomato_healthy": None,
}

SEVERITY_COLOR = {
    "Faible":   "#f39c12",
    "Moyen":    "#e67e22",
    "Eleve":    "#e74c3c",
    "Critique": "#8e1010",
}

# --- CONSEILS AGRICOLES ---

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

# =============================================================================
# NOUVELLE FONCTIONNALITE 1 — NORMALISATION COLORIMETRIQUE (SOLUTION 2)
# Aligne l'image d'entrée sur le style visuel du dataset PlantVillage via :
#   - CLAHE sur le canal de luminance (améliore le contraste local)
#   - Normalisation statistique des canaux RGB vers les cibles PlantVillage
# =============================================================================

# Statistiques cibles estimées du dataset PlantVillage (proches d'ImageNet)
_PV_TARGET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_PV_TARGET_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def normalize_to_plantvillage_style(image_pil):
    """
    Normalise une image PIL pour l'aligner sur le style visuel PlantVillage.
    Retourne une image PIL normalisée.
    """
    img_np = np.array(image_pil.convert("RGB"), dtype=np.uint8)

    # Etape 1 : CLAHE sur le canal L (espace LAB) pour égaliser le contraste
    lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB)
    l_ch, a_ch, b_ch = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_ch = clahe.apply(l_ch)
    img_enhanced = cv2.cvtColor(cv2.merge([l_ch, a_ch, b_ch]), cv2.COLOR_LAB2RGB).astype(np.float32)

    # Etape 2 : Normalisation statistique canal par canal
    img_norm = img_enhanced / 255.0
    src_mean = img_norm.mean(axis=(0, 1))
    src_std  = img_norm.std(axis=(0, 1)) + 1e-6
    img_aligned = (img_norm - src_mean) / src_std * _PV_TARGET_STD + _PV_TARGET_MEAN
    img_aligned = np.clip(img_aligned, 0.0, 1.0)

    return Image.fromarray((img_aligned * 255).astype(np.uint8))


# =============================================================================
# NOUVELLE FONCTIONNALITE 2 — GRAD-CAM
# Génère une carte de chaleur montrant les zones qui influencent la décision.
# =============================================================================

def compute_gradcam(model, input_array, class_idx):
    """
    Calcule la heatmap Grad-CAM pour la classe `class_idx`.
    `input_array` : batch numpy de shape (1, H, W, 3).
    Retourne un tableau numpy 2D normalisé [0, 1] ou None si impossible.
    """
    last_conv_name = None
    for layer in reversed(model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            last_conv_name = layer.name
            break
    if last_conv_name is None:
        return None

    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[model.get_layer(last_conv_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        inputs = tf.cast(input_array, tf.float32)
        conv_outputs, predictions = grad_model(inputs)
        loss = predictions[:, class_idx]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    heatmap = tf.squeeze(conv_outputs[0] @ pooled_grads[..., tf.newaxis])
    heatmap = tf.maximum(heatmap, 0)
    heatmap = heatmap / (tf.math.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy()


def overlay_gradcam(image_pil, heatmap, alpha=0.4):
    """
    Superpose la heatmap Grad-CAM sur l'image PIL.
    Retourne une image PIL avec la superposition.
    """
    img_np = np.array(image_pil.resize((128, 128)))
    heatmap_resized = cv2.resize(heatmap, (128, 128))
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    overlay = np.clip(alpha * heatmap_colored + (1 - alpha) * img_np, 0, 255).astype(np.uint8)
    return Image.fromarray(overlay)


# --- FONCTIONS DE PREDICTION (identiques à main.py, adaptées pour PIL) ---

def plant_gate(image_pil):
    """Filtre OOD via MobileNetV2 — accepte directement un objet PIL."""
    arr = tf.keras.preprocessing.image.img_to_array(image_pil.convert("RGB").resize((224, 224)))
    arr = preprocess_input(np.array([arr]))
    preds = FILTER_MODEL.predict(arr, verbose=0)
    top5 = decode_predictions(preds, top=5)[0]
    is_plant = any(
        any(kw in label.lower() for kw in PLANT_KEYWORDS)
        for _, label, _ in top5
    )
    return is_plant, top5


def model_prediction(image_pil):
    """Diagnostic CNN — retourne index, probabilités, confiance et le batch array."""
    input_arr = tf.keras.preprocessing.image.img_to_array(image_pil.resize((128, 128)))
    input_arr_batch = np.array([input_arr])
    probs = DISEASE_MODEL.predict(input_arr_batch, verbose=0)[0]
    result_index = int(np.argmax(probs))
    confidence = float(np.max(probs))
    return result_index, probs, confidence, input_arr_batch


def run_diagnosis(image_pil, conf_threshold, use_normalization, show_gradcam):
    """
    Pipeline complet :
      1. Filtre OOD
      2. Normalisation colorimétrique (optionnelle)
      3. Diagnostic CNN
      4. Validation du seuil de confiance
      5. Grad-CAM (optionnel)
    Retourne un dict de résultats.
    """
    is_plant, top5_filter = plant_gate(image_pil)
    if not is_plant:
        return {"rejected": True, "reason": "ood", "top5": top5_filter}

    processed_image = normalize_to_plantvillage_style(image_pil) if use_normalization else image_pil

    result_index, probs, confidence, input_arr = model_prediction(processed_image)

    if confidence < conf_threshold:
        return {"rejected": True, "reason": "confidence", "confidence": confidence}

    predicted_label = CLASS_NAMES[result_index]
    is_healthy = "healthy" in predicted_label.lower()

    gradcam_image = None
    if show_gradcam:
        heatmap = compute_gradcam(DISEASE_MODEL, input_arr, result_index)
        if heatmap is not None:
            gradcam_image = overlay_gradcam(processed_image, heatmap)

    return {
        "rejected":        False,
        "label":           predicted_label,
        "confidence":      confidence,
        "probs":           probs,
        "is_healthy":      is_healthy,
        "processed_image": processed_image,
        "gradcam_image":   gradcam_image,
        "severity":        SEVERITY.get(predicted_label),
    }


# --- ETAT DE LA SESSION ---

if 'history' not in st.session_state:
    st.session_state.history = []

# --- BARRE LATERALE ---

st.sidebar.title("PhytoDiag IA v2")
app_mode = st.sidebar.selectbox(
    'Sélectionner une page',
    ['Accueil', 'À propos', 'Reconnaissance des maladies', 'Analyse par lot', 'Historique']
)

conf_threshold = st.sidebar.slider("Seuil de confiance min (%)", 10, 100, 70, 5) / 100

st.sidebar.markdown("---")
st.sidebar.markdown("**Options avancées**")

use_normalization = st.sidebar.toggle(
    "Normalisation colorimétrique",
    value=True,
    help="Aligne l'image sur le style visuel du dataset PlantVillage (CLAHE + normalisation statistique). Recommandé pour les photos prises en extérieur."
)

show_gradcam = st.sidebar.toggle(
    "Afficher Grad-CAM",
    value=False,
    help="Superpose une carte de chaleur sur l'image pour visualiser les zones qui ont influencé le diagnostic."
)

# --- PAGE ACCUEIL ---

if app_mode == "Accueil":
    st.header('PhytoDiag IA v2')
    st.image("./home_image.JPG", use_container_width=True)
    st.markdown("""
    #### Bienvenue dans le système de reconnaissance des maladies des plantes

    Notre mission est d'aider à identifier efficacement les maladies des plantes. Téléversez une image d'une plante et notre système l'analysera
    pour détecter tout signe de maladie. Ensemble, protégeons nos cultures et assurons un avenir plus sain.
    """)

# --- PAGE A PROPOS ---

if app_mode == 'À propos':
    st.header("À propos")
    st.markdown(f"""
    ### À propos du projet
    #### 1. Objectif
        Développer une application web qui détecte automatiquement l'état de santé d'une plante à partir d'une
        image (saine ou malade) et identifie la maladie probable.
    #### 2. Intelligence Artificielle et OOD
        Le projet utilise deux modèles :
        - **Modèle de Diagnostic** : CNN entraîné sur PlantVillage.
        - **Filtre OOD (MobileNetV2)** : Utilisé comme barrière de sécurité pour rejeter les images non-végétales.
    #### 3. Fonctionnement du Filtre
        Toute image téléchargée passe d'abord par un filtre ImageNet. Si l'IA ne reconnaît pas de caractéristiques
        liées aux plantes (mots-clés : leaf, plant, tomato, potato...), la prédiction est bloquée.
        Un seuil de confiance de **{conf_threshold*100:.0f}%** est également appliqué sur le diagnostic final.
    #### 4. Normalisation colorimétrique (nouveau)
        Avant le diagnostic, l'image est normalisée via CLAHE (égalisation adaptative du contraste) puis alignée
        statistiquement sur le style visuel PlantVillage. Cela réduit l'écart entre photos terrain et données d'entraînement.
    #### 5. Grad-CAM (nouveau)
        La carte d'activation Grad-CAM superpose une heatmap sur l'image pour montrer quelles zones de la feuille
        ont le plus influencé la décision du modèle — outil d'interprétabilité et de validation.
    #### 6. Niveau de sévérité (nouveau)
        Chaque maladie est associée à un niveau de sévérité prédéfini (Faible / Moyen / Élevé / Critique)
        affiché avec l'indicateur coloré pour prioriser les interventions.
    #### 7. Analyse par lot (nouveau)
        Téléversez plusieurs images simultanément pour obtenir un rapport groupé exportable en CSV.
    """)

# --- PAGE RECONNAISSANCE DES MALADIES ---

if app_mode == 'Reconnaissance des maladies':
    st.header("Reconnaissance des maladies")
    test_image = st.file_uploader('Choisissez une image...', type=['jpg', 'jpeg', 'png'])

    if test_image is not None:
        image_pil = Image.open(test_image)

        # Apercu avant / après normalisation
        if use_normalization:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Image originale")
                st.image(image_pil, use_container_width=True)
            with col2:
                st.subheader("Après normalisation")
                st.image(normalize_to_plantvillage_style(image_pil), use_container_width=True)
        else:
            st.image(image_pil, use_container_width=True)

        if st.button('Prédire'):
            with st.spinner("Analyse en cours (Vérification et Diagnostic)..."):
                result = run_diagnosis(image_pil, conf_threshold, use_normalization, show_gradcam)

            if result["rejected"]:
                if result["reason"] == "ood":
                    st.error(REJECT_MSG)
                    with st.expander("Pourquoi ce rejet ? (Détails techniques OOD)"):
                        st.write("Le filtre de détection visuelle a identifié ces objets :")
                        st.write([f"• {label} ({score*100:.1f}%)" for _, label, score in result["top5"]])
                else:
                    st.warning(f"Confiance trop faible ({result['confidence']*100:.1f}%). {REJECT_MSG}")
            else:
                predicted_label = result["label"]
                is_healthy      = result["is_healthy"]
                confidence      = result["confidence"]
                severity        = result["severity"]

                status_color = "#2ecc71" if is_healthy else "#e74c3c"
                status_text  = "Plante saine" if is_healthy else "Plante malade"

                st.markdown(
                    f"""
                    <div style="padding:1rem;border-radius:10px;background-color:{status_color}22;border:2px solid {status_color};text-align:center;">
                        <h3 style="margin:0;color:{status_color};">{status_text}</h3>
                        <p style="margin:0.3rem 0 0;font-size:1.1rem;">Catégorie : <b>{predicted_label}</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col_m1, col_m2 = st.columns(2)
                col_m1.metric("Confiance du diagnostic", f"{confidence * 100:.2f}%")

                if severity:
                    sev_color = SEVERITY_COLOR.get(severity, "#888")
                    col_m2.markdown(
                        f'<div style="padding:0.5rem 1rem;border-radius:8px;background:{sev_color}22;border:1.5px solid {sev_color};text-align:center;margin-top:0.5rem"><b>Sévérité : {severity}</b></div>',
                        unsafe_allow_html=True
                    )

                st.info(f"**Dispositions à prendre :** {dispositions_agricoles[predicted_label]}")

                # Grad-CAM
                if show_gradcam and result["gradcam_image"] is not None:
                    st.subheader("Zones d'attention (Grad-CAM)")
                    st.image(result["gradcam_image"], use_container_width=True)
                    st.caption("Les zones rouges/jaunes indiquent les régions qui ont le plus influencé la prédiction.")

                # Top-5 probabilités
                st.write("Top-5 des prédictions :")
                sorted_idx = np.argsort(result["probs"])[::-1][:5]
                st.bar_chart({CLASS_NAMES[i]: float(result["probs"][i]) for i in sorted_idx})

                # Enregistrement historique
                st.session_state.history.append({
                    "time":       time.strftime("%H:%M:%S"),
                    "file":       test_image.name,
                    "label":      predicted_label,
                    "confidence": f"{confidence * 100:.1f}%",
                    "status":     "Saine" if is_healthy else "Malade",
                    "severity":   severity or "—",
                    "normalized": "Oui" if use_normalization else "Non",
                })

# =============================================================================
# NOUVELLE FONCTIONNALITE 3 — ANALYSE PAR LOT
# Permet de téléverser plusieurs images et d'obtenir un tableau récapitulatif
# exportable en CSV.
# =============================================================================

if app_mode == 'Analyse par lot':
    st.header("Analyse par lot")
    st.info("Téléversez plusieurs images en une seule fois pour obtenir un rapport groupé.")

    uploaded_files = st.file_uploader(
        "Choisissez plusieurs images...",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True
    )

    if uploaded_files and st.button(f"Analyser les {len(uploaded_files)} image(s)"):
        batch_results = []
        progress_bar  = st.progress(0)

        for i, f in enumerate(uploaded_files):
            image_pil = Image.open(f)
            result    = run_diagnosis(image_pil, conf_threshold, use_normalization, False)

            if result["rejected"]:
                row = {
                    "Fichier":    f.name,
                    "Statut":     "Rejeté",
                    "Diagnostic": "—",
                    "Confiance":  "—",
                    "Sévérité":   "—",
                }
            else:
                row = {
                    "Fichier":    f.name,
                    "Statut":     "Saine" if result["is_healthy"] else "Malade",
                    "Diagnostic": result["label"],
                    "Confiance":  f"{result['confidence']*100:.1f}%",
                    "Sévérité":   result["severity"] or "—",
                }
                st.session_state.history.append({
                    "time":       time.strftime("%H:%M:%S"),
                    "file":       f.name,
                    "label":      result["label"],
                    "confidence": f"{result['confidence']*100:.1f}%",
                    "status":     "Saine" if result["is_healthy"] else "Malade",
                    "severity":   result["severity"] or "—",
                    "normalized": "Oui" if use_normalization else "Non",
                })

            batch_results.append(row)
            progress_bar.progress((i + 1) / len(uploaded_files))

        df = pd.DataFrame(batch_results)
        st.dataframe(df, use_container_width=True)

        # Statistiques récapitulatives
        total    = len(batch_results)
        healthy  = sum(1 for r in batch_results if r["Statut"] == "Saine")
        diseased = sum(1 for r in batch_results if r["Statut"] == "Malade")
        rejected = sum(1 for r in batch_results if r["Statut"] == "Rejeté")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total analysé", total)
        c2.metric("Saines",  healthy)
        c3.metric("Malades", diseased)
        c4.metric("Rejetées", rejected)

        # Export CSV du rapport
        csv_buf = io.StringIO()
        df.to_csv(csv_buf, index=False)
        st.download_button(
            label="Télécharger le rapport CSV",
            data=csv_buf.getvalue(),
            file_name=f"rapport_phytodiag_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# --- PAGE HISTORIQUE ---

if app_mode == 'Historique':
    st.header("Historique des analyses")

    if not st.session_state.history:
        st.write("Aucune analyse effectuée pour le moment.")
    else:
        col_clear, col_export = st.columns(2)

        with col_clear:
            if st.button("Effacer l'historique"):
                st.session_state.history = []
                st.rerun()

        with col_export:
            df_hist  = pd.DataFrame(st.session_state.history)
            csv_hist = io.StringIO()
            df_hist.to_csv(csv_hist, index=False)
            st.download_button(
                label="Exporter l'historique CSV",
                data=csv_hist.getvalue(),
                file_name=f"historique_phytodiag_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        for scan in reversed(st.session_state.history):
            icon    = "Saine" if scan['status'] == "Saine" else "Malade"
            sev_str = f"| Sévérité : **{scan['severity']}**" if scan.get('severity', '—') != '—' else ""
            norm_str = f"| Normalisée : *{scan.get('normalized', '—')}*"
            st.markdown(f"""
            **{scan['time']}** | *{scan['file']}* | **{scan['label']}** | Confiance : **{scan['confidence']}** {sev_str} {norm_str} | *{icon}*
            """)
            st.divider()
