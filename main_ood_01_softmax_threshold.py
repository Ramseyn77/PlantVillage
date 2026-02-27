import time

import numpy as np
import streamlit as st
import tensorflow as tf

MODEL = tf.keras.models.load_model("training_model.keras")

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

REJECT_MSG = "Je ne suis pas capable de predire sur ce genre d'image."


def model_prediction(test_image):
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=[128, 128])
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])
    prediction = MODEL.predict(input_arr, verbose=0)
    probs = prediction[0]
    result_index = int(np.argmax(probs))
    confidence = float(np.max(probs))
    return result_index, probs, confidence


st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox("Select Page", ["Home", "About", "Disease Recognition"])
conf_threshold = st.sidebar.slider("OOD - confidence min", 0.10, 0.99, 0.75, 0.01)

if app_mode == "Home":
    st.header("PhytoDiag IA - OOD #1 Softmax threshold")
    st.image("./home_image.JPG", use_container_width=True)

if app_mode == "About":
    st.header("About")
    st.write("Methode OOD #1: rejet si la confiance max softmax est trop faible.")

if app_mode == "Disease Recognition":
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
                result_index, probs, confidence = model_prediction(test_image)
                if confidence < conf_threshold:
                    st.error(REJECT_MSG)
                    st.metric("Confiance", f"{confidence * 100:.2f}%")
                else:
                    predicted_label = CLASS_NAMES[result_index]
                    is_healthy = "healthy" in predicted_label.lower()
                    st.success("Plante saine" if is_healthy else "Plante malade")
                    st.write(f"Categorie: {predicted_label}")
                    st.metric("Confiance", f"{confidence * 100:.2f}%")
                    top_idx = np.argsort(probs)[::-1][:5]
                    st.bar_chart({CLASS_NAMES[i]: probs[i] for i in top_idx})
