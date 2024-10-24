import streamlit as st
import pandas as pd

# 使用与 app.py 相同的 CSS
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

/* Profile specific styles */
.profile-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.score-card {
    background: #E8F0FD;
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
}

/* Tables */
.stTable {
    border-radius: 10px;
    overflow: hidden;
}

/* Symptom and preference cards */
.info-card {
    background: #ffffff;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    margin: 10px 0;
}
</style>
"""

def navigation():
    cols = st.columns(3)
    with cols[0]:
        st.button("👤\nProfile", use_container_width=True, type="primary")
    with cols[1]:
        if st.button("🕒\nRecommendations", use_container_width=True):
            st.switch_page("app.py")
    with cols[2]:
        if st.button("📝\nMeal Log", use_container_width=True):
            st.switch_page("pages/3_Meal_Log.py")

def main():
    st.set_page_config(page_title="Profile", page_icon="👤", layout="wide")
    st.markdown(css, unsafe_allow_html=True)
    
    st.title("Profile")

    # Profile Header
    with st.container():
        st.markdown("""
        <div class="profile-card">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="font-size: 36px; width: 60px; height: 60px; 
                           background: #E8F0FD; border-radius: 30px; 
                           display: flex; align-items: center; justify-content: center;">
                    A
                </div>
                <div>
                    <div style="font-weight: bold;">Andrea Doe</div>
                    <div style="color: #666;">
                        Age: 28 • Weight: 65 kg • Height: 170 cm
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Top 3 Symptoms Section
    st.markdown("### Top 3 Symptoms")
    
    # Define all possible symptoms
    all_symptoms = [
        "Irregular Periods (Menstrual Irregularities)",
        "Weight Gain or Difficulty Losing Weight",
        "Acne and Oily Skin",
        "Excess Hair Growth (Hirsutism)",
        "Hair Loss (Alopecia)",
        "Fatigue",
        "Mood Swings and Anxiety",
        "Infertility or Trouble Conceiving"
    ]
    
    # Initialize session state for symptoms if not exists
    if 'selected_symptoms' not in st.session_state:
        st.session_state.selected_symptoms = all_symptoms[:3]  # Default to first three
    if 'show_symptoms_form' not in st.session_state:
        st.session_state.show_symptoms_form = False
        
    # Display current symptoms
    st.markdown("""
    <div class="info-card">
        <strong>Current Symptoms:</strong>
    </div>
    """, unsafe_allow_html=True)
    for symptom in st.session_state.selected_symptoms:
        st.markdown(f"• {symptom}")
        
    # Add button to modify symptoms
    if st.button("Modify Symptoms"):
        st.session_state.show_symptoms_form = True
        
    if st.session_state.show_symptoms_form:
        selected = st.multiselect(
            "Select 1-3 symptoms:",
            all_symptoms,
            default=st.session_state.selected_symptoms,
            max_selections=3
        )
        
        if st.button("Save Symptoms"):
            if 0 < len(selected) <= 3:
                st.session_state.selected_symptoms = selected
                st.session_state.show_symptoms_form = False
                st.success("Symptoms updated successfully!")
                st.rerun()
            else:
                st.error("Please select between 1 and 3 symptoms.")

    # Dietary Preference Section
    st.markdown("### Dietary Preference")
    
    # Define all dietary preferences
    dietary_preferences = [
        "Vegetarian",
        "Ketogenic (Keto)",
        "Gluten-Free",
        "Lactose-Free",
        "Halal",
        "Kosher",
        "Low-Carb",
        "Mediterranean",
        "Raw Foodism",
        "Flexitarian"
    ]
    
    # Initialize session state for dietary preference if not exists
    if 'dietary_preference' not in st.session_state:
        st.session_state.dietary_preference = dietary_preferences[0]  # Default to first option
    if 'show_preference_form' not in st.session_state:
        st.session_state.show_preference_form = False
        
    # Display current preference
    st.markdown("""
    <div class="info-card">
        <strong>Current Preference:</strong> {}
    </div>
    """.format(st.session_state.dietary_preference), unsafe_allow_html=True)
        
    # Add button to modify preference
    if st.button("Modify Dietary Preference"):
        st.session_state.show_preference_form = True
        
    if st.session_state.show_preference_form:
        selected_preference = st.selectbox(
            "Select your dietary preference:",
            dietary_preferences,
            index=dietary_preferences.index(st.session_state.dietary_preference)
        )
        
        if st.button("Save Preference"):
            st.session_state.dietary_preference = selected_preference
            st.session_state.show_preference_form = False
            st.success("Dietary preference updated successfully!")
            st.rerun()

    # Nutri Score
    st.markdown("### Nutri Score")
    st.markdown("""
    <div class="score-card">
        Based on your overview meal tracking, your score is <strong>78</strong> and considered good.
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Tell me more >"):
        st.info("This would show more information about the Nutri Score.")

    # Self Assessment
    st.markdown("### Self Assessment")
    st.markdown("Understand meal impact on conditions")

    assessment_data = {
        "Conditions": ["Brain Fog", "Constipation", "Seasonal Allergies", 
                      "Sweat Easily", "Acid Reflux", "Cravings for sweets", 
                      "Difficulty Falling asleep"],
        "Jan-10": ["✅", "✅", "❌", "❌", "❌", "✅", "✅"],
        "Apr-21": ["❌", "✅", "✅", "❌", "❌", "❌", "✅"]
    }
    st.dataframe(pd.DataFrame(assessment_data), use_container_width=True)

    # Blood Work
    st.markdown("### Blood Work")
    st.markdown("Uncover underlying conditions")

    blood_work_data = {
        "Test": ["Fasting Sugar", "Post Prandial Sugar", "HbA1c", "Zinc", "Selenium"],
        "Jan-10": ["89", "80", "5.9", "9", "--"],
        "Apr-21": ["89", "80", "5.9", "--", "--"]
    }
    df_blood_work = pd.DataFrame(blood_work_data)
    
    st.markdown("**SUGARS**")
    st.dataframe(df_blood_work.iloc[:3], use_container_width=True)
    
    st.markdown("**MINERALS**")
    st.dataframe(df_blood_work.iloc[3:], use_container_width=True)

    # Navigation at bottom
    navigation()

if __name__ == "__main__":
    main()