import streamlit as st
from PIL import Image
import io
from datetime import datetime
import streamlit.components.v1 as components

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

/* Meal log specific styles */
.meal-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}

/* Actions buttons */
.stButton > button {
    border: none !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    transition: transform 0.2s !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
}
</style>
"""

def navigation():
    cols = st.columns(3)
    with cols[0]:
        if st.button("👤\nProfile", use_container_width=True):
            st.switch_page("pages/1_Profile.py")
    with cols[1]:
        if st.button("🕒\nRecommendations", use_container_width=True):
            st.switch_page("app.py")
    with cols[2]:
        st.button("📝\nMeal Log", use_container_width=True, type="primary")

def nutrition_bar_chart(nutritional_values):
    """创建营养成分条形图"""
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

def create_meal_card(meal):
    """创建简洁的餐点卡片"""
    html = f"""
    <div style="
        background: white;
        margin: 10px 0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div style="flex: 1">
            <div style="color: #666; font-size: 0.9em;">{meal['meal_type']}</div>
            <div style="font-weight: bold; margin: 5px 0;">{meal['name']}</div>
            <div style="color: #888; font-size: 0.9em;">{meal['time']}</div>
            <div style="color: #FFD700; margin-top: 5px;">{"★" * meal['rating']}</div>
        </div>
    </div>
    """
    return html

def main():
    st.set_page_config(page_title="Meal Log", page_icon="🍽️", layout="wide")
    st.markdown(css, unsafe_allow_html=True)
    
    st.title("Meal Log")

    # Add Meal button in the top left
    col1, col2, col3 = st.columns([2,8,2])
    with col1:
        if st.button("+ Add Meal", use_container_width=True):
            st.switch_page("app.py")

    # Display meal log
    if 'meal_log' in st.session_state and st.session_state.meal_log:
        # 显示每个餐点卡片
        for index, meal in enumerate(reversed(st.session_state.meal_log)):
            # 创建两列布局
            col1, col2 = st.columns([7, 3])
            
            with col1:
                # 显示简洁的餐点信息
                st.markdown(create_meal_card(meal), unsafe_allow_html=True)
            
            with col2:
                # 显示图片
                try:
                    if isinstance(meal['image'], bytes):
                        image = Image.open(io.BytesIO(meal['image']))
                        st.image(image, use_column_width=True)
                except Exception as e:
                    st.info("No image available")

            # 使用 expander 显示详细信息，移除 key 参数
            with st.expander(f"Show Details for {meal['meal_type']}: {meal['name']}"):
                # 基本信息
                st.markdown(f"**Details:**")
                st.markdown(meal['details'])
                
                # 营养分析
                st.markdown("### Nutritional Analysis")
                st.markdown(f"**Overall Rating:** {meal['nutrition_analysis']['overall_rating']}")
                st.markdown("**Summary:**")
                st.markdown(meal['nutrition_analysis']['summary'])
                
                # 显示营养成分条形图
                if 'values' in meal['nutrition_analysis']:
                    st.components.v1.html(
                        nutrition_bar_chart(meal['nutrition_analysis']['values']), 
                        height=300, 
                        scrolling=True
                    )
                
                # PCOS 建议
                st.markdown("### PCOS Recommendations")
                st.markdown(meal['pcos_recommendations'])

                # 编辑和删除按钮
                col3, col4 = st.columns([1, 1])
                with col3:
                    if st.button("✏️ Edit", key=f"edit_meal_{index}"):
                        st.session_state.editing_meal = len(st.session_state.meal_log) - 1 - index
                        st.experimental_rerun()
                with col4:
                    if st.button("🗑️ Delete", key=f"delete_meal_{index}"):
                        if st.warning("Are you sure you want to delete this meal?",
                                  key=f"warning_{index}"):
                            st.session_state.meal_log.pop(len(st.session_state.meal_log) - 1 - index)
                            st.success("Meal deleted!")
                            st.experimental_rerun()

        # 编辑功能
        if 'editing_meal' in st.session_state:
            meal_index = st.session_state.editing_meal
            meal = st.session_state.meal_log[meal_index]
            
            st.markdown("---")  # 添加分隔线
            with st.container():
                st.subheader("✏️ Edit Meal")
                
                # 编辑表单
                new_details = st.text_area("Meal Description", 
                                         meal.get('details', ''), 
                                         height=100,
                                         key="edit_details")
                col1, col2 = st.columns(2)
                with col1:
                    new_time = st.text_input("Time", 
                                           meal.get('time', ''),
                                           key="edit_time")
                with col2:
                    new_rating = st.slider("Rating", 
                                         1, 5, 
                                         meal.get('rating', 3),
                                         key="edit_rating")
                
                col3, col4 = st.columns([1,1])
                with col3:
                    if st.button("💾 Save Changes", key="save_edit"):
                        meal['details'] = new_details
                        meal['time'] = new_time
                        meal['rating'] = new_rating
                        del st.session_state.editing_meal
                        st.success("Changes saved!")
                        st.experimental_rerun()
                with col4:
                    if st.button("❌ Cancel", key="cancel_edit"):
                        del st.session_state.editing_meal
                        st.experimental_rerun()

    else:
        st.info("🍽️ No meals logged yet. Add your first meal!")

    # Add navigation at the bottom
    navigation()

if __name__ == "__main__":
    main()