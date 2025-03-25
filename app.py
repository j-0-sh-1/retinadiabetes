import streamlit as st
import pymongo
import numpy as np
from PIL import Image
import base64
import datetime
import pandas as pd
import plotly.express as px
import tensorflow as tf

# MongoDB Connection Setup
MONGO_URI = "mongodb+srv://joshuailangovansamuel:i9KNhtkqhUibQEer@cluster0.pbvcd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGO_URI)
db = client['diabetes']
patients_collection = db['patients']

# Load the Trained Model
@st.cache_resource
def load_model():
    # Replace "trained_model.keras" with the path to your pre-trained model
    return tf.keras.models.load_model("trained_model.keras")

model = load_model()

# Preprocess Image for Model
def preprocess_image(image, img_size=(224, 224)):
    image = image.convert("RGB")
    image = image.resize(img_size)
    img_array = np.array(image) / 255.0  # Normalize to [0, 1]
    return np.expand_dims(img_array, axis=0)

# Classify Image Using Trained Model
def classify_image(image):
    img_array = preprocess_image(image)
    prediction = model.predict(img_array)[0]
    stages = ["No DR", "Mild", "Moderate", "Severe", "Proliferative"]
    pred_class = stages[np.argmax(prediction)]
    confidence = float(np.max(prediction))
    return pred_class, confidence

# Classification Module
def classification_tab():
    st.header("Classification Module")
    uploaded_file = st.file_uploader("Upload Retina Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        if st.button("Classify"):
            prediction, confidence = classify_image(image)
            st.write(f"**Prediction:** {prediction}")
            st.write(f"**Confidence:** {confidence:.2f}")
            if prediction != "No DR":
                if st.button("Add as New Patient"):
                    st.session_state['new_patient'] = {
                        "retinopathy_stage": prediction,
                        "confidence": confidence,
                        "image": base64.b64encode(uploaded_file.getvalue()).decode()
                    }
                    st.success("Please fill in patient details in the Patient Management tab.")

# Patient Management Module
def patient_management_tab():
    st.header("Patient Management Module")

    # Add New Patient
    st.subheader("Add New Patient")
    col1, col2 = st.columns(2)
    with col1:
        if 'new_patient' in st.session_state:
            new_patient = st.session_state['new_patient']
            st.write(f"Retinopathy Stage (from classification): {new_patient['retinopathy_stage']}")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        contact = st.text_input("Contact")
        diagnosis_date = st.date_input("Diagnosis Date", value=datetime.date.today())
        if st.button("Save Patient"):
            patient_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "contact": contact,
                "diagnosis_date": diagnosis_date.isoformat(),
                "retinopathy_stage": new_patient['retinopathy_stage'] if 'new_patient' in st.session_state else "Unknown",
                "daily_monitoring": [],
                "medication_adherence": [],
                "recommendations": {},
            }
            if 'new_patient' in st.session_state:
                patient_data["image"] = st.session_state['new_patient']['image']
                del st.session_state['new_patient']
            patients_collection.insert_one(patient_data)
            st.success("Patient added successfully!")

    # View Existing Patients
    with col2:
        st.subheader("Existing Patients")
        patient_names = [patient['name'] for patient in patients_collection.find()]
        selected_patient = st.selectbox("Select Patient", patient_names)
        if selected_patient:
            patient = patients_collection.find_one({"name": selected_patient})
            st.write(f"**Name:** {patient.get('name', 'N/A')}")
            st.write(f"**Age:** {patient.get('age', 'N/A')}")
            st.write(f"**Gender:** {patient.get('gender', 'N/A')}")
            st.write(f"**Contact:** {patient.get('contact', 'N/A')}")
            st.write(f"**Diagnosis Date:** {patient.get('diagnosis_date', 'N/A')}")
            st.write(f"**Retinopathy Stage:** {patient.get('retinopathy_stage', 'N/A')}")
            if 'daily_monitoring' in patient and patient['daily_monitoring']:
                st.write("**Daily Monitoring (Last Week):**")
                df = pd.DataFrame(patient['daily_monitoring'])
                st.dataframe(df)
            if 'image' in patient:
                st.image(base64.b64decode(patient['image']), caption="Retina Image", use_column_width=True)

# Analytics & Monitoring Module
def analytics_tab():
    st.header("Analytics & Monitoring Module")

    # Patient Selection
    patient_names = [patient['name'] for patient in patients_collection.find()]
    selected_patient = st.selectbox("Select Patient for Analytics", patient_names)
    patient = patients_collection.find_one({"name": selected_patient})

    # Blood Sugar Trend
    st.subheader("Blood Sugar Trend")
    if 'daily_monitoring' in patient and patient['daily_monitoring']:
        df = pd.DataFrame(patient['daily_monitoring'])
        df['date'] = pd.to_datetime(df['date'])
        fig = px.line(df, x='date', y='blood_sugar', title=f"Blood Sugar Levels for {patient['name']}")
        st.plotly_chart(fig)
    else:
        st.write("No daily monitoring data available.")

    # Activity Summary
    st.subheader("Activity Summary")
    if 'daily_monitoring' in patient and patient['daily_monitoring']:
        df = pd.DataFrame(patient['daily_monitoring'])
        activity_counts = df['activity'].value_counts()
        fig = px.bar(x=activity_counts.index, y=activity_counts.values, title="Activity Frequency")
        st.plotly_chart(fig)
    else:
        st.write("No activity data available.")

    # Retinopathy Stage Distribution
    st.subheader("Retinopathy Stage Distribution")
    stages = [p.get('retinopathy_stage', 'Unknown') for p in patients_collection.find()]
    df_stages = pd.DataFrame(stages, columns=["Stage"])
    fig = px.sunburst(df_stages, path=['Stage'], title="Retinopathy Stages Across Patients")
    st.plotly_chart(fig)

    # Medication Adherence
    st.subheader("Medication Adherence")
    if 'medication_adherence' in patient and patient['medication_adherence']:
        adherence_rate = sum(patient['medication_adherence']) / len(patient['medication_adherence']) * 100
        st.write(f"Adherence Rate: {adherence_rate:.2f}%")
        fig = px.bar(x=["Adherent", "Non-Adherent"], 
                     y=[sum(patient['medication_adherence']), len(patient['medication_adherence']) - sum(patient['medication_adherence'])],
                     title="Medication Adherence")
        st.plotly_chart(fig)
    else:
        st.write("No adherence data available.")

# Recommendations Module
def recommendations_tab():
    st.header("Recommendations Module")
    patient_names = [patient['name'] for patient in patients_collection.find()]
    selected_patient = st.selectbox("Select Patient for Recommendations", patient_names)
    patient = patients_collection.find_one({"name": selected_patient})

    # Recommendations based on Retinopathy Stage
    stage = patient.get('retinopathy_stage', 'Unknown')
    st.write(f"**Patient:** {patient['name']}")
    st.write(f"**Retinopathy Stage:** {stage}")
    if stage == "No DR":
        st.write("**Recommendation:** Monitor annually.")
    elif stage == "Mild":
        st.write("**Recommendation:** Metformin daily, regular exercise, next checkup in 6 months.")
    elif stage == "Moderate":
        st.write("**Recommendation:** Insulin twice daily, reduce carbohydrate intake, next checkup in 3 months.")
    elif stage in ["Severe", "Proliferative"]:
        st.write("**Recommendation:** Insulin and laser therapy, strict diet control, next checkup in 1 month.")
    else:
        st.write("**Recommendation:** Consult a specialist for further evaluation.")

# Main App Structure
st.title("Diabetic Retinopathy Management System")
st.markdown("A comprehensive tool for managing diabetic retinopathy with classification, patient management, analytics, and recommendations.")

tab1, tab2, tab3, tab4 = st.tabs(["Classification", "Patient Management", "Analytics & Monitoring", "Recommendations"])

with tab1:
    classification_tab()

with tab2:
    patient_management_tab()

with tab3:
    analytics_tab()

with tab4:
    recommendations_tab()

# Close MongoDB connection (optional, Streamlit keeps it open during runtime)
# client.close()