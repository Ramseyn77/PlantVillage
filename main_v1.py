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
# NOUVELLE FONCTIONNALITE 1 — SEGMENTATION DE LA FEUILLE (SOLUTION 1)
# Isole la feuille de son arrière-plan naturel et la place sur fond blanc,
# imitant ainsi le style visuel du dataset PlantVillage.
#
# Pipeline :
#   1. Détection de la feuille par seuillage HSV (vert/jaune/brun)
#   2. Raffinage du masque avec GrabCut d'OpenCV
#   3. Nettoyage morphologique (fermeture + dilatation)
#   4. Application du masque sur fond blanc
# =============================================================================

def segment_leaf(image_pil):
    """
    Segmente la feuille dans l'image PIL et retourne deux images PIL :
      - image avec la feuille isolée sur fond blanc
      - masque binaire pour visualisation
    En cas d'échec de GrabCut, retourne un fallback par seuillage HSV seul.
    """
    img_rgb = np.array(image_pil.convert("RGB"))
    h, w    = img_rgb.shape[:2]

    # --- Etape 1 : masque initial par seuillage HSV ---
    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

    # Plages couvrant les tons verts, jaunes et bruns des feuilles
    ranges = [
        ((25,  20,  20), (95, 255, 255)),   # vert / jaune-vert
        ((10,  20,  20), (25, 255, 255)),    # jaune / brun clair
        ((0,   10,  30), (20, 180, 200)),    # brun foncé / feuille séchée
    ]
    hsv_mask = np.zeros((h, w), dtype=np.uint8)
    for lo, hi in ranges:
        hsv_mask |= cv2.inRange(img_hsv, np.array(lo), np.array(hi))

    # Nettoyage morphologique du masque HSV
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    hsv_mask = cv2.morphologyEx(hsv_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    hsv_mask = cv2.morphologyEx(hsv_mask, cv2.MORPH_DILATE, kernel, iterations=1)

    # --- Etape 2 : GrabCut guidé par le masque HSV ---
    # GrabCut nécessite un rectangle englobant la région d'intérêt
    coords = cv2.findNonZero(hsv_mask)
    if coords is not None and coords.shape[0] > 100:
        x_min, y_min = coords[:, 0, 0].min(), coords[:, 0, 1].min()
        x_max, y_max = coords[:, 0, 0].max(), coords[:, 0, 1].max()

        # Marges pour éviter de couper la feuille
        margin = 10
        x_min = max(0, x_min - margin)
        y_min = max(0, y_min - margin)
        x_max = min(w - 1, x_max + margin)
        y_max = min(h - 1, y_max + margin)

        rect = (x_min, y_min, x_max - x_min, y_max - y_min)

        if rect[2] > 10 and rect[3] > 10:
            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)
            gc_mask   = np.zeros((h, w), dtype=np.uint8)

            # Initialisation du masque GrabCut avec le masque HSV
            gc_mask[hsv_mask > 0]  = cv2.GC_PR_FGD   # probablement feuille
            gc_mask[hsv_mask == 0] = cv2.GC_PR_BGD   # probablement fond

            try:
                cv2.grabCut(
                    cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR),
                    gc_mask, rect, bgd_model, fgd_model,
                    iterCount=5, mode=cv2.GC_INIT_WITH_MASK
                )
                final_mask = np.where(
                    (gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD), 255, 0
                ).astype(np.uint8)

                # Nettoyage final
                final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
                final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_DILATE, kernel, iterations=1)

                # Si GrabCut a produit un masque raisonnable, on l'utilise
                coverage = final_mask.sum() / (h * w * 255)
                if 0.05 < coverage < 0.95:
                    use_mask = final_mask
                else:
                    use_mask = hsv_mask  # fallback
            except Exception:
                use_mask = hsv_mask      # fallback si GrabCut échoue
        else:
            use_mask = hsv_mask
    else:
        use_mask = hsv_mask

    # --- Etape 3 : Application du masque sur fond blanc ---
    white_bg = np.ones_like(img_rgb, dtype=np.uint8) * 255
    mask_3ch = cv2.cvtColor(use_mask, cv2.COLOR_GRAY2RGB)
    segmented = np.where(mask_3ch > 0, img_rgb, white_bg).astype(np.uint8)

    return Image.fromarray(segmented), Image.fromarray(use_mask)


# --- GRAD-CAM ---

def compute_gradcam(model, input_array, class_idx):
    """
    Calcule la heatmap Grad-CAM pour la classe `class_idx`.
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

    grads       = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    heatmap     = tf.squeeze(conv_outputs[0] @ pooled_grads[..., tf.newaxis])
    heatmap     = tf.maximum(heatmap, 0)
    heatmap     = heatmap / (tf.math.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy()


def overlay_gradcam(image_pil, heatmap, alpha=0.4):
    """Superpose la heatmap Grad-CAM sur l'image PIL."""
    img_np          = np.array(image_pil.resize((128, 128)))
    heatmap_resized = cv2.resize(heatmap, (128, 128))
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    overlay         = np.clip(alpha * heatmap_colored + (1 - alpha) * img_np, 0, 255).astype(np.uint8)
    return Image.fromarray(overlay)


# --- FONCTIONS DE PREDICTION ---

def plant_gate(image_pil):
    """Filtre OOD via MobileNetV2 — accepte directement un objet PIL."""
    arr  = tf.keras.preprocessing.image.img_to_array(image_pil.convert("RGB").resize((224, 224)))
    arr  = preprocess_input(np.array([arr]))
    preds = FILTER_MODEL.predict(arr, verbose=0)
    top5  = decode_predictions(preds, top=5)[0]
    is_plant = any(
        any(kw in label.lower() for kw in PLANT_KEYWORDS)
        for _, label, _ in top5
    )
    return is_plant, top5


def model_prediction(image_pil):
    """Diagnostic CNN — retourne index, probabilités, confiance et le batch array."""
    input_arr       = tf.keras.preprocessing.image.img_to_array(image_pil.resize((128, 128)))
    input_arr_batch = np.array([input_arr])
    probs           = DISEASE_MODEL.predict(input_arr_batch, verbose=0)[0]
    result_index    = int(np.argmax(probs))
    confidence      = float(np.max(probs))
    return result_index, probs, confidence, input_arr_batch


def run_diagnosis(image_pil, conf_threshold, use_segmentation, show_gradcam):
    """
    Pipeline complet :
      1. Filtre OOD
      2. Segmentation de la feuille (optionnelle)
      3. Diagnostic CNN
      4. Validation du seuil de confiance
      5. Grad-CAM (optionnel)
    Retourne un dict de résultats.
    """
    is_plant, top5_filter = plant_gate(image_pil)
    if not is_plant:
        return {"rejected": True, "reason": "ood", "top5": top5_filter}

    segmented_image = None
    mask_image      = None
    if use_segmentation:
        segmented_image, mask_image = segment_leaf(image_pil)
        processed_image = segmented_image
    else:
        processed_image = image_pil

    result_index, probs, confidence, input_arr = model_prediction(processed_image)

    if confidence < conf_threshold:
        return {"rejected": True, "reason": "confidence", "confidence": confidence}

    predicted_label = CLASS_NAMES[result_index]
    is_healthy      = "healthy" in predicted_label.lower()

    gradcam_image = None
    if show_gradcam:
        heatmap = compute_gradcam(DISEASE_MODEL, input_arr, result_index)
        if heatmap is not None:
            gradcam_image = overlay_gradcam(processed_image, heatmap)

    return {
        "rejected":         False,
        "label":            predicted_label,
        "confidence":       confidence,
        "probs":            probs,
        "is_healthy":       is_healthy,
        "segmented_image":  segmented_image,
        "mask_image":       mask_image,
        "gradcam_image":    gradcam_image,
        "severity":         SEVERITY.get(predicted_label),
    }


# --- ETAT DE LA SESSION ---

if 'history' not in st.session_state:
    st.session_state.history = []

# --- BARRE LATERALE ---

st.sidebar.title("PhytoDiag IA v1")
app_mode = st.sidebar.selectbox(
    'Sélectionner une page',
    ['Accueil', 'À propos', 'Reconnaissance des maladies', 'Analyse par lot', 'Historique']
)

conf_threshold = st.sidebar.slider("Seuil de confiance min (%)", 10, 100, 70, 5) / 100

st.sidebar.markdown("---")
st.sidebar.markdown("**Options avancées**")

use_segmentation = st.sidebar.toggle(
    "Segmentation de la feuille",
    value=True,
    help="Isole la feuille de son arrière-plan et la place sur fond blanc, imitant le style du dataset PlantVillage. Recommandé pour les photos prises en extérieur."
)

show_mask = st.sidebar.toggle(
    "Afficher le masque de segmentation",
    value=False,
    help="Affiche le masque binaire utilisé pour isoler la feuille."
)

show_gradcam = st.sidebar.toggle(
    "Afficher Grad-CAM",
    value=False,
    help="Superpose une carte de chaleur sur l'image pour visualiser les zones qui ont influencé le diagnostic."
)

# --- PAGE ACCUEIL ---

if app_mode == "Accueil":
    st.header('PhytoDiag IA v1')
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
    #### 4. Segmentation de la feuille (nouveau)
        Avant le diagnostic, la feuille est isolée de l'arrière-plan en deux étapes :
        - **Seuillage HSV** : détecte les tons verts, jaunes et bruns caractéristiques des feuilles.
        - **GrabCut** : algorithme d'OpenCV qui raffine le contour de la feuille itérativement.
        La feuille est ensuite placée sur fond blanc, comme dans le dataset PlantVillage.
    #### 5. Grad-CAM (nouveau)
        La carte d'activation Grad-CAM montre quelles zones de la feuille ont le plus influencé la décision.
    #### 6. Niveau de sévérité (nouveau)
        Chaque maladie est associée à un niveau (Faible / Moyen / Élevé / Critique) avec indicateur coloré.
    #### 7. Analyse par lot (nouveau)
        Téléversez plusieurs images simultanément pour un rapport groupé exportable en CSV.
    """)

# --- PAGE RECONNAISSANCE DES MALADIES ---

if app_mode == 'Reconnaissance des maladies':
    st.header("Reconnaissance des maladies")
    test_image = st.file_uploader('Choisissez une image...', type=['jpg', 'jpeg', 'png'])

    if test_image is not None:
        image_pil = Image.open(test_image)

        # Apercu : original + segmenté (+ masque optionnel)
        if use_segmentation:
            seg_preview, mask_preview = segment_leaf(image_pil)

            if show_mask:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.subheader("Image originale")
                    st.image(image_pil, use_container_width=True)
                with col2:
                    st.subheader("Feuille segmentée")
                    st.image(seg_preview, use_container_width=True)
                with col3:
                    st.subheader("Masque")
                    st.image(mask_preview, use_container_width=True)
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Image originale")
                    st.image(image_pil, use_container_width=True)
                with col2:
                    st.subheader("Feuille segmentée")
                    st.image(seg_preview, use_container_width=True)
        else:
            st.image(image_pil, use_container_width=True)

        if st.button('Prédire'):
            with st.spinner("Analyse en cours (Segmentation et Diagnostic)..."):
                result = run_diagnosis(image_pil, conf_threshold, use_segmentation, show_gradcam)

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
                    "segmenté":   "Oui" if use_segmentation else "Non",
                })

# --- ANALYSE PAR LOT ---

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
            result    = run_diagnosis(image_pil, conf_threshold, use_segmentation, False)

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
                    "segmenté":   "Oui" if use_segmentation else "Non",
                })

            batch_results.append(row)
            progress_bar.progress((i + 1) / len(uploaded_files))

        df = pd.DataFrame(batch_results)
        st.dataframe(df, use_container_width=True)

        total    = len(batch_results)
        healthy  = sum(1 for r in batch_results if r["Statut"] == "Saine")
        diseased = sum(1 for r in batch_results if r["Statut"] == "Malade")
        rejected = sum(1 for r in batch_results if r["Statut"] == "Rejeté")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total analysé", total)
        c2.metric("Saines",  healthy)
        c3.metric("Malades", diseased)
        c4.metric("Rejetées", rejected)

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
            icon     = "Saine" if scan['status'] == "Saine" else "Malade"
            sev_str  = f"| Sévérité : **{scan['severity']}**" if scan.get('severity', '—') != '—' else ""
            seg_str  = f"| Segmenté : *{scan.get('segmenté', '—')}*"
            st.markdown(f"""
            **{scan['time']}** | *{scan['file']}* | **{scan['label']}** | Confiance : **{scan['confidence']}** {sev_str} {seg_str} | *{icon}*
            """)
            st.divider()
