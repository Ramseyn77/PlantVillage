import time

import numpy as np
import streamlit as st
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2,
    decode_predictions,
    preprocess_input,
)

DISEASE_MODEL = tf.keras.models.load_model("training_model.keras")
FILTER_MODEL = MobileNetV2(weights="imagenet")

CLASS_NAMES = [
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite",
    "Tomato__Target_Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus",
    "Tomato__Tomato_mosaic_virus",
    "Tomato_healthy",
]

PLANT_KEYWORDS = {
    "plant",
    "leaf",
    "bell_pepper",
    "cucumber",
    "zucchini",
    "broccoli",
    "cauliflower",
    "corn",
    "mushroom",
}

REJECT_MSG = "Je ne suis pas capable de predire sur ce genre d'image."


def plant_gate(test_image):
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=[224, 224])
    arr = tf.keras.preprocessing.image.img_to_array(image)
    arr = preprocess_input(np.array([arr]))
    preds = FILTER_MODEL.predict(arr, verbose=0)
    top5 = decode_predictions(preds, top=5)[0]
    keep = False
    for _, label, _ in top5:
        label_norm = label.lower()
        if any(keyword in label_norm for keyword in PLANT_KEYWORDS):
            keep = True
            break
    return keep, top5


def disease_prediction(test_image):
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=[128, 128])
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])
    prediction = DISEASE_MODEL.predict(input_arr, verbose=0)
    probs = prediction[0]
    result_index = int(np.argmax(probs))
    confidence = float(np.max(probs))
    return result_index, probs, confidence


st.sidebar.title("PyhtoDiag IA")
app_mode = st.sidebar.selectbox("Select Page", ["Home", "About", "Disease Recognition"])
conf_threshold = st.sidebar.slider("Disease confidence min", 0.10, 0.99, 0.70, 0.01)

if app_mode == "Acceuil":
    st.header("PhytoDiag IA - OOD #4 Visual gate (ImageNet)")
    st.image("./home_image.JPG", use_container_width=True)

if app_mode == "A propos":
    st.header("A propos")
    st.write("Methode OOD #4: filtre visuel generaliste avant le modele maladie.")

if app_mode == "Reconnaissance des maladies":
    st.header("Reconnaissance des maladies")
    test_image = st.file_uploader("Choisissez une image...", type=["jpg", "jpeg", "png"])
    if st.button("Afficher l'image") and test_image is not None:
        st.image(test_image, use_container_width=True)

    if st.button("Predire"):
        if test_image is None:
            st.warning("Veuillez choisir une image.")
        else:
            with st.spinner("Veuillez patienter ..."):
                time.sleep(1)
                is_plant_like, top5_filter = plant_gate(test_image)
                st.write("Top-5 filtre ImageNet:")
                st.write([f"{label}: {score:.3f}" for _, label, score in top5_filter])

                if not is_plant_like:
                    st.error(REJECT_MSG)
                else:
                    result_index, probs, confidence = disease_prediction(test_image)
                    if confidence < conf_threshold:
                        st.error(REJECT_MSG)
                    else:
                        predicted_label = CLASS_NAMES[result_index]
                        is_healthy = "healthy" in predicted_label.lower()
                        st.success("Plante saine" if is_healthy else "Plante malade")
                        st.write(f"Categorie: {predicted_label}")
                        st.metric("Confiance", f"{confidence * 100:.2f}%")
                        top_idx = np.argsort(probs)[::-1][:5]
                        st.bar_chart({CLASS_NAMES[i]: probs[i] for i in top_idx})
