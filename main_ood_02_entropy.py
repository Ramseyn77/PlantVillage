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
EPS = 1e-10


def model_prediction(test_image):
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=[128, 128])
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])
    prediction = MODEL.predict(input_arr, verbose=0)
    probs = prediction[0]
    result_index = int(np.argmax(probs))
    confidence = float(np.max(probs))
    entropy = float(-np.sum(probs * np.log(probs + EPS)))
    return result_index, probs, confidence, entropy


st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox("Select Page", ["Home", "About", "Disease Recognition"])
entropy_threshold = st.sidebar.slider("OOD - entropy max", 0.10, 3.00, 1.80, 0.01)

if app_mode == "PhytoDiag":
    st.header("PhytoDiag IA - OOD #2 Entropy")
    st.image("./home_image.JPG", use_container_width=True)

if app_mode == "A propos":
    st.header("About")
    st.write("Methode OOD #2: rejet si l'entropie de la distribution est trop elevee.")

if app_mode == "age de  reconnaissance":
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
                result_index, probs, confidence, entropy = model_prediction(test_image)
                if entropy > entropy_threshold:
                    st.error(REJECT_MSG)
                    st.metric("Confiance", f"{confidence * 100:.2f}%")
                    st.metric("Entropie", f"{entropy:.4f}")
                else:
                    predicted_label = CLASS_NAMES[result_index]
                    is_healthy = "healthy" in predicted_label.lower()
                    st.success("Plante saine" if is_healthy else "Plante malade")
                    st.write(f"Categorie: {predicted_label}")
                    st.metric("Confiance", f"{confidence * 100:.2f}%")
                    st.metric("Entropie", f"{entropy:.4f}")
                    top_idx = np.argsort(probs)[::-1][:5]
                    st.bar_chart({CLASS_NAMES[i]: probs[i] for i in top_idx})
