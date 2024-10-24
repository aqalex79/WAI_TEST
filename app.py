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
    width: 100% !important;  /* 改为100%填充父容器 */
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

/* Main container - 添加底部间距防止内容被遮挡 */
.stApp {
    padding-bottom: 80px !important;  /* 确保内容不被导航栏遮挡 */
}

/* 确保内容可以滚动 */
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

/* Other buttons */
.stButton > button.upload-btn {
    background-color: #a8d8bf !important;
    color: black !important;
    border-radius: 12px !important;
    padding: 8px 16px !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}

.stButton > button.recommend-btn {
    background-color: #FFC0CB !important;
    color: black !important;
    border-radius: 12px !important;
    padding: 8px 16px !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
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

def init_session_state():
    """初始化session state变量"""
    if 'detection_complete' not in st.session_state:
        st.session_state.detection_complete = False
    if 'original_detection' not in st.session_state:
        st.session_state.original_detection = None
    if 'edited_food_items' not in st.session_state:
        st.session_state.edited_food_items = None
    if 'current_file_key' not in st.session_state:
        st.session_state.current_file_key = None

def get_meal_type(current_time):
    """根据当前时间判断用餐类型"""
    hour = current_time.hour
    if 3 <= hour < 11:
        return "Breakfast"
    elif 11 <= hour < 15:
        return "Lunch"
    else:
        return "Dinner"

def format_meal_output(detected_items, meal_type):
    """格式化输出结果，包含用餐类型和食物详情"""
    items = [item.strip('• ').strip() for item in detected_items.split('\n') if item.strip()]
    meal_name = items[0].split('(')[0].strip() if items else "Unknown Meal"
    
    output = f"{meal_type}\n\n"
    output += "\n".join(f"• {item}" for item in items)
    
    return output, meal_name

def handle_image_upload(uploaded_file):
    """处理图片上传逻辑"""
    if uploaded_file:
        file_key = hash(uploaded_file.getvalue())
        
        # 只有当上传新图片时才重置状态
        if st.session_state.current_file_key != file_key:
            st.session_state.current_file_key = file_key
            st.session_state.detection_complete = False
            st.session_state.original_detection = None
            st.session_state.edited_food_items = None
            
        return True
    return False

def detect_food_items(image_content):
    """检测食物项目"""
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
    
    # 初始化session state
    init_session_state()
    
    st.header("Meal Recommendation")

    uploaded_file = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"], key="upload_photo")
    
    if handle_image_upload(uploaded_file):
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)
        st.success("Image uploaded successfully! Analyzing the image...")

        try:
            image_content = input_image_setup(uploaded_file)
            
            # 只在首次检测或新图片上传时进行检测
            if not st.session_state.detection_complete:
                detected_items_response = detect_food_items(image_content)
                current_time = datetime.now()
                meal_type = get_meal_type(current_time)
                formatted_output, meal_name = format_meal_output(detected_items_response, meal_type)
                
                # 保存原始检测结果
                st.session_state.original_detection = formatted_output
                st.session_state.meal_name = meal_name
                st.session_state.detection_complete = True
                st.session_state.edited_food_items = formatted_output

            st.subheader("Detected Food Items")
            
            # 使用编辑后的内容或原始检测结果
            current_items = st.session_state.edited_food_items or st.session_state.original_detection
            
            # 编辑区域
            edited_items = st.text_area(
                "Edit Food Items:",
                value=current_items,
                height=150,
                key="food_items_editor"
            )
            
            # 保存按钮
            if st.button("Save Changes", key="save_food_items"):
                st.session_state.edited_food_items = edited_items
                st.success("Changes saved successfully!")
            
            # 显示当前内容
            st.write("### Current Food Items")
            st.write(st.session_state.edited_food_items or st.session_state.original_detection)

            # Recommendations section
            st.write("### Nutritional Analysis and PCOS Recommendations")
            if st.button("Provide Recommendation", key="provide_recommendation"):
                current_food_items = st.session_state.edited_food_items or st.session_state.original_detection
                try:
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

                    nutrition_response = get_gemini_response("Nutrition Analysis", image_content, nutrition_prompt)
                    nutritional_values = parse_nutritional_values(nutrition_response)

                    st.write("### Overall: ⭐⭐⭐⭐")
                    st.write("### Summary:")
                    st.write("Increase protein and fiber intake or undertake light exercise such as walks to reduce the sugar spike")

                    st.write("### Details:")
                    components.html(nutrition_bar_chart(nutritional_values), height=300, scrolling=True)

                    # 保存营养分析结果
                    st.session_state['nutritional_values'] = nutritional_values

                    pcos_prompt = textwrap.dedent(f"""
                    Act as a nutritionist specializing in managing PCOS (Polycystic Ovary Syndrome) and provide nutritional recommendations for the following dish:
                    {current_food_items}
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

                    # 保存 PCOS 建议
                    st.session_state['pcos_recommendations'] = pcos_response
                    
                    st.session_state['current_meal_rating'] = 4

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
                
                # 获取当前时间和用餐类型
                current_time = datetime.now()
                meal_type = get_meal_type(current_time)
                
                # 构建完整的餐点记录
                new_meal = {
                    "meal_type": meal_type,
                    "name": st.session_state.get('meal_name', 'Unknown Meal'),
                    "details": st.session_state.edited_food_items,
                    "time": current_time.strftime("%I:%M %p"),
                    "date": current_time.strftime("%Y-%m-%d"),
                    "rating": st.session_state.get('current_meal_rating', 0),
                    "image": image_bytes.getvalue(),
                    # 保存营养分析结果
                    "nutrition_analysis": {
                        "values": st.session_state.get('nutritional_values', {}),
                        "overall_rating": "⭐⭐⭐⭐",
                        "summary": "Increase protein and fiber intake or undertake light exercise such as walks to reduce the sugar spike"
                    },
                    # 保存 PCOS 建议
                    "pcos_recommendations": st.session_state.get('pcos_recommendations', "")
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