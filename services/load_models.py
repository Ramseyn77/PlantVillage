import streamlit as st
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2

@st.cache_resource
def load_disease_model():
    return tf.keras.models.load_model("training_model.keras")

@st.cache_resource
def load_filter_model():
    return MobileNetV2(weights="imagenet")