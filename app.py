import streamlit as st 
import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import streamlit.components.v1 as components
import textwrap
import re
import traceback
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Google API key for LLM
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, image, prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([input_text, image[0], prompt])
        return response.text
    except Exception as e:
        raise RuntimeError(f"Failed to get response from Gemini: {e}")

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

def parse_nutritional_values(llm_response):
    nutritional_values = {
        'protein': 0,
        'fat': 0,
        'carbs': 0,
        'fiber': 0
    }

    patterns = [
        r'(\w+):\s*(\d+(?:\.\d+)?)%',
        r'(\w+):\s*(\d+(?:\.\d+)?)',
        r'(\w+)\s*:\s*(\d+(?:\.\d+)?)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, llm_response, re.IGNORECASE)
        for nutrient, value in matches:
            nutrient = nutrient.lower()
            if nutrient in nutritional_values:
                nutritional_values[nutrient] = round(float(value))

    return nutritional_values

def nutrition_bar_chart(nutritional_values):
    return f"""
    <div id="nutrition-chart"></div>
    <script>
    (function() {{
        const nutritionalValues = {nutritional_values};
        const colors = {{
            'protein': '#4CAF50',
            'fat': '#F44336',
            'carbs': '#FFC107',
            'fiber': '#2196F3'
        }};

        function createNutritionBar(label, value, color) {{
            const barContainer = document.createElement('div');
            barContainer.style.marginBottom = '10px';

            const labelSpan = document.createElement('span');
            labelSpan.textContent = `${{label}}: ${{value}}%`;
            barContainer.appendChild(labelSpan);

            const barBackground = document.createElement('div');
            barBackground.style.width = '100%';
            barBackground.style.backgroundColor = '#e0e0e0';
            barBackground.style.borderRadius = '5px';
            barBackground.style.marginTop = '5px';

            const bar = document.createElement('div');
            bar.style.width = `${{value}}%`;
            bar.style.height = '10px';
            bar.style.backgroundColor = color;
            bar.style.borderRadius = '5px';

            barBackground.appendChild(bar);
            barContainer.appendChild(barBackground);

            return barContainer;
        }}

        const chartContainer = document.getElementById('nutrition-chart');
        chartContainer.style.padding = '20px';
        chartContainer.style.backgroundColor = '#f5f5f5';
        chartContainer.style.borderRadius = '10px';

        for (const [nutrient, value] of Object.entries(nutritionalValues)) {{
            const bar = createNutritionBar(nutrient.charAt(0).toUpperCase() + nutrient.slice(1), value, colors[nutrient]);
            chartContainer.appendChild(bar);
        }}
    }})();
    </script>
    """

def main():
    st.set_page_config(page_title="Food-Recognition", page_icon="🥗", layout="wide")
    
    # Custom CSS
    st.markdown("""
    <style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
        font-family: Arial, sans-serif;
    }
    .upload-btn {
        background-color: #a8d8bf !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 20px !important;
        padding: 0.5em 1em !important;
    }
    .provide-recommendation-btn, .log-activity-btn {
        background-color: #FFC0CB !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 20px !important;
        padding: 0.5em 1em !important;
    }
    .footer-nav {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 800px;
        display: flex;
        justify-content: space-around;
        background-color: #f8f8f8;
        padding: 10px 0;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    }
    .footer-nav a {
        text-decoration: none;
        color: black;
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 12px;
    }
    .footer-nav img {
        width: 24px;
        height: 24px;
        margin-bottom: 4px;
    }
    .footer-nav a.active {
        color: #4a90e2;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.header("Meal Recommendation")

    uploaded_file = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"], key="upload_photo")
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)
        st.success("Image uploaded successfully! Analyzing the image...")

        try:
            image_content = input_image_setup(uploaded_file)
            detection_prompt = "Identify all food items present in the image, providing their names and estimated quantities."
            detected_items_response = get_gemini_response("Food Detection", image_content, detection_prompt)

            st.subheader("Detected Food Items")
            st.write(detected_items_response)

            if 'food_items' not in st.session_state:
                st.session_state['food_items'] = detected_items_response

            st.write("### Edit Detected Food Items")
            food_items = st.text_area("Detected Food Items:", st.session_state.get('food_items', ''), height=150)

            if st.button("Save Changes", key="save_food_items"):
                st.session_state['food_items'] = food_items
                st.success("Changes saved!")

            st.write("### Updated Food Items")
            st.write(st.session_state['food_items'])
    
            st.write("### Nutritional Analysis and PCOS Recommendations")
            if st.button("Provide Recommendation", key="provide_recommendation", help="Get nutritional analysis and PCOS recommendations"):
                try:
                    # Nutritional Analysis
                    nutrition_prompt = textwrap.dedent(f"""
                    Provide a nutritional analysis for the following dish:
                    {st.session_state['food_items']}
                    Just simply display(no extra wordings) the nutritional values as percentages for protein, fat, carbs, and fiber. Please use assumptions for the weight of the dish.
                    Format your response like this:
                    Protein: X%
                    Fat: Y%
                    Carbs: Z%
                    Fiber: W%
                    Where X, Y, Z, and W are numeric values.
                    """)

                    nutrition_response = get_gemini_response("Nutrition Analysis", image_content, nutrition_prompt)
                    nutritional_values = parse_nutritional_values(nutrition_response)

                    st.write("### Overall: ⭐⭐⭐⭐")
                    
                    st.write("### Summary:")
                    st.write("Increase protein and fiber intake or Undertake light exercise such as walks to reduce the sugar spike")

                    st.write("### Details:")
                    components.html(nutrition_bar_chart(nutritional_values), height=300, scrolling=True)

                    # PCOS Recommendations
                    pcos_prompt = textwrap.dedent(f"""
                    Act as a nutritionist specializing in managing PCOS (Polycystic Ovary Syndrome) and provide nutritional recommendations for the following dish:
                    {st.session_state['food_items']}
                    Focus on these 4 key areas:
                    1. Blood Sugar Balance: How well does the meal help maintain stable blood sugar levels? Are the carbs healthy (whole grains, veggies), and does it avoid sugars or refined carbs?
                    2. Protein & Healthy Fats: Does the meal include enough quality protein and healthy fats (like those from fish, nuts, or avocado) to support hormone balance and keep hunger in check?
                    3. Fiber & Nutrients: Does the meal include fiber (from veggies, whole grains) and important nutrients (vitamin D, magnesium, omega-3s) that support PCOS?
                    4. Inflammation & Portion Control: Does the meal contain anti-inflammatory ingredients (like omega-3s, turmeric) and are the portion sizes suitable for managing weight?
                    Please provide simple, actionable feedback in these 4 categories, and suggest any easy improvements for a PCOS-friendly diet.
                    """)

                    pcos_response = get_gemini_response("PCOS Recommendations", image_content, pcos_prompt)

                    st.subheader("PCOS Diet Recommendations")
                    st.write(pcos_response)

                    # Save rating to session state
                    st.session_state['current_meal_rating'] = 4  # Default rating, you can add input for user rating

                except Exception as e:
                    st.error("Error during analysis and recommendation generation. Please try again.")
                    st.error(f"Details: {str(e)}")

        except Exception as e:
            st.error(f"Error during image analysis: {e}")

    if st.button("Log Activity", key="log_activity", help="Log this meal activity"):
        if 'food_items' in st.session_state and uploaded_file:
            new_meal = {
                "name": st.session_state['food_items'],
                "time": datetime.now().strftime("%I:%M %p"),
                "rating": st.session_state.get('current_meal_rating', 0),
                "image": uploaded_file
            }
            if 'meal_log' not in st.session_state:
                st.session_state.meal_log = []
            st.session_state.meal_log.append(new_meal)
            st.success("Activity logged successfully! This meal has been recorded in your Meal Log.")
            st.markdown("[View Meal Log](meal_log)")
        else:
            st.write("Please upload a dish image and analyze it before logging activity.")

    footer_html = """
    <div class="footer-nav">
        <a href="page1.html">
            <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMCAyMXYtMmE0IDQgMCAwIDAtNC00SDhhNCA0IDAgMCAwLTQgNHYyIiAvPjxjaXJjbGUgY3g9IjEyIiBjeT0iNyIgcj0iNCI+PC9jaXJjbGU+PC9zdmc+" alt="Profile">
            <span>Profile</span>
        </a>
        <a href="#" class="active">
            <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIj48L2NpcmNsZT48cG9seWxpbmUgcG9pbnRzPSIxMiA2IDEyIDEyIDE2IDE0Ij48L3BvbHlsaW5lPjwvc3ZnPg==" alt="Meal Recommendations">
            <span>Meal Recommendations</span>
        </a>
        <a href="#">
            <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xNCAySDZhMiAyIDAgMCAwLTIgMnYxNmEyIDIgMCAwIDAgMiAyaDEyYTIgMiAwIDAgMCAyLTJWOHoiIC8+PHBvbHlsaW5lIHBvaW50cz0iMTQgMiAxNCA4IDIwIDgiPjwvcG9seWxpbmU+PGxpbmUgeDE9IjE2IiB5MT0iMTMiIHgyPSI4IiB5Mj0iMTMiPjwvbGluZT48bGluZSB4MT0iMTYiIHkxPSIxNyIgeDI9IjgiIHkyPSIxNyI+PC9saW5lPjxwb2x5bGluZSBwb2ludHM9IjEwIDkgOSA5IDggOSI+PC9wb2x5bGluZT48L3N2Zz4=" alt="Meal Log">
            <span>Meal Log</span>
        </a>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
