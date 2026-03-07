import streamlit as st
import tensorflow as tf
import numpy as np
import time
import json
import requests
import pandas as pd
import io
from pathlib import Path
from datetime import datetime
from PIL import Image
from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2,
    decode_predictions,
    preprocess_input,
)

# --- CONFIGURATION ET CHARGEMENT DES MODELES ---

@st.cache_resource
def load_models():
    disease = tf.keras.models.load_model('training_model.keras')
    filtre  = MobileNetV2(weights="imagenet")
    return disease, filtre

DISEASE_MODEL, FILTER_MODEL = load_models()

PLANT_KEYWORDS = {
    # Légumes / fruits ImageNet directement liés aux cultures cibles
    "tomato", "potato", "bell_pepper", "cucumber", "zucchini",
    "broccoli", "cauliflower", "corn", "artichoke", "cardoon",
    "head_cabbage", "granny_smith", "lemon", "orange", "pineapple",
    "banana", "strawberry", "fig", "hip", "rapeseed", "acorn",
    "buckeye", "ear",
    # Végétaux / botaniques génériques
    "plant", "leaf", "vine", "daisy", "sunflower", "hay",
    # Champignons (apparences similaires aux maladies foliaires)
    "mushroom", "agaric", "bolete", "gyromitra", "stinkhorn",
    "earthstar", "hen_of_the_woods", "coral_fungus",
    # Contexte agricole / jardinage
    "greenhouse", "pot", "barn", "garden", "tray",
    # Mots partiels pouvant apparaître dans les labels ImageNet composés
    "pepper", "squash", "gourd", "berry", "herb", "moss", "lichen",
}

REJECT_MSG = "Desole, je ne suis pas capable de predire sur ce genre d'image. Assurez-vous qu'il s'agit d'une feuille de plante (Tomate, Pomme de terre ou Poivron)."

CLASS_NAMES = [
    "Pepper__bell___Bacterial_spot", "Pepper__bell___healthy",
    "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
    "Tomato_Bacterial_spot", "Tomato_Early_blight", "Tomato_Late_blight",
    "Tomato_Leaf_Mold", "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite", "Tomato__Target_Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus", "Tomato__Tomato_mosaic_virus",
    "Tomato_healthy"
]

# --- SEVERITE ---

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
    "Pepper__bell___Bacterial_spot": "Retirer les feuilles infectees, eviter l'arrosage par le haut pour ne pas propager les bacteries, et appliquer un fongicide a base de cuivre.",
    "Pepper__bell___healthy": "Le plant est en excellente sante. Continuez une surveillance reguliere et assurez une bonne aeration entre les plants.",
    "Potato___Early_blight": "Pratiquer la rotation des cultures, eliminer les debris de recolte et appliquer des fongicides protecteurs des les premiers signes.",
    "Potato___Late_blight": "URGENT : Eliminer et detruire les plants infectes. Ameliorer le drainage du sol et utiliser des varietes resistantes a l'avenir.",
    "Potato___healthy": "Votre culture de pommes de terre est saine. Maintenez une fertilisation equilibree pour renforcer sa resistance naturelle.",
    "Tomato_Bacterial_spot": "Eviter de manipuler les plants quand ils sont mouilles. Utiliser des semences certifiees et appliquer des traitements cupriques.",
    "Tomato_Early_blight": "Taillez les feuilles inferieures pour ameliorer la circulation d'air. Le paillage du sol aide a reduire les eclaboussures de spores.",
    "Tomato_Late_blight": "CRITIQUE : Retirer les parties atteintes immediatement. Reduire l'humidite ambiante et appliquer des fongicides specifiques sans tarder.",
    "Tomato_Leaf_Mold": "Augmenter l'espacement entre les plants et assurer une ventilation maximale, surtout en serre. Eviter l'humidite foliaire nocturne.",
    "Tomato_Septoria_leaf_spot": "Supprimer les premieres feuilles infectees a la base. Pratiquer une rotation de 2-3 ans sans solanacees.",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Favoriser les predateurs naturels. En cas de forte attaque, utiliser du savon noir ou des huiles horticoles biologiques.",
    "Tomato__Target_Spot": "Eliminer les debris vegetaux. Assurer une nutrition potassique adequate pour renforcer les tissus de la plante.",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Lutter contre les aleurodes (mouches blanches) via des pieges jaunes ou des filets. Arracher les plants virusés.",
    "Tomato__Tomato_mosaic_virus": "Hygiene stricte : desinfecter les outils, ne pas fumer pres des plants. Eliminer les plants infectes pour stopper la propagation.",
    "Tomato_healthy": "Plante saine. Bravo ! Continuez vos bonnes pratiques culturales actuelles."
}

# --- DESCRIPTION SIMPLE PAR MALADIE ---

SIMPLE_DESCRIPTION = {
    "Pepper__bell___Bacterial_spot": "Petites taches brunes/noires entourees d'un halo jaune sur les feuilles. Les taches peuvent aussi apparaitre sur les fruits.",
    "Pepper__bell___healthy": "Feuilles vert vif, sans taches ni deformations. Plant vigoureux.",
    "Potato___Early_blight": "Taches brunes en forme de cible (cercles concentriques) sur les vieilles feuilles. Feuilles qui jaunissent puis tombent.",
    "Potato___Late_blight": "Grandes taches vert fonce a brun qui s'etendent rapidement. Duvet blanc/gris sous la feuille par temps humide. Odeur desagreable.",
    "Potato___healthy": "Feuilles vert franc, sans taches ni jaunissement. Plant en bonne sante.",
    "Tomato_Bacterial_spot": "Petites taches aqueuses qui deviennent brunes avec un halo jaune. Les taches ont un aspect gras ou huileux.",
    "Tomato_Early_blight": "Taches brunes concentriques (aspect cible) sur les feuilles du bas en premier. Jaunissement autour des taches.",
    "Tomato_Late_blight": "Grandes taches brunes irregulieres avec halo verdatre. Duvet blanc sous la feuille par temps humide. Tres contagieux.",
    "Tomato_Leaf_Mold": "Taches jaunes sur le dessus des feuilles, duvet gris/olive en dessous. Surtout en serre ou par temps chaud et humide.",
    "Tomato_Septoria_leaf_spot": "Nombreuses petites taches circulaires avec centre gris/blanc et bord brun fonce. Commence sur les feuilles basses.",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Feuilles avec piquetures blanches/jaunes (aspect poivre). Toiles fines visibles en cas de forte infestation. Feuilles qui sechen.",
    "Tomato__Target_Spot": "Taches brunes avec cercles concentriques sur feuilles ET fruits. Ressemble a l'alternariose precoce.",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Feuilles enroulees vers le haut, jaunies, petites et deformees. Plant rabougri. Transmis par les mouches blanches.",
    "Tomato__Tomato_mosaic_virus": "Feuilles avec motif mosaique vert clair/fonce, deformees et cloquees. Transmis par contact (mains, outils).",
    "Tomato_healthy": "Feuilles vert vif, bien developpees, sans deformation ni coloration anormale.",
}

# --- CALENDRIER DE TRAITEMENT ---

CALENDAR = {
    "Pepper__bell___Bacterial_spot": [
        {"jour": "J+0",  "action": "Retirer toutes les feuilles infectees et les detruire (ne pas composter)."},
        {"jour": "J+1",  "action": "Appliquer un fongicide a base de cuivre (bouillie bordelaise) sur l'ensemble du plant."},
        {"jour": "J+7",  "action": "Inspecter a nouveau. Si nouvelles taches, renouveler le traitement."},
        {"jour": "J+14", "action": "Evaluation finale : si la maladie persiste, envisager l'arrachage."},
    ],
    "Pepper__bell___healthy": None,
    "Potato___Early_blight": [
        {"jour": "J+0",  "action": "Supprimer et detruire les feuilles infectees a la base du plant."},
        {"jour": "J+2",  "action": "Appliquer un fongicide protecteur (mancozebe ou chlorothalonil)."},
        {"jour": "J+10", "action": "Reevaluer. Planifier une rotation de cultures pour la saison suivante."},
    ],
    "Potato___Late_blight": [
        {"jour": "J+0 URGENT", "action": "Arracher et detruire immediatement les plants atteints. Ne pas les laisser au sol."},
        {"jour": "J+1",        "action": "Traiter les plants voisins avec fongicide systemique (cymoxanil + mancozebe)."},
        {"jour": "J+3",        "action": "Inspecter l'ensemble de la parcelle. Surveiller la meteo (froid + humidite = risque eleve)."},
        {"jour": "J+7",        "action": "Second traitement preventif sur les plants encore sains."},
    ],
    "Potato___healthy": None,
    "Tomato_Bacterial_spot": [
        {"jour": "J+0",  "action": "Eviter toute manipulation des plants mouilles. Retirer les feuilles tres atteintes."},
        {"jour": "J+1",  "action": "Appliquer un traitement cuprique. Espacer les arrosages."},
        {"jour": "J+7",  "action": "Controler l'evolution. Renouveler le traitement si necessaire."},
    ],
    "Tomato_Early_blight": [
        {"jour": "J+0",  "action": "Couper les feuilles inferieures infectees. Pailler le sol."},
        {"jour": "J+2",  "action": "Appliquer un fongicide (mancozebe, chlorothalonil)."},
        {"jour": "J+10", "action": "Reevaluer. Si l'infection remonte vers le haut, intensifier les traitements."},
    ],
    "Tomato_Late_blight": [
        {"jour": "J+0 CRITIQUE", "action": "Retirer immediatement toutes les parties atteintes. Reduire l'irrigation."},
        {"jour": "J+1",          "action": "Appliquer un fongicide systemique specifique (propamocarbe, metalaxyl)."},
        {"jour": "J+5",          "action": "Inspection complete. Si >30% du plant est atteint, arracher."},
        {"jour": "J+10",         "action": "Reevaluation finale et traitement preventif des plants voisins."},
    ],
    "Tomato_Leaf_Mold": [
        {"jour": "J+0",  "action": "Augmenter la ventilation (ouvrir serre, espacer les plants)."},
        {"jour": "J+3",  "action": "Appliquer un fongicide preventif si les conditions restent humides."},
        {"jour": "J+10", "action": "Controle visuel. La maladie recule avec une bonne ventilation."},
    ],
    "Tomato_Septoria_leaf_spot": [
        {"jour": "J+0",       "action": "Supprimer les feuilles basses infectees. Ne pas travailler les plants mouilles."},
        {"jour": "J+2",       "action": "Appliquer un fongicide de contact (mancozebe)."},
        {"jour": "Saison+1",  "action": "Planifier une rotation de 2-3 ans sans solanacees."},
    ],
    "Tomato_Spider_mites_Two_spotted_spider_mite": [
        {"jour": "J+0", "action": "Introduire des predateurs naturels (Phytoseiulus persimilis) si en serre."},
        {"jour": "J+2", "action": "En cas de forte attaque, appliquer savon noir ou huile horticole biologique."},
        {"jour": "J+7", "action": "Verifier l'efficacite. Maintenir une humidite elevee pour freiner la proliferation."},
    ],
    "Tomato__Target_Spot": [
        {"jour": "J+0",  "action": "Eliminer les debris vegetaux et les feuilles tombees au sol."},
        {"jour": "J+2",  "action": "Appliquer un fongicide systemique (azoxystrobine)."},
        {"jour": "J+10", "action": "Reevaluation et fertilisation potassique pour renforcer les tissus."},
    ],
    "Tomato__Tomato_YellowLeaf__Curl_Virus": [
        {"jour": "J+0",      "action": "Installer des filets anti-insectes et des pieges jaunes contre les aleurodes."},
        {"jour": "J+3",      "action": "Arracher les plants viruses confirmes pour stopper la propagation."},
        {"jour": "J+7",      "action": "Traiter contre les aleurodes avec insecticide systemique ou biologique."},
        {"jour": "Saison+1", "action": "Choisir des varietes resistantes au TYLCV."},
    ],
    "Tomato__Tomato_mosaic_virus": [
        {"jour": "J+0", "action": "Desinfecter tous les outils. Isoler les plants suspects. Ne pas fumer pres des plants."},
        {"jour": "J+1", "action": "Arracher et detruire les plants confirmes malades."},
        {"jour": "J+7", "action": "Controle du reste de la parcelle. Hygiene stricte lors des manipulations."},
    ],
    "Tomato_healthy": None,
}

# --- VARIETES RESISTANTES ---

VARIETIES = {
    "Pepper__bell___Bacterial_spot":                    ["Aristotle", "Revolution", "Paladin", "Alliance"],
    "Potato___Early_blight":                            ["Kennebec", "Elba", "Allegany", "Rosa"],
    "Potato___Late_blight":                             ["Sarpo Mira", "Orla", "Setanta", "Cara", "Sarpo Axona"],
    "Tomato_Bacterial_spot":                            ["Tasti-Lee", "BHN 589", "Florida 47"],
    "Tomato_Early_blight":                              ["Mountain Supreme", "Juliet", "Legend", "Plum Regal"],
    "Tomato_Late_blight":                               ["Mountain Magic", "Defiant PhR", "Jasper", "Iron Lady"],
    "Tomato_Leaf_Mold":                                 ["Clermont", "Dombito", "Jumbo", "Piranto"],
    "Tomato_Septoria_leaf_spot":                        ["Legend", "Plum Regal", "Mountain Merit"],
    "Tomato__Tomato_YellowLeaf__Curl_Virus":            ["Shanty", "Nativo", "Boludo", "Tyking"],
    "Tomato__Tomato_mosaic_virus":                      ["Celebrity", "Floradade", "Big Beef"],
    "Tomato_Spider_mites_Two_spotted_spider_mite":      ["Favoriser les varieties a feuillage dense (moins susceptibles)"],
    "Tomato__Target_Spot":                              ["Mountain Merit", "Plum Regal"],
}

# --- CONDITIONS METEOROLOGIQUES FAVORABLES PAR MALADIE ---

WEATHER_RISK = {
    "Potato___Late_blight":   {"desc": "Mildiou actif par temps frais (8-22C) et tres humide (>80%).",        "temp_range": (8,  22), "humidity_min": 80, "humidity_max": 100},
    "Tomato_Late_blight":     {"desc": "Mildiou actif entre 10-24C avec humidite >75%.",                     "temp_range": (10, 24), "humidity_min": 75, "humidity_max": 100},
    "Tomato_Early_blight":    {"desc": "Alternariose favorisee par temps chaud (24-30C) et humide.",         "temp_range": (24, 30), "humidity_min": 55, "humidity_max": 100},
    "Potato___Early_blight":  {"desc": "Alternariose favorisee par temps chaud (24-30C) et humide.",         "temp_range": (24, 30), "humidity_min": 55, "humidity_max": 100},
    "Tomato_Leaf_Mold":       {"desc": "Moisissure active par temps chaud/humide (21-24C, >85% HR).",        "temp_range": (21, 24), "humidity_min": 85, "humidity_max": 100},
    "Tomato_Bacterial_spot":  {"desc": "Bacteriose favorisee par pluies et temperatures de 25-30C.",         "temp_range": (25, 30), "humidity_min": 70, "humidity_max": 100},
    "Tomato_Septoria_leaf_spot": {"desc": "Septoriose active par temps humide et temperatures moderees.",    "temp_range": (20, 25), "humidity_min": 65, "humidity_max": 100},
    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "desc": "Acariens proliferent par temps CHAUD et SEC (>26C, humidite <50%).",
        "temp_range": (26, 50), "humidity_min": 0, "humidity_max": 50,
    },
}

# --- BASE DE DONNEES DES MALADIES ---

DISEASE_INFO = {
    "Pepper__bell___Bacterial_spot": {
        "pathogene":   "Bacterie Xanthomonas campestris pv. vesicatoria",
        "cultures":    "Poivron, Piment",
        "conditions":  "Temps chaud (24-30C) et humide, arrosage par aspersion, pluies frequentes.",
        "cycle":       "Survit sur semences et debris vegetaux. Se propage par l'eau et le vent.",
        "prevention":  "Semences certifiees, eviter l'arrosage foliaire, rotation des cultures.",
    },
    "Potato___Early_blight": {
        "pathogene":   "Champignon Alternaria solani",
        "cultures":    "Pomme de terre, Tomate",
        "conditions":  "Temps chaud (24-30C), cycles humidite/secheresse alternes.",
        "cycle":       "Spores hivernent dans le sol et les debris. Liberees par vent et pluie.",
        "prevention":  "Rotation des cultures, elimination des debris, fongicides preventifs.",
    },
    "Potato___Late_blight": {
        "pathogene":   "Oomycete Phytophthora infestans",
        "cultures":    "Pomme de terre, Tomate",
        "conditions":  "Temps frais (10-20C) et tres humide (>90%), brouillard, rosee.",
        "cycle":       "Spores liberees par temps humide, infectent en quelques heures. Extremement contagieux.",
        "prevention":  "Varietes resistantes, fongicides preventifs, bonne aeration des cultures.",
    },
    "Tomato_Bacterial_spot": {
        "pathogene":   "Bacterie Xanthomonas vesicatoria",
        "cultures":    "Tomate",
        "conditions":  "Temperatures de 25-30C, pluies frequentes, vent.",
        "cycle":       "Penetre par stomates et blessures. Se propage par eau, outils, manipulation.",
        "prevention":  "Semences certifiees, eviter manipulation par temps mouille, traitements cupriques.",
    },
    "Tomato_Early_blight": {
        "pathogene":   "Champignon Alternaria solani",
        "cultures":    "Tomate, Pomme de terre",
        "conditions":  "Chaud et humide (24-30C). Stress hydrique favorise l'infection.",
        "cycle":       "Spores du sol, liberees lors des pluies, infectent les feuilles agees en premier.",
        "prevention":  "Paillage du sol, fongicides, suppression des feuilles basses, bonne nutrition.",
    },
    "Tomato_Late_blight": {
        "pathogene":   "Oomycete Phytophthora infestans",
        "cultures":    "Tomate, Pomme de terre",
        "conditions":  "Frais et tres humide (10-24C, >75% HR).",
        "cycle":       "Propagation tres rapide. Spores actives en quelques heures par temps humide.",
        "prevention":  "Surveillance meteo, fongicides preventifs, varietes resistantes.",
    },
    "Tomato_Leaf_Mold": {
        "pathogene":   "Champignon Passalora fulva",
        "cultures":    "Tomate (surtout en serre)",
        "conditions":  "Tres humide (>85% HR), temperatures de 21-24C.",
        "cycle":       "Spores aeriennes. Propagation rapide en serre dense.",
        "prevention":  "Ventilation, espacement des plants, eviter l'humidite foliaire nocturne.",
    },
    "Tomato_Septoria_leaf_spot": {
        "pathogene":   "Champignon Septoria lycopersici",
        "cultures":    "Tomate",
        "conditions":  "Temps humide, temperatures moderees (20-25C).",
        "cycle":       "Survit dans le sol et les debris. Spores transportees par eau et outils.",
        "prevention":  "Rotation 2-3 ans, elimination des debris, paillage.",
    },
    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "pathogene":   "Acarien Tetranychus urticae",
        "cultures":    "Tomate, Poivron, Concombre",
        "conditions":  "Chaud et sec (>28C, faible humidite). Stress hydrique.",
        "cycle":       "Multiplication rapide par temps sec. Vit sous les feuilles.",
        "prevention":  "Maintenir l'humidite, predateurs naturels, eviter le stress hydrique.",
    },
    "Tomato__Target_Spot": {
        "pathogene":   "Champignon Corynespora cassiicola",
        "cultures":    "Tomate, Concombre",
        "conditions":  "Chaud et humide (25-30C, >80% HR).",
        "cycle":       "Spores aeriennes depuis le sol ou les debris vegetaux.",
        "prevention":  "Elimination des debris, fongicides, bonne fertilisation.",
    },
    "Tomato__Tomato_YellowLeaf__Curl_Virus": {
        "pathogene":   "Virus TYLCV, transmis par l'aleurode Bemisia tabaci",
        "cultures":    "Tomate",
        "conditions":  "Populations elevees d'aleurodes, temps chaud.",
        "cycle":       "Le virus est inocule lors des piqures d'aleurodes. Pas de transmission par contact.",
        "prevention":  "Filets anti-insectes, pieges jaunes, insecticides, varietes resistantes.",
    },
    "Tomato__Tomato_mosaic_virus": {
        "pathogene":   "Virus ToMV (Tomato mosaic virus)",
        "cultures":    "Tomate, Poivron",
        "conditions":  "Transmission mecanique tres facile (contact, outils, mains).",
        "cycle":       "Survit tres longtemps dans les debris. Ne necessite pas d'insecte vecteur.",
        "prevention":  "Hygiene stricte, semences certifiees, ne pas fumer pres des plants.",
    },
}

# --- FICHIER DE PERSISTANCE DES PARCELLES ---

PARCELS_FILE = Path("parcels.json")
WEATHER_API_KEY = "a4258553cc334f96e69d5e1577bfab51"

# =============================================================================
# FONCTIONS ORIGINALES
# =============================================================================

def plant_gate(test_image):
    """
    Filtre OOD : Verifie si l'image telecharge ressemble a une plante
    en utilisant un modele generaliste (MobileNetV2).
    """
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=[224, 224])
    arr   = tf.keras.preprocessing.image.img_to_array(image)
    arr   = preprocess_input(np.array([arr]))

    preds = FILTER_MODEL.predict(arr, verbose=0)
    top5  = decode_predictions(preds, top=5)[0]

    is_plant = False
    for _, label, _ in top5:
        label_norm = label.lower()
        if any(keyword in label_norm for keyword in PLANT_KEYWORDS):
            is_plant = True
            break
    return is_plant, top5


def model_prediction(test_image):
    """Prediction de la maladie avec le modele specifique aux cultures cibles."""
    image    = tf.keras.preprocessing.image.load_img(test_image, target_size=[128, 128])
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])
    prediction = DISEASE_MODEL.predict(input_arr, verbose=0)
    probs      = prediction[0]
    result_index = int(np.argmax(probs))
    confidence   = float(np.max(probs))
    return result_index, probs, confidence


# =============================================================================
# NOUVELLES FONCTIONS
# =============================================================================

def model_prediction_pil(image_pil):
    """Variante de model_prediction acceptant un objet PIL (utilisee pour la comparaison)."""
    input_arr = tf.keras.preprocessing.image.img_to_array(
        image_pil.convert("RGB").resize((128, 128))
    )
    input_arr_batch = np.array([input_arr])
    probs = DISEASE_MODEL.predict(input_arr_batch, verbose=0)[0]
    result_index = int(np.argmax(probs))
    confidence   = float(np.max(probs))
    return result_index, probs, confidence


def get_confidence_context(confidence):
    """Retourne un message contextualise et une couleur selon le niveau de confiance."""
    if confidence >= 0.95:
        return "Diagnostic tres fiable. Le modele est quasi-certain de son resultat.", "success"
    elif confidence >= 0.80:
        return "Diagnostic fiable. Une verification visuelle rapide est conseillee.", "warning"
    else:
        return "Confiance moderee. Comparez avec la description visuelle et consultez un agronome si necessaire.", "error"


def get_weather_risk(city, api_key, disease_label):
    """
    Appelle l'API OpenWeatherMap pour evaluer le risque meteo
    de propagation de la maladie detectee.
    Retourne un dict avec temp, humidite, niveau de risque, ou None si echec.
    """
    if not api_key or not city:
        return None
    try:
        url  = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return {"error": f"Ville introuvable ou cle API invalide (code {resp.status_code})."}
        data     = resp.json()
        temp     = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        desc_meteo = data["weather"][0]["description"]

        risk_info = WEATHER_RISK.get(disease_label)
        if not risk_info:
            return {"temp": temp, "humidity": humidity, "desc_meteo": desc_meteo, "risk": None,
                    "msg": "Pas de donnees de risque meteo pour cette maladie."}

        temp_min, temp_max = risk_info["temp_range"]
        hum_min  = risk_info.get("humidity_min", 0)
        hum_max  = risk_info.get("humidity_max", 100)

        risk_score = 0
        if temp_min <= temp <= temp_max:
            risk_score += 1
        if hum_min <= humidity <= hum_max:
            risk_score += 1

        risk_level = {2: "Eleve", 1: "Modere", 0: "Faible"}[risk_score]

        return {
            "temp":       temp,
            "humidity":   humidity,
            "desc_meteo": desc_meteo,
            "risk":       risk_level,
            "msg":        risk_info["desc"],
        }
    except Exception as e:
        return {"error": str(e)}



def load_parcels():
    """Charge les parcelles depuis le fichier JSON local."""
    if PARCELS_FILE.exists():
        with open(PARCELS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_parcels(data):
    """Sauvegarde les parcelles dans le fichier JSON local."""
    with open(PARCELS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def check_propagation_alert(analyses):
    """
    Verifie si une meme maladie apparait plusieurs fois avec une confiance croissante
    dans une liste d'analyses de parcelle.
    Retourne un dict d'alerte ou None.
    """
    if len(analyses) < 2:
        return None
    from collections import Counter
    disease_counts = Counter(a["label"] for a in analyses if "healthy" not in a["label"])
    for disease, count in disease_counts.items():
        if count >= 2:
            subset      = [a for a in analyses if a["label"] == disease]
            confidences = [float(str(a["confidence"]).replace("%", "")) for a in subset]
            if confidences[-1] > confidences[0]:
                return {"disease": disease, "count": count, "trend": "croissante",
                        "first": f"{confidences[0]:.1f}%", "last": f"{confidences[-1]:.1f}%"}
    return None


# --- ETAT DE LA SESSION ---

if "history"  not in st.session_state: st.session_state.history  = []
if "parcels"  not in st.session_state: st.session_state.parcels  = load_parcels()
if "last_result" not in st.session_state: st.session_state.last_result = None

# --- BARRE LATERALE ---

st.sidebar.title("PhytoDiag IA")
app_mode = st.sidebar.selectbox(
    "Selectionner une page",
    ["Accueil", "A propos", "Reconnaissance des maladies",
     "Comparaison avant/apres", "Suivi de parcelle", "Base de maladies", "Historique"]
)

conf_threshold = st.sidebar.slider("Seuil de confiance min (%)", 10, 100, 70, 5) / 100

st.sidebar.markdown("---")
st.sidebar.markdown("**Meteo**")
weather_city = st.sidebar.text_input("Ville", placeholder="Ex: Alger, Paris, Rabat")

# =============================================================================
# PAGE ACCUEIL
# =============================================================================

if app_mode == "Accueil":
    st.header("PhytoDiag IA")
    st.image("./home_image.JPG", use_container_width=True)
    st.markdown("""
    #### Bienvenue dans le systeme de reconnaissance des maladies des plantes

    Notre mission est d'aider a identifier efficacement les maladies des plantes. Telechargez une image d'une plante
    et notre systeme l'analysera pour detecter tout signe de maladie. Ensemble, protegeons nos cultures.
    """)

# =============================================================================
# PAGE A PROPOS
# =============================================================================

if app_mode == "A propos":
    st.header("A propos")
    st.markdown(f"""
    ### A propos du projet
    #### 1. Objectif
        Detecter automatiquement l'etat de sante d'une plante (saine ou malade) et identifier la maladie probable.
    #### 2. Modeles utilises
        - **CNN de diagnostic** : entraine sur le dataset PlantVillage (15 classes).
        - **Filtre OOD (MobileNetV2)** : rejette les images non-vegetales.
    #### 3. Fonctionnalites
        - Seuil de confiance ajustable : **{conf_threshold*100:.0f}%** actuellement.
        - Description visuelle simple de chaque maladie.
        - Calendrier de traitement par maladie.
        - Recommandation de varietes resistantes.
        - Risque meteo si cle API OpenWeatherMap fournie.
        - Export PDF du rapport de diagnostic.
        - Suivi de parcelle avec persistance locale (fichier parcels.json).
        - Comparaison avant/apres traitement.
        - Base encyclopedique des maladies.
    """)

# =============================================================================
# PAGE RECONNAISSANCE DES MALADIES
# =============================================================================

if app_mode == "Reconnaissance des maladies":
    st.header("Reconnaissance des maladies")
    test_image = st.file_uploader("Choisissez une image...", type=["jpg", "jpeg", "png"])

    if test_image is not None:
        if st.button("Afficher l'image"):
            st.image(test_image, use_container_width=True)

        if st.button("Predire"):
            with st.spinner("Analyse en cours (Verification et Diagnostic)..."):
                # ETAPE 1 : Filtre OOD (desactive)
                if True:
                    # ETAPE 2 : Diagnostic
                    result_index, probs, confidence = model_prediction(test_image)

                    # ETAPE 3 : Seuil de confiance
                    if confidence < conf_threshold:
                        st.warning(f"Confiance trop faible ({confidence*100:.1f}%). {REJECT_MSG}")
                        st.session_state.last_result = None
                    else:
                        predicted_label = CLASS_NAMES[result_index]
                        is_healthy      = "healthy" in predicted_label.lower()
                        severity        = SEVERITY.get(predicted_label)
                        status_color    = "#2ecc71" if is_healthy else "#e74c3c"
                        status_text     = "Plante saine" if is_healthy else "Plante malade"

                        st.markdown(
                            f'<div style="padding:1rem;border-radius:10px;background:{status_color}22;border:2px solid {status_color};text-align:center;">'
                            f'<h3 style="margin:0;color:{status_color};">{status_text}</h3>'
                            f'<p style="margin:0.3rem 0 0;font-size:1.1rem;">Categorie : <b>{predicted_label}</b></p></div>',
                            unsafe_allow_html=True
                        )

                        # Metriques : confiance + severite
                        col_m1, col_m2 = st.columns(2)
                        col_m1.metric("Confiance", f"{confidence*100:.2f}%")
                        if severity:
                            sev_color = SEVERITY_COLOR.get(severity, "#888")
                            col_m2.markdown(
                                f'<div style="padding:0.5rem 1rem;border-radius:8px;background:{sev_color}22;border:1.5px solid {sev_color};text-align:center;margin-top:0.5rem"><b>Severite : {severity}</b></div>',
                                unsafe_allow_html=True
                            )

                        # Confiance contextualisee
                        ctx_msg, ctx_type = get_confidence_context(confidence)
                        getattr(st, ctx_type)(ctx_msg)

                        # Description visuelle simple
                        st.subheader("Description visuelle")
                        st.write(SIMPLE_DESCRIPTION.get(predicted_label, ""))

                        # Conseils agricoles
                        st.info(f"**Dispositions a prendre :** {dispositions_agricoles[predicted_label]}")

                        # Calendrier de traitement
                        cal = CALENDAR.get(predicted_label)
                        if cal:
                            with st.expander("Calendrier de traitement"):
                                for step in cal:
                                    st.markdown(f"- **{step['jour']}** : {step['action']}")

                        # Varietes resistantes
                        var = VARIETIES.get(predicted_label)
                        if var:
                            with st.expander("Varietes resistantes recommandees pour la prochaine saison"):
                                st.write(", ".join(var))

                        # Risque meteo
                        if weather_city and WEATHER_API_KEY:
                            with st.expander("Risque meteo actuel"):
                                weather = get_weather_risk(weather_city, WEATHER_API_KEY, predicted_label)
                                if weather is None:
                                    st.write("Entrez votre ville et cle API dans la barre laterale.")
                                elif "error" in weather:
                                    st.error(f"Erreur meteo : {weather['error']}")
                                else:
                                    st.write(f"**{weather_city}** — {weather['desc_meteo']} | {weather['temp']}°C | Humidite : {weather['humidity']}%")
                                    if weather["risk"]:
                                        risk_colors = {"Eleve": "error", "Modere": "warning", "Faible": "success"}
                                        getattr(st, risk_colors.get(weather["risk"], "info"))(
                                            f"Risque de propagation : **{weather['risk']}** — {weather['msg']}"
                                        )
                                    else:
                                        st.info(weather["msg"])

                        # Top-5 probabilites
                        st.write("Top-5 des predictions :")
                        sorted_idx = np.argsort(probs)[::-1][:5]
                        st.bar_chart({CLASS_NAMES[i]: probs[i] for i in sorted_idx})


                        # Enregistrement historique + session
                        entry = {
                            "time":       time.strftime("%H:%M:%S"),
                            "file":       test_image.name,
                            "label":      predicted_label,
                            "confidence": f"{confidence*100:.1f}%",
                            "status":     "Saine" if is_healthy else "Malade",
                        }
                        st.session_state.history.append(entry)
                        st.session_state.last_result = entry

# =============================================================================
# PAGE COMPARAISON AVANT / APRES TRAITEMENT
# =============================================================================

if app_mode == "Comparaison avant/apres":
    st.header("Comparaison avant / apres traitement")
    st.info("Telechargez deux images de la meme plante (avant traitement et apres) pour comparer les diagnostics.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Image AVANT traitement")
        img_before = st.file_uploader("Image avant...", type=["jpg", "jpeg", "png"], key="before")
    with col2:
        st.subheader("Image APRES traitement")
        img_after  = st.file_uploader("Image apres...", type=["jpg", "jpeg", "png"], key="after")

    if img_before and img_after and st.button("Comparer"):
        with st.spinner("Analyse des deux images..."):
            pil_before = Image.open(img_before)
            pil_after  = Image.open(img_after)

            is_plant_b, _ = plant_gate(img_before)
            is_plant_a, _ = plant_gate(img_after)

        col1, col2 = st.columns(2)

        with col1:
            st.image(pil_before, caption="Avant", use_container_width=True)
            if is_plant_b:
                idx_b, probs_b, conf_b = model_prediction_pil(pil_before)
                if conf_b >= conf_threshold:
                    label_b    = CLASS_NAMES[idx_b]
                    healthy_b  = "healthy" in label_b
                    color_b    = "#2ecc71" if healthy_b else "#e74c3c"
                    st.markdown(f'<div style="border:2px solid {color_b};padding:0.5rem;border-radius:8px;text-align:center;"><b>{label_b}</b><br>Confiance : {conf_b*100:.1f}%</div>', unsafe_allow_html=True)
                else:
                    st.warning(f"Confiance trop faible ({conf_b*100:.1f}%)")
            else:
                st.error("Image rejetee par le filtre OOD")

        with col2:
            st.image(pil_after, caption="Apres", use_container_width=True)
            if is_plant_a:
                idx_a, probs_a, conf_a = model_prediction_pil(pil_after)
                if conf_a >= conf_threshold:
                    label_a   = CLASS_NAMES[idx_a]
                    healthy_a = "healthy" in label_a
                    color_a   = "#2ecc71" if healthy_a else "#e74c3c"
                    st.markdown(f'<div style="border:2px solid {color_a};padding:0.5rem;border-radius:8px;text-align:center;"><b>{label_a}</b><br>Confiance : {conf_a*100:.1f}%</div>', unsafe_allow_html=True)
                else:
                    st.warning(f"Confiance trop faible ({conf_a*100:.1f}%)")
            else:
                st.error("Image rejetee par le filtre OOD")

        # Conclusion comparative
        if is_plant_b and is_plant_a and conf_b >= conf_threshold and conf_a >= conf_threshold:
            st.markdown("---")
            if "healthy" not in label_b and "healthy" in label_a:
                st.success("Le traitement semble avoir ete efficace : la plante est maintenant diagnostiquee saine.")
            elif "healthy" in label_b and "healthy" in label_a:
                st.success("La plante etait saine et le reste apres traitement.")
            elif label_b == label_a:
                st.warning(f"La maladie '{label_b}' est toujours detectee. Le traitement n'a pas encore produit d'effet visible.")
            else:
                st.info(f"Evolution : '{label_b}' -> '{label_a}'. Une consultation agronomique est recommandee.")

# =============================================================================
# PAGE SUIVI DE PARCELLE
# =============================================================================

if app_mode == "Suivi de parcelle":
    st.header("Suivi de parcelle")

    # Creer ou selectionner une parcelle
    parcels = st.session_state.parcels
    parcel_names = list(parcels.keys())

    col_sel, col_new = st.columns([2, 1])
    with col_new:
        new_name = st.text_input("Nouvelle parcelle", placeholder="Ex: Serre A - Tomates")
        if st.button("Creer") and new_name.strip():
            if new_name not in parcels:
                parcels[new_name] = []
                save_parcels(parcels)
                st.session_state.parcels = parcels
                st.success(f"Parcelle '{new_name}' creee.")
                st.rerun()

    with col_sel:
        selected = st.selectbox("Selectionner une parcelle", ["—"] + parcel_names)

    if selected != "—":
        parcel_data = parcels[selected]

        # Ajouter la derniere analyse a cette parcelle
        if st.session_state.last_result:
            lr = st.session_state.last_result
            if st.button(f"Ajouter '{lr['label']}' ({lr['confidence']}) a cette parcelle"):
                entry = {**lr, "date": datetime.now().strftime("%d/%m/%Y %H:%M")}
                parcels[selected].append(entry)
                save_parcels(parcels)
                st.session_state.parcels = parcels
                st.session_state.last_result = None
                st.success("Analyse ajoutee a la parcelle.")
                st.rerun()
        else:
            st.caption("Effectuez d'abord un diagnostic pour pouvoir l'ajouter a cette parcelle.")

        # Alerte de propagation
        alert = check_propagation_alert(parcel_data)
        if alert:
            st.error(
                f"Alerte propagation : '{alert['disease']}' detecte {alert['count']} fois "
                f"avec une confiance {alert['trend']} ({alert['first']} -> {alert['last']}). "
                f"Intervention urgente recommandee."
            )

        # Historique de la parcelle
        st.subheader(f"Historique : {selected}")
        if not parcel_data:
            st.write("Aucune analyse enregistree pour cette parcelle.")
        else:
            df_parcel = pd.DataFrame(parcel_data)
            st.dataframe(df_parcel, use_container_width=True)

            # Graphique d'evolution de la confiance
            diseased = [a for a in parcel_data if "healthy" not in a.get("label", "")]
            if len(diseased) >= 2:
                st.subheader("Evolution de la confiance (maladies)")
                chart_data = {
                    a.get("date", a.get("time", str(i))): float(str(a["confidence"]).replace("%", ""))
                    for i, a in enumerate(diseased)
                }
                st.line_chart(chart_data)

        # Supprimer la parcelle
        if st.button(f"Supprimer la parcelle '{selected}'", type="secondary"):
            del parcels[selected]
            save_parcels(parcels)
            st.session_state.parcels = parcels
            st.rerun()

# =============================================================================
# PAGE BASE DE MALADIES
# =============================================================================

if app_mode == "Base de maladies":
    st.header("Base de donnees des maladies")
    st.info("Encyclopedie des maladies couvertes par PhytoDiag IA.")

    disease_choice = st.selectbox(
        "Choisir une maladie",
        [d for d in CLASS_NAMES if "healthy" not in d]
    )

    if disease_choice:
        info = DISEASE_INFO.get(disease_choice)

        st.subheader(disease_choice.replace("_", " ").replace("  ", " — "))
        st.write(f"**Description :** {SIMPLE_DESCRIPTION.get(disease_choice, '—')}")

        if info:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Pathogene :** {info['pathogene']}")
                st.markdown(f"**Cultures touchees :** {info['cultures']}")
                st.markdown(f"**Conditions favorables :** {info['conditions']}")
            with col2:
                st.markdown(f"**Cycle d'infection :** {info['cycle']}")
                st.markdown(f"**Prevention :** {info['prevention']}")

        severity = SEVERITY.get(disease_choice)
        if severity:
            sev_color = SEVERITY_COLOR.get(severity, "#888")
            st.markdown(
                f'<div style="margin-top:0.5rem;padding:0.5rem 1rem;border-radius:8px;background:{sev_color}22;border:1.5px solid {sev_color};display:inline-block"><b>Severite : {severity}</b></div>',
                unsafe_allow_html=True
            )

        cal = CALENDAR.get(disease_choice)
        if cal:
            st.subheader("Calendrier de traitement type")
            for step in cal:
                st.markdown(f"- **{step['jour']}** : {step['action']}")

        var = VARIETIES.get(disease_choice)
        if var:
            st.subheader("Varietes resistantes")
            st.write(", ".join(var))

# =============================================================================
# PAGE HISTORIQUE
# =============================================================================

if app_mode == "Historique":
    st.header("Historique des analyses")
    if not st.session_state.history:
        st.write("Aucune analyse effectuee pour le moment.")
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
            icon = "🌿" if scan["status"] == "Saine" else "⚠️"
            st.markdown(f"""
            🕒 **{scan['time']}** | 📄 *{scan['file']}* | **{scan['label']}** | Confiance : **{scan['confidence']}** | {icon} *{scan['status']}*
            """)
            st.divider()
