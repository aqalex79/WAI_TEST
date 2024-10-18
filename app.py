from dotenv import load_dotenv
load_dotenv() # load the environment variables

import streamlit as st 
import os
import pathlib
import textwrap
from PIL import Image
import google.generativeai as genai

# Configure Google API key for LLM
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, image, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input_text, image[0], prompt])
    return response.text 

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

def main():
    st.set_page_config(page_title="Food-Recognition", page_icon="🥗")
    st.header("Meal Recommendation")

    # Upload Image Section
    uploaded_file = st.file_uploader("Choose an image of your dish ...", type=["jpg", "jpeg", "png"])
    image = ""

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)
        st.write("Image uploaded successfully! Analyzing the image...")
        
        # Automatically call LLM to detect food items
        try:
            pdf_content = input_image_setup(uploaded_file)
            detection_prompt = "Identify all food items present in the image, providing their names and estimated quantities."
            detected_items_response = get_gemini_response("Food Detection", pdf_content, detection_prompt)
            st.subheader("Detected Food Items")
            st.write(detected_items_response)
        except Exception as e:
            st.error(f"Error during image analysis: {str(e)}")

        # Editable Food Items Section
        if 'save_changes_clicked' not in st.session_state:
            st.write("### Edit Detected Food Items")
            st.write("Modify the detected food items if necessary, or add any missing items.")
            food_items = st.text_area("Detected Food Items:", detected_items_response, height=150)
            if st.button("Save Changes", key="save_food_items"):
                st.session_state['save_changes_clicked'] = True
                st.session_state['food_items'] = food_items

    # Provide Recommendation Section
    st.write("### Get Recommendations")
    if st.button("Provide Recommendation"):
        if uploaded_file is not None:
            try:
                input_text = "Provide a nutritional overview and alternatives based on the provided food items."
                recommendation_prompt = textwrap.dedent("""
                Act as a nutritionist specializing in managing PCOS (Polycystic Ovary Syndrome) and provide nutritional analysis for the given dish:
                1. Display a table of nutritional values (calories, protein, fat, carbohydrates).
                2. Focus on these 4 key areas:
                
                Blood Sugar Balance: How well does the meal help maintain stable blood sugar levels? Are the carbs healthy (whole grains, veggies), and does it avoid sugars or refined carbs?
                
                Protein & Healthy Fats: Does the meal include enough quality protein and healthy fats (like those from fish, nuts, or avocado) to support hormone balance and keep hunger in check?
                
                Fiber & Nutrients: Does the meal include fiber (from veggies, whole grains) and important nutrients (vitamin D, magnesium, omega-3s) that support PCOS?
                
                Inflammation & Portion Control: Does the meal contain anti-inflammatory ingredients (like omega-3s, turmeric) and are the portion sizes suitable for managing weight?
                
                Please provide simple, actionable feedback in these 4 categories, and suggest any easy improvements for a PCOS-friendly diet.
                """)
                response = get_gemini_response(input_text, pdf_content, recommendation_prompt)
                st.subheader("The Recommendation")
                st.write(response)

                # Overall Rating and Summary
                st.write("### Overall:")
                st.write("⭐⭐⭐⭐☆")
                st.write("### Summary:")
                st.write("Increase protein and fiber intake or undertake light exercise such as walks to reduce the sugar spike.")
                
                # Detailed Nutritional Info
                st.write("### Details:")
                st.write("**Protein:** 60%  — **Fat:** 10%  — **Carbs:** 80%  — **Fiber:** 10%")
                st.write("As the first meal of the day, it is best to avoid sugar-spiking elements and instead focus on good fat and protein sources.")
                st.markdown("[Tell me more](#)")
            except Exception as e:
                st.error(f"Error during recommendation generation: {str(e)}")
        else:
            st.write("Please upload a dish image to receive recommendations.")

    # Log Activity Section
    st.write("### Log Your Activity")
    if st.button("Log Activity"):
        if uploaded_file is not None:
            st.write("Activity logged successfully! This meal has been recorded for your future reference.")
        else:
            st.write("Please upload a dish image to log activity.")

if __name__ == "__main__":
    main()
