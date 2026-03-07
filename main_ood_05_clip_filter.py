import time

import numpy as np
import streamlit as st
import tensorflow as tf
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

DISEASE_MODEL = tf.keras.models.load_model("training_model.keras")
CLIP_NAME = "openai/clip-vit-base-patch32"
CLIP_MODEL = CLIPModel.from_pretrained(CLIP_NAME)
CLIP_PROCESSOR = CLIPProcessor.from_pretrained(CLIP_NAME)

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

CLIP_TEXTS = [
    "a photo of a pepper plant",
    "a photo of a potato plant",
    "a photo of a tomato plant",
    "a close-up photo of a plant leaf",
]

REJECT_MSG = "Je ne suis pas capable de predire sur ce genre d'image."


def clip_gate(test_image):
    pil_image = Image.open(test_image).convert("RGB")
    inputs = CLIP_PROCESSOR(
        text=CLIP_TEXTS,
        images=pil_image,
        return_tensors="pt",
        padding=True,
    )
    with torch.no_grad():
        outputs = CLIP_MODEL(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1).cpu().numpy()[0]
    best_idx = int(np.argmax(probs))
    best_score = float(probs[best_idx])
    return best_score, CLIP_TEXTS[best_idx], probs


def disease_prediction(test_image):
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=[128, 128])
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])
    prediction = DISEASE_MODEL.predict(input_arr, verbose=0)
    probs = prediction[0]
    result_index = int(np.argmax(probs))
    confidence = float(np.max(probs))
    return result_index, probs, confidence


st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox("Select Page", ["Home", "About", "Disease Recognition"])
clip_threshold = st.sidebar.slider("CLIP similarity min", 0.05, 0.95, 0.40, 0.01)
conf_threshold = st.sidebar.slider("Disease confidence min", 0.10, 0.99, 0.70, 0.01)

if app_mode == "Home":
    st.header("PhytoDiag IA - OOD #5 CLIP gate")
    st.image("./home_image.JPG", use_container_width=True)

if app_mode == "About":
    st.header("About")
    st.write("Methode OOD #5: filtre CLIP (image-text) avant prediction maladie.")

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
                clip_score, clip_text, clip_probs = clip_gate(test_image)
                st.metric("CLIP score", f"{clip_score:.3f}")
                st.write(f"Prompt le plus proche: {clip_text}")
                st.write(
                    {CLIP_TEXTS[i]: float(clip_probs[i]) for i in range(len(CLIP_TEXTS))}
                )

                if clip_score < clip_threshold:
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
