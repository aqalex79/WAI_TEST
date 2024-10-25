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
import json

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Unified CSS styles
css = """
<style>
/* Main container */
.stApp {
    max-width: 800px;
    margin: 0 auto;
    font-family: Arial, sans-serif;
    padding-bottom: 120px;
}

/* Navigation styles */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    flex: 1 !important;
    min-width: 0 !important;
    margin: 0 !important;
    display: flex !important;
}

div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div > button {
    width: 100% !important;
    height: auto !important;
    min-height: 50px !important;
    padding: 8px 4px !important;
    margin: 0 4px !important;
    font-size: 12px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    white-space: nowrap !important;
}

/* Navigation container */
div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    gap: 8px !important;
    padding: 8px !important;
}

/* Main container padding */
.stApp {
    padding-bottom: 80px !important;
}

/* Ensure content scrolling */
[data-testid="stAppViewContainer"] {
    height: calc(100vh - 80px) !important;
    overflow-y: auto !important;
}

/* Mobile responsive */
@media (max-width: 768px) {
    div[data-testid="stHorizontalBlock"] {
        padding: 12px 15px !important;
        gap: 10px !important;
    }
    
    div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div > button {
        width: 90px !important;
        height: 75px !important;
        font-size: 12px !important;
    }
}

/* Content containers */
.content-container {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
</style>
"""

def navigation():
    cols = st.columns(3)
    with cols[0]:
        if st.button("👤\nProfile", use_container_width=True):
            st.switch_page("pages/1_Profile.py")
    with cols[1]:
        st.button("🕒\nRecommendations", use_container_width=True, type="primary")
    with cols[2]:
        if st.button("📝\nMeal Log", use_container_width=True):
            st.switch_page("pages/3_Meal_Log.py")

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

    try:
        # 更严格的匹配模式
        patterns = [
            r'(\w+):\s*(\d+(?:\.\d+)?)\s*%?',  # 匹配百分比或没有百分比的数字
        ]

        for pattern in patterns:
            matches = re.findall(pattern, llm_response, re.IGNORECASE)
            for nutrient, value in matches:
                nutrient = nutrient.lower().strip()
                if nutrient in nutritional_values:
                    try:
                        nutritional_values[nutrient] = round(float(value))
                    except ValueError:
                        continue

        return nutritional_values
    except Exception:
        return nutritional_values  # 返回默认值

def get_pcos_analysis(food_items, image_content, meal_type):
    # Get user symptoms and dietary preference from session state
    symptoms = st.session_state.get('selected_symptoms', [])
    dietary_preference = st.session_state.get('dietary_preference', '')
    
    pcos_prompt = textwrap.dedent(f"""
    You are a nutritionist specializing in managing PCOS (Polycystic Ovary Syndrome) through diet.
    
    Meal Information:
    Time: {meal_type}
    Dietary Preference: {dietary_preference}
    User Symptoms: {', '.join(symptoms)}
    Food Items: {food_items}
    
    Provide concise, structured feedback without detailed explanations following exactly this format:
    
    PCOS_SCORE: [Promising/Can Do Better/Needs Improvement]
    
    FOCUS_AREAS:
    Hormonal Balance & Insulin Sensitivity|[1-5]|[brief explanation]
    Inflammation Control & Gut Health|[1-5]|[brief explanation]
    Energy & Mental Health|[1-5]|[brief explanation]
    Reproductive Health & Fertility|[1-5]|[brief explanation]
    
    SUGGESTIONS:
    Quick Fix: [immediate adjustment]
    Swap Out: [healthier alternative]
    Pro Moves: [advanced recommendation]
    """)
    
    return get_gemini_response("PCOS Analysis", image_content, pcos_prompt)

def parse_pcos_response(response_text):
    """Parse PCOS analysis response into structured data"""
    lines = response_text.strip().split('\n')
    data = {
        'pcos_score': '',
        'focus_areas': {},
        'suggestions': {}
    }
    
    current_section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('PCOS_SCORE:'):
            data['pcos_score'] = line.split(':', 1)[1].strip()
            
        elif 'FOCUS_AREAS:' in line:
            current_section = 'focus_areas'
            continue
            
        elif 'SUGGESTIONS:' in line:
            current_section = 'suggestions'
            continue
            
        if current_section == 'focus_areas':
            if '|' in line:
                try:
                    area, score, explanation = line.split('|')
                    # 添加错误处理来确保score是一个有效的数字
                    score_str = score.strip('[]').strip()
                    try:
                        score_value = int(score_str)
                        data['focus_areas'][area.strip()] = {
                            'score': score_value,
                            'explanation': explanation.strip()
                        }
                    except ValueError:
                        # 如果无法解析为整数，使用默认值3
                        data['focus_areas'][area.strip()] = {
                            'score': 3,
                            'explanation': explanation.strip()
                        }
                except Exception:
                    continue
                
        elif current_section == 'suggestions':
            if ':' in line:
                key, value = line.split(':', 1)
                data['suggestions'][key.lower().replace(' ', '_')] = value.strip()
    
    return data

def nutrition_bar_chart(nutritional_values):
    """Create nutrition bar chart"""
    try:
        # 确保所有值都是有效的数字并且在0-100之间
        processed_values = {}
        for nutrient, value in nutritional_values.items():
            try:
                # 确保值是一个数字，并限制在0-100之间
                num_value = float(value)
                processed_values[nutrient] = min(max(0, round(num_value)), 100)
            except (ValueError, TypeError):
                processed_values[nutrient] = 0

        html = """
        <div style="font-family: Arial, sans-serif; background-color: #f8f9fa; border-radius: 8px; padding: 16px;">
        """
        
        colors = {
            'protein': '#4CAF50',
            'fat': '#F44336',
            'carbs': '#FFC107',
            'fiber': '#2196F3'
        }
        
        for nutrient, value in processed_values.items():
            html += f"""
            <div style="margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-weight: 500; font-size: 14px;">
                        {nutrient.capitalize()}
                    </span>
                    <span style="font-size: 14px;">
                        {value}%
                    </span>
                </div>
                <div style="width: 100%; height: 8px; background-color: #e0e0e0; border-radius: 4px; overflow: hidden;">
                    <div style="width: {value}%; height: 100%; background-color: {colors.get(nutrient, '#888')};">
                    </div>
                </div>
            </div>
            """
        
        html += "</div>"
        return html
    except Exception as e:
        # 如果发生任何错误，返回一个简单的错误提示
        return f"""
        <div style="font-family: Arial, sans-serif; background-color: #fff3f3; color: #d32f2f; padding: 12px; border-radius: 8px; font-size: 14px;">
            Unable to display nutritional analysis. Please try again.
        </div>
        """

def init_session_state():
    """Initialize session state variables"""
    if 'detection_complete' not in st.session_state:
        st.session_state.detection_complete = False
    if 'original_detection' not in st.session_state:
        st.session_state.original_detection = None
    if 'edited_food_items' not in st.session_state:
        st.session_state.edited_food_items = None
    if 'current_file_key' not in st.session_state:
        st.session_state.current_file_key = None

def get_meal_type(current_time):
    """Determine meal type based on time"""
    hour = current_time.hour
    if 3 <= hour < 11:
        return "Breakfast"
    elif 11 <= hour < 15:
        return "Lunch"
    else:
        return "Dinner"

def format_meal_output(detected_items, meal_type):
    """Format output with meal type and details"""
    items = [item.strip('• ').strip() for item in detected_items.split('\n') if item.strip()]
    meal_name = items[0].split('(')[0].strip() if items else "Unknown Meal"
    
    output = f"{meal_type}\n\n"
    output += "\n".join(f"• {item}" for item in items)
    
    return output, meal_name

def handle_image_upload(uploaded_file):
    """Handle image upload logic"""
    if uploaded_file:
        file_key = hash(uploaded_file.getvalue())
        
        if st.session_state.current_file_key != file_key:
            st.session_state.current_file_key = file_key
            st.session_state.detection_complete = False
            st.session_state.original_detection = None
            st.session_state.edited_food_items = None
            
        return True
    return False

def detect_food_items(image_content):
    """Detect food items from image"""
    detection_prompt = """
    List only the food items and their estimated weight in the image.
    Format as bullet points.
    Example format:
    • 1 slice of chocolate cake (150g)
    • 2 scoops of vanilla ice cream (100g)
    """
    return get_gemini_response("Food Detection", image_content, detection_prompt)

def main():
    st.set_page_config(page_title="Food-Recognition", page_icon="🥗", layout="wide")
    st.markdown(css, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    st.header("Meal Recommendation")

    uploaded_file = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"], key="upload_photo")
    
    if handle_image_upload(uploaded_file):
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)
        st.success("Image uploaded successfully! Analyzing the image...")

        try:
            image_content = input_image_setup(uploaded_file)
            
            if not st.session_state.detection_complete:
                detected_items_response = detect_food_items(image_content)
                current_time = datetime.now()
                meal_type = get_meal_type(current_time)
                formatted_output, meal_name = format_meal_output(detected_items_response, meal_type)
                
                st.session_state.original_detection = formatted_output
                st.session_state.meal_name = meal_name
                st.session_state.detection_complete = True
                st.session_state.edited_food_items = formatted_output

            st.subheader("Detected Food Items")
            current_items = st.session_state.edited_food_items or st.session_state.original_detection
            
            edited_items = st.text_area(
                "Edit Food Items:",
                value=current_items,
                height=150,
                key="food_items_editor"
            )
            
            if st.button("Save Changes", key="save_food_items"):
                st.session_state.edited_food_items = edited_items
                st.success("Changes saved successfully!")
            
            st.write("### Current Food Items")
            st.write(st.session_state.edited_food_items or st.session_state.original_detection)

            if st.button("Provide Recommendation", key="provide_recommendation"):
                current_food_items = st.session_state.edited_food_items or st.session_state.original_detection
                
                # 把整体分析过程放在外层 try-except 中
                try:
                    # Nutrition Analysis
                    nutrition_prompt = textwrap.dedent(f"""
                        Provide a nutritional analysis for the following dish:
                        {current_food_items}
                        Just simply display(no extra wordings) the nutritional values as percentages for protein, fat, carbs, and fiber.
                        Format your response like this:
                        Protein: X%
                        Fat: Y%
                        Carbs: Z%
                        Fiber: W%
                        Where X, Y, Z, and W are numeric values.
                        """)

                    # 单独处理营养分析的异常
                    nutrition_response = get_gemini_response("Nutrition Analysis", image_content, nutrition_prompt)
                    nutritional_values = parse_nutritional_values(nutrition_response)
                    
                    if any(nutritional_values.values()):  # 确保至少有一个非零值
                        st.write("### Nutritional Analysis")
                        chart_html = nutrition_bar_chart(nutritional_values)
                        components.html(chart_html, height=200, scrolling=False)
                        # 保存有效的营养分析结果
                        st.session_state['nutritional_values'] = nutritional_values
                    else:
                        st.warning("Could not determine nutritional values. Please try again.")
                        st.session_state['nutritional_values'] = {}

                    # PCOS Analysis - 不需要嵌套在内层 try-except 中
                    current_time = datetime.now()
                    meal_type = get_meal_type(current_time)
                    pcos_response = get_pcos_analysis(current_food_items, image_content, meal_type)
                    pcos_data = parse_pcos_response(pcos_response)

                    # Display PCOS analysis
                    st.write("### PCOS Analysis")
                    st.markdown(f"**PCOS Score:** {pcos_data['pcos_score']}")
                    
                    # Display Focus Areas
                    st.write("#### Focus Areas")
                    for area, data in pcos_data['focus_areas'].items():
                        col1, col2 = st.columns([3, 7])
                        with col1:
                            st.write(f"**{area}:**")
                        with col2:
                            # Create a progress bar
                            progress_html = f"""
                            <div style="background-color: #f0f2f6; border-radius: 10px; height: 20px; width: 100%">
                                <div style="background-color: #1f77b4; width: {data['score']*20}%; height: 100%; border-radius: 10px">
                                </div>
                            </div>
                            <p style="color: #666666; font-size: 14px; margin-top: 5px">{data['explanation']}</p>
                            """
                            st.markdown(progress_html, unsafe_allow_html=True)

                    # Display Actionable Suggestions
                    st.write("#### Actionable Suggestions")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("""
                        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 10px">
                            <p style="color: #1f77b4; font-weight: bold">⚡ Quick Fix</p>
                            <p style="font-size: 14px">{}</p>
                        </div>
                        """.format(pcos_data['suggestions'].get('quick_fix', '')), unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("""
                        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 10px">
                            <p style="color: #1f77b4; font-weight: bold">🔄 Swap Out</p>
                            <p style="font-size: 14px">{}</p>
                        </div>
                        """.format(pcos_data['suggestions'].get('swap_out', '')), unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown("""
                        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 10px">
                            <p style="color: #1f77b4; font-weight: bold">⭐ Pro Moves</p>
                            <p style="font-size: 14px">{}</p>
                        </div>
                        """.format(pcos_data['suggestions'].get('pro_moves', '')), unsafe_allow_html=True)

                    # Save analysis results
                    st.session_state['pcos_analysis'] = pcos_data

                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")

        except Exception as e:
            st.error(f"Error during image analysis: {e}")

    # Log Activity button
    if st.button("Log Activity", key="log_activity"):
        if 'edited_food_items' in st.session_state and uploaded_file:
            try:
                image_bytes = io.BytesIO()
                image = Image.open(uploaded_file)
                image.save(image_bytes, format='PNG')
                
                current_time = datetime.now()
                meal_type = get_meal_type(current_time)
                
                # Create meal log entry
                new_meal = {
                    "meal_type": meal_type,
                    "name": st.session_state.get('meal_name', 'Unknown Meal'),
                    "details": st.session_state.edited_food_items,
                    "time": current_time.strftime("%I:%M %p"),
                    "date": current_time.strftime("%Y-%m-%d"),
                    "image": image_bytes.getvalue(),
                    "nutrition_analysis": {
                        "values": st.session_state.get('nutritional_values', {}),
                    },
                    "pcos_analysis": {
                        "score": st.session_state.get('pcos_analysis', {}).get('pcos_score', ''),
                        "focus_areas": st.session_state.get('pcos_analysis', {}).get('focus_areas', {}),
                        "suggestions": st.session_state.get('pcos_analysis', {}).get('suggestions', {})
                    }
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

    # Add navigation at the bottom
    navigation()

if __name__ == "__main__":
    main()