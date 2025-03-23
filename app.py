import streamlit as st
import tensorflow as tf
import numpy as np
import cv2
from PIL import Image

# Cache the model loading for faster re-runs
@st.cache(allow_output_mutation=True)
def load_model():
    model = tf.keras.models.load_model("trained_model.keras")
    return model

model = load_model()

def preprocess_image(image, img_size=(224, 224)):
    # Convert the uploaded image to RGB and resize it
    image = image.convert("RGB")
    img = np.array(image)
    img = cv2.resize(img, img_size)
    img = img / 255.0  # Normalize pixel values to [0,1]
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img

# Streamlit UI
st.title("Diabetic Retinopathy Classifier")
st.write("Upload an image to test for signs of diabetic retinopathy.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("Classify Image"):
        img = preprocess_image(image)
        prediction = model.predict(img)
        confidence = prediction[0][0]
        # Adjust threshold based on how the model was trained (here using 0.5 as threshold)
        label = "Diabetic Retinopathy" if confidence > 0.5 else "No Diabetic Retinopathy"
        st.write(f"**Prediction:** {label}")
        st.write(f"**Confidence:** {confidence:.4f}")
