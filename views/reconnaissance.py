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
  st.markdown("<h1 style='color: #1e293b; margin-bottom: 1.5rem;'>Reconnaissance des maladies 🔎</h1>", unsafe_allow_html=True)
  st.markdown("<p style='color: #64748b; font-size: 1.1rem;'>Diagnostiquez l'état de santé de vos plantes à partir d'une photo.</p>", unsafe_allow_html=True)

  disease_model = load_disease_model()
  filter_model = load_filter_model()
  
  col_upload, col_settings = st.columns([2, 1])
  
  with col_settings:
      with st.container(border=True):
          st.markdown("<h4 style='color: #334155;'>Paramètres</h4>", unsafe_allow_html=True)
          st.write("Associez cette analyse à l'une de vos cultures (Optionnel) :")
          selected_culture_id = None
          
          if st.session_state.get('user') and st.session_state['user'].get('id'):
              user_id = st.session_state['user']['id']
              champs = get_champs_by_user(user_id)
              
              if champs:
                  champ_dict = {f"{c[1]} - {c[2]}": c[0] for c in champs}
                  selected_champ = st.selectbox("Sélectionnez le champ", list(champ_dict.keys()))
                  
                  cultures = get_cultures_by_champ(champ_dict[selected_champ])
                  if cultures:
                      culture_dict = {f"{c[1]} ({c[2]})": c[0] for c in cultures}
                      selected_culture = st.selectbox("Sélectionnez la culture", list(culture_dict.keys()))
                      selected_culture_id = culture_dict[selected_culture]
                  else:
                      st.info("Aucune culture dans ce champ.")
              else:
                  st.info("Vous n'avez pas encore de champs créés.")
          else:
              st.info("Connectez-vous pour lier l'analyse à vos champs.")

          st.write("<br>", unsafe_allow_html=True)
          st.markdown("<h4 style='color: #334155;'>Filtre de Confiance</h4>", unsafe_allow_html=True)
          conf_threshold = st.slider("Seuil minimal (%)", 10, 100, 70, 5) / 100
          
          st.write("<br>", unsafe_allow_html=True)
          st.markdown("<h4 style='color: #334155;'>Météo & Risque</h4>", unsafe_allow_html=True)
          weather_city = st.text_input("Ville pour la météo", placeholder="Ex: Cotonou, Paris")

  with col_upload:
      test_image = st.file_uploader("Prenez une photo ou téléchargez une image", type=["jpg","jpeg","png"])

      if test_image is not None:
          st.image(test_image, use_container_width=True)
          
          st.write("<br>", unsafe_allow_html=True)
          if st.button("Lancer l'Analyse Diagnostique", use_container_width=True):
              with st.spinner("Analyse en cours par l'Intelligence Artificielle..."):
                  is_plant, top5 = plant_gate(test_image, filter_model)

                  if not is_plant:
                      st.error("L'image soumise ne semble pas être une plante ou une feuille. Veuillez réessayer avec une image plus claire.")
                  else:
                      result_index, probs, confidence = model_prediction(
                          test_image,
                          disease_model
                      )

                      if confidence < conf_threshold:
                          st.warning(f"La confiance de l'IA est trop faible ({confidence*100:.1f}%). Veuillez envoyer une image plus nette.")
                      else:
                          predicted_label = CLASS_NAMES[result_index]
                          is_healthy = "healthy" in predicted_label.lower()
                          status_color = "#10b981" if is_healthy else "#ef4444"
                          status_text = "🌿 Plante Saine" if is_healthy else "⚠️ Plante Malade"
                          statut_db = "Saine" if is_healthy else "Malade"

                          st.markdown(
                              f"""
                              <div style="padding: 1.5rem; border-radius: 12px; background-color: {status_color}15; border: 2px solid {status_color}; text-align: center; margin-top: 2rem;">
                                  <h2 style="margin: 0; color: {status_color}; font-size: 2rem;">{status_text}</h2>
                                  <p style="margin: 0.5rem 0 0; font-size: 1.2rem; color: #334155;">Diagnostic : <b>{predicted_label.replace('_', ' ')}</b></p>
                              </div>
                              """,
                              unsafe_allow_html=True
                          )
                          
                          st.write("<br>", unsafe_allow_html=True)
                          col_m1, col_m2 = st.columns(2)
                          with col_m1:
                              st.metric("Taux de Confiance", f"{confidence * 100:.2f}%")
                          with col_m2:
                              st.metric("Statut", statut_db)
                          
                          try:
                              st.info(f"**Recommandations :** {dispositions_agricoles[predicted_label]}")
                          except KeyError:
                              pass
                          
                          from utils.meteo import get_weather_risk
                          if weather_city:
                              with st.expander("Risque météo de propagation actuel"):
                                  try:
                                      api_key = st.secrets["OPENWEATHER_API_KEY"]
                                  except (FileNotFoundError, KeyError):
                                      api_key = None
                                      st.warning("⚠️ Clé API Météo non configurée dans les secrets.")

                                  weather = get_weather_risk(weather_city, api_key, predicted_label)
                                  if weather is None:
                                      pass
                                  elif "error" in weather:
                                      st.error(f"Erreur météo : {weather['error']}")
                                  else:
                                      st.markdown(f"**{weather_city.capitalize()}** — {weather['desc_meteo']} | **{weather['temp']}°C** | Humidité : **{weather['humidity']}%**")
                                      if weather.get("risk"):
                                          risk_colors = {"Eleve": "red", "Modere": "orange", "Faible": "green"}
                                          c = risk_colors.get(weather["risk"], "blue")
                                          st.markdown(f"<span style='color: {c}; font-weight: bold;'>Risque {weather['risk']}</span> : {weather['msg']}", unsafe_allow_html=True)
                                      else:
                                          st.info(weather["msg"])


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
                                  st.success("✅ L'analyse a été sauvegardée dans votre historique.")
                              except Exception as e:
                                  st.error(f"Erreur lors de la sauvegarde : {e}")
                          else:
                              st.warning("ℹ️ L'analyse n'a pas été sauvegardée (mode invité ou aucune culture sélectionnée).")