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

st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox('Select Page', ['Home', 'About', 'Disease Recognition'])

#Home Page 
if (app_mode == "Home") :
    st.header('PLANT DISEASE RECOGNITION SYSTEM')
    image_path = "./home_image.JPG"
    st.image(image_path, use_column_width=True)
    st.markdown("""
    #### Welcome to the Plant Disease Recognition System

    Our mission is to help in identifying plant diseases efficiently. Upload an image of a plant and our system will analyze 
    it to detect any signs of disease. Together, let's protect our crops ans ensure a healthier  
""")

# About Page

if(app_mode =='About') :
    st.header("About")
    st.markdown("""
    #### About Dataset
    """)

# Disease Recognition Page 
if(app_mode == 'Disease Recognition') :
    st.header("Disease Recognition")
    test_image = st.file_uploader('Choose an image....')
    if(st.button('Show Image')) :
        st.image(test_image, use_column_width=True)
    # Predict Button 
    if(st.button('Predict')) :
        with st.spinner("Please wait ....") :
            time.sleep(3)
            st.write("Our Prédiction")
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