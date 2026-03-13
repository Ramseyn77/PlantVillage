import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import (
    decode_predictions,
    preprocess_input,
)

PLANT_KEYWORDS = {
    "plant", "leaf", "bell_pepper", "cucumber", 
    "zucchini", "broccoli", "cauliflower",
    "corn", "mushroom", "granny_smith",
    "daisy", "pot", "greenhouse"
}

def plant_gate(test_image, filter_model):
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=[224, 224])
    arr = tf.keras.preprocessing.image.img_to_array(image)
    arr = preprocess_input(np.array([arr]))

    preds = filter_model.predict(arr, verbose=0)
    top5 = decode_predictions(preds, top=5)[0]

    is_plant = any(
        keyword in label.lower()
        for _, label, _ in top5
        for keyword in PLANT_KEYWORDS
    )

    return is_plant, top5


def model_prediction(test_image, disease_model):
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=[128, 128])
    arr = tf.keras.preprocessing.image.img_to_array(image)
    arr = np.array([arr])

    prediction = disease_model.predict(arr, verbose=0)
    probs = prediction[0]

    return int(np.argmax(probs)), probs, float(np.max(probs))