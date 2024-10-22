import streamlit as st 
import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import streamlit.components.v1 as components
import textwrap
import re
from datetime import datetime
import io

# Load environment variables
load_dotenv()

# Configure Google API key for LLM
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 统一的 CSS 样式
css = """
<style>
.stApp {
    max-width: 800px;
    margin: 0 auto;
    font-family: Arial, sans-serif;
    padding-bottom: 70px;
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

/* Navigation styles */
.nav-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: white;
    padding: 10px;
    box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    z-index: 1000;
}

.nav-button {
    background-color: transparent;
    border: none;
    color: black;
    padding: 10px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    width: 33.33%;
    transition: all 0.3s ease;
}

.nav-button:hover {
    background-color: #e9ecef;
    transform: translateY(-5px);
}

.nav-button.active {
    color: #4a90e2;
    background-color: #e3f2fd;
}

</style>
"""

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

def navigation():
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👤 Profile", use_container_width=True):
            st.switch_page("pages/1_Profile.py")
    with col2:
        st.button("🕒 Recommendations", use_container_width=True, type="primary")
    with col3:
        if st.button("📝 Meal Log", use_container_width=True):
            st.switch_page("pages/3_Meal_Log.py")

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
    st.markdown(css, unsafe_allow_html=True)
    
    # Main content container
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
            if st.button("Provide Recommendation", key="provide_recommendation"):
                try:
                    nutrition_prompt = textwrap.dedent(f"""
                    Provide a nutritional analysis for the following dish:
                    {st.session_state['food_items']}
                    Just simply display(no extra wordings) the nutritional values as percentages for protein, fat, carbs, and fiber.
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
                    st.write("Increase protein and fiber intake or undertake light exercise such as walks to reduce the sugar spike")

                    st.write("### Details:")
                    components.html(nutrition_bar_chart(nutritional_values), height=300, scrolling=True)

                    pcos_prompt = textwrap.dedent(f"""
                    Act as a nutritionist specializing in managing PCOS (Polycystic Ovary Syndrome) and provide nutritional recommendations for the following dish:
                    {st.session_state['food_items']}
                    Focus on these 4 key areas:
                    1. Blood Sugar Balance
                    2. Protein & Healthy Fats
                    3. Fiber & Nutrients
                    4. Inflammation & Portion Control
                    Please provide simple, actionable feedback in these categories.
                    """)

                    pcos_response = get_gemini_response("PCOS Recommendations", image_content, pcos_prompt)
                    st.subheader("PCOS Diet Recommendations")
                    st.write(pcos_response)

                    st.session_state['current_meal_rating'] = 4

                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")

        except Exception as e:
            st.error(f"Error during image analysis: {e}")

    if st.button("Log Activity", key="log_activity"):
        if 'food_items' in st.session_state and uploaded_file:
            try:
                image_bytes = io.BytesIO()
                image = Image.open(uploaded_file)
                image.save(image_bytes, format='PNG')
                
                new_meal = {
                    "name": st.session_state['food_items'],
                    "time": datetime.now().strftime("%I:%M %p"),
                    "rating": st.session_state.get('current_meal_rating', 0),
                    "image": image_bytes.getvalue()
                }
                
                if 'meal_log' not in st.session_state:
                    st.session_state.meal_log = []
                
                st.session_state.meal_log.append(new_meal)
                st.success("Activity logged successfully!")
                st.switch_page("pages/3_Meal_Log.py")
            except Exception as e:
                st.error(f"Error saving meal log: {str(e)}")
        else:
            st.warning("Please upload a dish image and analyze it first.")

    # Add navigation
    navigation()

if __name__ == "__main__":
    main()