import streamlit as st
import time
import numpy as np
from services.load_models import load_disease_model, load_filter_model
from services.predictor import plant_gate, model_prediction
from utils.dispositions import dispositions_agricoles
from utils.db_handler import get_champs_by_user, get_cultures_by_champ, save_analysis

CLASS_NAMES = [
    "Pepper__bell___Bacterial_spot", "Pepper__bell___healthy", 
    "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",       
    "Tomato_Bacterial_spot", "Tomato_Early_blight", "Tomato_Late_blight", 
    "Tomato_Leaf_Mold", "Tomato_Septoria_leaf_spot",      
    "Tomato_Spider_mites_Two_spotted_spider_mite", "Tomato__Target_Spot", 
    "Tomato__Tomato_YellowLeaf__Curl_Virus", "Tomato__Tomato_mosaic_virus",       
    "Tomato_healthy"
]

def show():
  st.title("Reconnaissance des maladies")

  disease_model = load_disease_model()
  filter_model = load_filter_model()
  
  st.write("Veuillez d'abord sélectionner une culture à associer à cette analyse (Optionnel).")
  selected_culture_id = None
  
  if st.session_state.get('user') and st.session_state['user'].get('id'):
      user_id = st.session_state['user']['id']
      champs = get_champs_by_user(user_id)
      
      if champs:
          champ_dict = {f"{c[1]} - {c[2]}": c[0] for c in champs}
          selected_champ = st.selectbox("Champ :", list(champ_dict.keys()))
          
          cultures = get_cultures_by_champ(champ_dict[selected_champ])
          if cultures:
              culture_dict = {f"{c[1]} ({c[2]})": c[0] for c in cultures}
              selected_culture = st.selectbox("Culture :", list(culture_dict.keys()))
              selected_culture_id = culture_dict[selected_culture]
          else:
              st.info("Aucune culture dans ce champ.")
      else:
          st.info("Vous n'avez pas de champs créés.")

  conf_threshold = st.slider("Seuil de confiance min (%)", 10, 100, 70, 5) / 100

  test_image = st.file_uploader("Choisissez une image...", type=["jpg","jpeg","png"])

  if test_image is not None:
      st.image(test_image, use_container_width=True)
      if st.button("Prédire"):
          with st.spinner("Analyse en cours..."):
              is_plant, top5 = plant_gate(test_image, filter_model)

              if not is_plant:
                  st.error("Désolé, je ne suis pas capable de prédire sur ce genre d'image. Assurez-vous qu'il s'agit d'une feuille de plante.")
              else:
                  result_index, probs, confidence = model_prediction(
                      test_image,
                      disease_model
                  )

                  if confidence < conf_threshold:
                      st.warning(f"Confiance trop faible ({confidence*100:.1f}%). Veuillez envoyer une image plus lisible.")
                  else:
                      predicted_label = CLASS_NAMES[result_index]
                      is_healthy = "healthy" in predicted_label.lower()
                      status_color = "#2ecc71" if is_healthy else "#e74c3c"
                      status_text = "🌿 Plante saine" if is_healthy else "⚠️ Plante malade"
                      statut_db = "Saine" if is_healthy else "Malade"

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
                      
                      try:
                          st.info(f"**Dispositions à prendre :** {dispositions_agricoles[predicted_label]}")
                      except KeyError:
                          pass

                      if selected_culture_id and st.session_state.get('user') and st.session_state['user'].get('id'):
                          try:
                              save_analysis(
                                  st.session_state['user']['id'], 
                                  selected_culture_id, 
                                  test_image.name, 
                                  predicted_label, 
                                  float(confidence), 
                                  statut_db
                              )
                              st.success("L'analyse a été sauvegardée avec succès !")
                          except Exception as e:
                              st.error(f"Erreur lors de la sauvegarde de l'analyse : {e}")
                      else:
                          st.warning("L'analyse n'a pas été sauvegardée car aucune culture n'était sélectionnée ou vous êtes en mode Invité.")