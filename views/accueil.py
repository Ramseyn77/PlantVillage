import streamlit as st

def show():
    st.header('PhytoDiag IA')
    image_path = "./home_image.JPG"
    st.image(image_path, use_container_width=True)
    st.markdown("""
    #### Bienvenue dans le système de reconnaissance des maladies des plantes

    Notre mission est d'aider à identifier efficacement les maladies des plantes. Téléversez une image d'une plante et notre système l'analysera 
    pour détecter tout signe de maladie. Ensemble, protégeons nos cultures et assurons un avenir plus sain.
    """)