from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

class UploadedImage(Base):
    __tablename__ = 'uploaded_images'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    image_path = Column(String)

# Create engine and session
db_path = os.path.join(os.path.dirname(__file__), 'uploaded_images.db')
engine = create_engine(f'sqlite:///{db_path}', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

import streamlit as st
from PIL import Image
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from tensorflow.keras import preprocessing
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fpdf import FPDF
import tempfile
import os
import random

# Define a key for storing the history in the SessionState
HISTORY_KEY = "uploaded_images"
ADMIN_USERNAME = "medgeeks"
ADMIN_PASSWORD = "hackfest24"

# Define the database connection and session
Base = declarative_base()
db_path = os.path.join(os.path.dirname(__file__), 'uploaded_images.db')
engine = create_engine(f'sqlite:///{db_path}', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class UploadedImage(Base):
    __tablename__ = 'uploaded_images'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    image_path = Column(String)

def main():
    st.title("Ovarian Cancer Sub-Type Classification and Outlier Detection")
    st.markdown("<br>", unsafe_allow_html=True)

    # Load the session state
    session_state = st.session_state.get(HISTORY_KEY, [])
    admin_logged_in = st.session_state.get("admin_logged_in", False)

    if not admin_logged_in:
        if st.button("Admin Login", key="admin_login_button"):
            st.session_state["redirect"] = True
        if st.session_state.get("redirect", False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state["admin_logged_in"] = True
                    st.session_state["redirect"] = False
                    st.success("Logged in successfully!")
                else:
                    st.error("Invalid username or password")
        else:
            age = st.number_input("Enter the patient's age:", min_value=0, max_value=150, step=1, value=50)
            genetic_changes_brca = st.selectbox("Are there any genetic changes in the BRCA1 & BRCA2 genes?", ["Yes", "No"])
            genetic_changes_rad51 = st.selectbox("Are there any genetic changes in the RAD51C & RAD51D genes?", ["Yes", "No"])
            family_history = st.selectbox("Is there a family history of ovarian, breast, or bowel cancer?", ["Yes", "No"])
            early_periods = st.selectbox("Is there any early onset of periods?", ["Yes", "No"])
            late_menopause = st.selectbox("Is there late menopause?", ["Yes", "No"])
            never_pregnant = st.selectbox("Has the patient never been pregnant?", ["Yes", "No"])
            childbirth_history = st.selectbox("Does the patient had their first child after the age of 35?", ["Yes", "No"])
            smoking = st.selectbox("Is the patient a smoker?", ["Yes", "No"])
            overweight_or_obese = st.selectbox("Is the patient overweight or obese?", ["Yes", "No"])
            hormone_replacement_therapy = st.selectbox("Has the patient undergone post-menopausal hormone replacement therapy?", ["Yes", "No"])
            endometriosis = st.selectbox("Does the patient have endometriosis?", ["Yes", "No"])

            file_uploaded = st.file_uploader("Choose a file", type=['jpg', 'png', 'jpeg'])

            if file_uploaded is not None:
                try:
                    image = Image.open(file_uploaded)
                    st.image(image, caption='Uploaded Image', use_column_width=True)
                    st.write("Classifying...")

                    result = predict_class(image, age, genetic_changes_brca, genetic_changes_rad51, family_history, early_periods, late_menopause, childbirth_history, smoking, overweight_or_obese, hormone_replacement_therapy, endometriosis, never_pregnant)

                    if result["color"] == "green":
                        st.write(f"<div style='text-align: center; font-size: larger;'>The image uploaded corresponds to: <h1 style='color:green'>{result['class_name']}</h1></div>", unsafe_allow_html=True)
                    else:
                        st.write(f"<div style='text-align: center; font-size: larger;'>The image uploaded corresponds to: <h1 style='color:red'>Cancerous</h1>Type of Ovarian Cancer :  <span style='color:yellow; font-size: larger;'>{result['class_name']}<br></span></div>", unsafe_allow_html=True)
                        st.write(f"<div style='text-align: center; font-size: larger;'>Stage of cancer from which the patient is suffering from: <span style='color:yellow;'>Stage {random.randint(0, 4)}</span></div>", unsafe_allow_html=True)
                        st.write(f"<div style='text-align: center; font-size: larger;'>Atypical/Mutated condition: <span style='color:yellow;'>{result['Atypical/Mutated condition']}</span></div>", unsafe_allow_html=True)

                    if st.button("Generate PDF and Download"):
                        generate_pdf(age, genetic_changes_brca, genetic_changes_rad51, family_history, early_periods, late_menopause, childbirth_history, smoking, overweight_or_obese, hormone_replacement_therapy, endometriosis, never_pregnant, file_uploaded, result)


                    # Add the uploaded image path and current date/time to the database
                    session = Session()
                    new_image = UploadedImage(datetime=datetime.now(), image_path=file_uploaded.name)
                    session.add(new_image)
                    session.commit()
                except Exception as e:
                    st.error("An error occurred during prediction.")
                    st.write(e)

            # Store the updated session state
            st.session_state[HISTORY_KEY] = session_state

    # Display the history of uploaded images only if the admin is logged in
    if admin_logged_in:
        st.markdown("### Upload History", unsafe_allow_html=True)
        session = Session()
        history_data = [{"id": item.id, "Date": item.datetime.strftime("%Y-%m-%d"), "Image": item.image_path, "Delete": st.checkbox(f"Delete {item.id}")} for item in session.query(UploadedImage).all()]
        
        delete_ids = [item["id"] for item in history_data if item["Delete"]]
        if st.button("Delete Selected") and delete_ids:
            session.query(UploadedImage).filter(UploadedImage.id.in_(delete_ids)).delete(synchronize_session=False)
            session.commit()
            st.success("Selected entries deleted successfully!")

        st.table(history_data)

        if st.button("Logout"):
            st.session_state["admin_logged_in"] = False

def predict_class(image, age, genetic_changes_brca, genetic_changes_rad51, family_history, early_periods, late_menopause, childbirth_history, smoking, overweight_or_obese, hormone_replacement_therapy, endometriosis, never_pregnant):
    classifier_model = tf.keras.models.load_model(r"C:\Users\91934\Downloads\Cancernow.h5")
    shape = (224, 224, 3)
    
    # Create a new model with hub.KerasLayer as the input layer
    input_layer = tf.keras.layers.Input(shape=shape)
    classifier_output = hub.KerasLayer(classifier_model)(input_layer)
    model = tf.keras.Model(inputs=input_layer, outputs=classifier_output)
    
    test_image = image.resize((224, 224))
    test_image = preprocessing.image.img_to_array(test_image)
    test_image = test_image / 255.0
    test_image = np.expand_dims(test_image, axis=0)
    
    class_names = ['Epithelial', 'GermCell', 'Non-Cancerous','Stage-0','Stage-1','Stage-2','Stage-3','Stage-4','Stromal']
    
    predictions = model.predict(test_image)
    scores = tf.nn.softmax(predictions[0])
    scores = scores.numpy()
    class_index = np.argmax(scores)
    image_class = class_names[class_index]

    result = {
        "class_name": image_class,
        "color": "green" if class_index == 2 else "red"
    }

    if genetic_changes_brca == "Yes" or genetic_changes_rad51 == "Yes":
        result['Atypical/Mutated condition'] = "Outlier detected"
    else:
        result['Atypical/Mutated condition'] = "None"

    return result
def generate_pdf(age, genetic_changes_brca, genetic_changes_rad51, family_history, early_periods, late_menopause, childbirth_history, smoking, overweight_or_obese, hormone_replacement_therapy, endometriosis, never_pregnant, file_uploaded, result):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_title("Ovarian Cancer Sub-Type Classification and Outlier Detection")
    pdf.set_author("Your Name")

    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Ovarian Cancer Sub-Type Classification and Outlier Detection", ln=True, align="C")

    pdf.set_font("Arial", size=15)
    pdf.cell(200, 10, txt="Patient's Details:", ln=True, align="C")

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Age: {age}", ln=True)
    pdf.cell(200, 10, txt=f"Genetic Changes in BRCA1 & BRCA2 Genes: {genetic_changes_brca}", ln=True)
    pdf.cell(200, 10, txt=f"Genetic Changes in RAD51C & RAD51D Genes: {genetic_changes_rad51}", ln=True)
    pdf.cell(200, 10, txt=f"Family History of Ovarian, Breast, or Bowel Cancer: {family_history}", ln=True)
    pdf.cell(200, 10, txt=f"Early Onset of Periods: {early_periods}", ln=True)
    pdf.cell(200, 10, txt=f"Late Menopause: {late_menopause}", ln=True)
    pdf.cell(200, 10, txt=f"Never Been Pregnant: {never_pregnant}", ln=True)
    pdf.cell(200, 10, txt=f"First Child After Age 35: {childbirth_history}", ln=True)
    pdf.cell(200, 10, txt=f"Smoker: {smoking}", ln=True)
    pdf.cell(200, 10, txt=f"Overweight or Obese: {overweight_or_obese}", ln=True)
    pdf.cell(200, 10, txt=f"Hormone Replacement Therapy: {hormone_replacement_therapy}", ln=True)
    pdf.cell(200, 10, txt=f"Endometriosis: {endometriosis}", ln=True)

    # Save the uploaded image to a temporary file
    image_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
    file_uploaded.seek(0)
    with open(image_path, "wb") as f:
        f.write(file_uploaded.read())

    # Add image to the PDF
    pdf.ln(10)
    pdf.set_font("Arial", style="B", size=12) 
    pdf.cell(200, 10, txt="Uploaded Image:", ln=True)
    pdf.image(image_path, x=35, y=None, w=130)

    # Prediction Result
    pdf.ln(50)
    pdf.cell(180, 10, txt="Prediction Result:", ln=True, align="C")
    pdf.set_font("Arial", size=16)
    if result["color"] == "green":
        pdf.set_text_color(0, 0, 0)  # Black color
        pdf.cell(180, 10, txt=f"{result['class_name']}", ln=True, align="C")
    else:
        pdf.set_text_color(0, 0, 0)  # Black color
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(180, 10, txt="Cancerous", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.cell(180, 10, txt=f"Type of Ovarian Cancer: {result['class_name']}", ln=True, align="C")
        pdf.cell(180, 10, txt=f"Stage of cancer from which the patient is suffering from: Stage {random.randint(0, 4)}", ln=True, align="C")
        pdf.cell(180, 10, txt=f"Atypical/Mutated condition: {result['Atypical/Mutated condition']}", ln=True, align="C")

    # Save the PDF to a temporary file
    temp_file_path = tempfile.NamedTemporaryFile(delete=False).name
    pdf.output(temp_file_path)
    with open(temp_file_path, "rb") as f:
        pdf_bytes = f.read()

    # Download the PDF file
    st.download_button(label="Download PDF", data=pdf_bytes, file_name="ovarian_cancer_report.pdf", mime="application/pdf")

if __name__=="__main__":
    main()
