import streamlit as st
import tensorflow as tf
import numpy as np
import time

# Tensoflow Model Prediction
def model_prediction(test_image):
    model = tf.keras.models.load_model('training_model.keras')
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=[128, 128])
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])  # Convert simple image to batch
    prediction = model.predict(input_arr)
    probs = prediction[0]
    result_index = int(np.argmax(probs))
    confidence = float(np.max(probs))
    return result_index, probs, confidence



#SideBar 

st.sidebar.title("PhytoDiag IA")
app_mode = st.sidebar.selectbox('Select Page', ['Home', 'About', 'Disease Recognition'])

#Home Page 
if (app_mode == "Acceul") :
    st.header('PhytoDiag IA')
    image_path = "./home_image.JPG"
    st.image(image_path, use_column_width=True)
    st.markdown("""
    #### Bienvenue dans le système de reconnaissance des maladies des plantes

    Notre mission est d'aider à identifier efficacement les maladies des plantes. Téléversez une image d'une plante et notre système l'analysera 
    pour détecter tout signe de maladie. Ensemble, protégeons nos cultures et assurons un avenir plus sain.
""")

# About Page

if(app_mode =='A propos') :
    st.header("À propos")
    st.markdown("""
    ### À propos
    #### 1. Objectif
        Développer une application web qui détecte automatiquement l’état de santé d’une plante à partir d’une 
        image (saine ou malade) et identifie la maladie probable.
    #### 2. Contexte
        Le projet utilise un jeu de données de feuilles (poivron, pomme de terre, tomate) et
        des modèles IA déjà entraînés (training_model.keras, YOLO).
    #### 3. Périmètre
        Téléversement d’image via l'interface web (Streamlit).
        Prédiction de la classe (maladie/sain).
        Affichage du niveau de confiance.
        Affichage des meilleures prédictions.
        Version locale.
    """)

# Disease Recognition Page 
if(app_mode == 'Page de reconnaissance') :
    st.header("Reconnaissance des maladies")
    test_image = st.file_uploader('Choisissez une image...')
    if(st.button('Afficher l\'image')) :
        st.image(test_image, use_column_width=True)
    # Predict Button 
    if(st.button('Prédire')) :
        with st.spinner("Veuillez patienter ...") :
            time.sleep(3)
            st.write("Notre prédiction")
            result_index, probs, confidence = model_prediction(test_image)
            # Define Class
            class_names = ["Pepper__bell___Bacterial_spot",   "Pepper__bell___healthy",     "Potato___Early_blight",  "Potato___Late_blight",  "Potato___healthy",       
            "Tomato_Bacterial_spot",  "Tomato_Early_blight" , "Tomato_Late_blight" , "Tomato_Leaf_Mold" , "Tomato_Septoria_leaf_spot" ,      
            "Tomato_Spider_mites_Two_spotted_spider_mite" ,"Tomato__Target_Spot", "Tomato__Tomato_YellowLeaf__Curl_Virus" ,"Tomato__Tomato_mosaic_virus" ,       
            "Tomato_healthy" , ]
            predicted_label = class_names[result_index]
            is_healthy = "healthy" in predicted_label.lower()
            status_color = "#2ecc71" if is_healthy else "#e74c3c"
            status_text = "🌿 Plante saine" if is_healthy else "⚠️ Plante malade"

            st.markdown(
                f"""
                <div style="
                    padding: 1rem;
                    border-radius: 10px;
                    background-color: {status_color}22;
                    border: 2px solid {status_color};
                    text-align: center;
                    ">
                    <h3 style="margin: 0; color: {status_color};">{status_text}</h3>
                    <p style="margin: 0.3rem 0 0; font-size: 1.1rem;">Catégorie : <b>{predicted_label}</b></p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.metric("Confiance", f"{confidence * 100:.2f}%")

            # Affichage des 5 meilleures classes
            top_k = min(5, len(class_names))
            sorted_idx = np.argsort(probs)[::-1][:top_k]
            st.write("Top prédictions :")
            st.bar_chart(
                {class_names[i]: probs[i] for i in sorted_idx}
            )