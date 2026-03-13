import streamlit as st
from services.load_models import load_disease_model, load_filter_model
from services.predictor import plant_gate, model_prediction
from utils.dispositions import dispositions_agricoles

import time
import numpy as np

def show():
  st.title("Reconnaissance des maladies")

  disease_model = load_disease_model()
  filter_model = load_filter_model()

  test_image = st.file_uploader("Choisissez une image...", type=["jpg","jpeg","png"])

  if test_image is not None:
      if st.button("Prédire"):
          with st.spinner("Analyse en cours..."):
              is_plant, top5 = plant_gate(test_image, filter_model)

              if not is_plant:
                  st.error("Image non reconnue comme plante.")
              else:
                  result_index, probs, confidence = model_prediction(
                      test_image,
                      disease_model
                  )

                  st.success(f"Classe prédite : {result_index}")
                  st.metric("Confiance", f"{confidence*100:.2f}%")