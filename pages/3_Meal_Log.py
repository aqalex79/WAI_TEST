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

/* Content scrolling */
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

.analysis-card {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}

.progress-bar {
    background-color: #f0f2f6;
    border-radius: 10px;
    height: 20px;
    width: 100%;
    margin: 5px 0;
}

.progress-bar-fill {
    background-color: #1f77b4;
    height: 100%;
    border-radius: 10px;
    transition: width 0.3s ease;
}

.suggestion-card {
    background: #ffffff;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    margin: 8px 0;
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

def create_meal_card(meal):
    """Create a clean meal card with basic info"""
    score_color = {
        'Promising': 'green',
        'Can Do Better': 'orange',
        'Needs Improvement': 'red'
    }.get(meal.get('pcos_analysis', {}).get('score', ''), 'gray')

    html = f"""
    <div class="meal-card">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <div style="color: #666; font-size: 0.9em;">{meal['meal_type']}</div>
                <div style="font-weight: bold; margin: 5px 0;">{meal['name']}</div>
                <div style="color: #888; font-size: 0.9em;">{meal['time']} • {meal['date']}</div>
            </div>
            <div>
                <span style="color: {score_color}; font-weight: bold;">
                    {meal.get('pcos_analysis', {}).get('score', 'Not Analyzed')}
                </span>
            </div>
        </div>
    </div>
    """
    return html

def create_focus_area_analysis(focus_areas):
    """Create focus area analysis visualization"""
    html = "<div class='analysis-card' style='padding: 10px; margin: 0;'>"
    # 确保按照固定顺序显示所有四个领域
    area_order = [
        'Hormonal Balance & Insulin Sensitivity',
        'Inflammation Control & Gut Health',
        'Energy & Mental Health',
        'Reproductive Health & Fertility'
    ]
    
    for area in area_order:
        data = focus_areas.get(area, {'score': 0, 'explanation': ''})
        score = data.get('score', 0)
        explanation = data.get('explanation', '')
        html += f"""
        <div style="margin-bottom: 6px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                <span style="font-weight: 500; font-size: 12px;">{area}</span>
                <span style="font-size: 12px;">{score}/5</span>
            </div>
            <div style="width: 100%; height: 6px; background-color: #e0e0e0; border-radius: 3px; overflow: hidden; margin: 2px 0;">
                <div style="width: {score*20}%; height: 100%; background-color: #1f77b4; border-radius: 3px;"></div>
            </div>
            <div style="font-size: 11px; color: #666; margin-top: 1px; line-height: 1.2;">
                {explanation}
            </div>
        </div>
        """
    html += "</div>"
    return html

def create_suggestions_section(suggestions):
    """Create suggestions section with cards"""
    html = """
    <div style="display: flex; flex-direction: column; gap: 8px;">
    """
    
    suggestions_data = [
        ('⚡ Quick Fix', suggestions.get('quick_fix', '')),
        ('🔄 Swap Out', suggestions.get('swap_out', '')),
        ('⭐ Pro Moves', suggestions.get('pro_moves', ''))
    ]
    
    for title, content in suggestions_data:
        html += f"""
        <div style="background: #ffffff; padding: 10px; border-radius: 8px; border: 1px solid #e0e0e0;">
            <div style="font-weight: bold; color: #1f77b4; margin-bottom: 4px;">
                {title}
            </div>
            <div style="font-size: 0.9em; color: #333; word-wrap: break-word; line-height: 1.4;">
                {content}
            </div>
        </div>
        """
    
    html += "</div>"
    return html

def nutrition_bar_chart(nutritional_values):
    """Create nutrition bar chart"""
    return f"""
    <div class="analysis-card" style="padding: 12px; margin: 0;">
        <div style="font-family: Arial, sans-serif;">
            {' '.join([f'''
            <div style="margin-bottom: 8px; width: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-size: 14px; font-weight: 500;">
                        {nutrient.capitalize()}
                    </span>
                    <span style="font-size: 14px;">
                        {value}%
                    </span>
                </div>
                <div style="width: 100%; height: 8px; background-color: #e0e0e0; border-radius: 4px; overflow: hidden;">
                    <div style="width: {value}%; height: 100%; background-color: {
                        {
                            'protein': '#4CAF50',
                            'fat': '#F44336',
                            'carbs': '#FFC107',
                            'fiber': '#2196F3'
                        }.get(nutrient, '#888')
                    };">
                    </div>
                </div>
            </div>
            ''' for nutrient, value in nutritional_values.items()])}
        </div>
    </div>
    """

def main():
    st.set_page_config(page_title="Meal Log", page_icon="🍽️", layout="wide")
    st.markdown(css, unsafe_allow_html=True)
    
    st.title("Meal Log")

    # Add Meal button
    col1, col2, col3 = st.columns([2,8,2])
    with col1:
        if st.button("+ Add Meal", use_container_width=True):
            st.switch_page("app.py")

    # Display meal log
    if 'meal_log' in st.session_state and st.session_state.meal_log:
        for index, meal in enumerate(reversed(st.session_state.meal_log)):
            # Create two-column layout
            col1, col2 = st.columns([7, 3])
            
            with col1:
                st.markdown(create_meal_card(meal), unsafe_allow_html=True)
            
            with col2:
                try:
                    if isinstance(meal['image'], bytes):
                        image = Image.open(io.BytesIO(meal['image']))
                        st.image(image, use_column_width=True)
                except Exception:
                    st.info("No image available")

            # Meal details expander
            with st.expander(f"Show Details"):
                # Basic information
                st.markdown(f"**Food Items:**")
                st.markdown(meal['details'])
                
                # Nutritional Analysis
                st.markdown("### Nutritional Analysis")
                if 'nutrition_analysis' in meal and 'values' in meal['nutrition_analysis']:
                    st.components.v1.html(
                        nutrition_bar_chart(meal['nutrition_analysis']['values']), 
                        height=180
                    )
                
                # PCOS Analysis
                st.markdown("### PCOS Analysis")
                if 'pcos_analysis' in meal:
                    # Focus Areas
                    st.markdown("#### Focus Areas")
                    st.components.v1.html(
                        create_focus_area_analysis(meal['pcos_analysis'].get('focus_areas', {})),
                        height=280
                    )
                    
                    # Suggestions
                    st.markdown("#### Recommendations")
                    st.components.v1.html(
                        create_suggestions_section(meal['pcos_analysis'].get('suggestions', {})),
                        height=300
                    )

                # Edit and Delete buttons
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

        # Editing functionality
        if 'editing_meal' in st.session_state:
            meal_index = st.session_state.editing_meal
            meal = st.session_state.meal_log[meal_index]
            
            st.markdown("---")
            with st.container():
                st.subheader("✏️ Edit Meal")
                
                # Edit form
                new_details = st.text_area(
                    "Meal Description", 
                    meal.get('details', ''), 
                    height=100,
                    key="edit_details"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    new_time = st.text_input(
                        "Time", 
                        meal.get('time', ''),
                        key="edit_time"
                    )
                
                # Save and Cancel buttons
                col3, col4 = st.columns([1,1])
                with col3:
                    if st.button("💾 Save Changes", key="save_edit"):
                        meal['details'] = new_details
                        meal['time'] = new_time
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