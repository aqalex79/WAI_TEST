import streamlit as st
import pandas as pd

# 统一的 CSS 样式
css = """
<style>
.stApp {
    max-width: 800px;
    margin: 0 auto;
    font-family: Arial, sans-serif;
    padding-bottom: 70px;
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

def navigation():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("👤 Profile", use_container_width=True, type="primary")
    with col2:
        if st.button("🕒 Recommendations", use_container_width=True):
            st.switch_page("app.py")
    with col3:
        if st.button("📝 Meal Log", use_container_width=True):
            st.switch_page("pages/3_Meal_Log.py")

def main():
    st.set_page_config(page_title="Profile", page_icon="👤", layout="wide")
    
    # 添加 CSS
    st.markdown(css, unsafe_allow_html=True)
    
    st.title("Profile")

    # Profile Header
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("## A")  # Avatar placeholder
    with col2:
        st.markdown("**Name:** Andrea Doe")
        st.markdown("**Age:** 28")
        st.markdown("**Weight:** 65 kg")
        st.markdown("**Height:** 170 cm")

    # Goals and Settings buttons
    col1, col2 = st.columns(2)
    with col1:
        st.button("Goals")
    with col2:
        st.button("Settings")

    # Nutri Score
    st.markdown("### Nutri Score")
    st.markdown("Based on your overview meal tracking, your score is **78** and considered good.")
    if st.button("Tell me more >"):
        st.markdown("This would show more information about the Nutri Score.")

    # Self Assessment
    st.markdown("### Self Assessment")
    st.markdown("Understand meal impact on conditions")

    assessment_data = {
        "Conditions": ["Brain Fog", "Constipation", "Seasonal Allergies", "Sweat Easily", 
                       "Acid Reflux", "Cravings for sweets", "Difficulty Falling asleep"],
        "Jan-10": ["✅", "✅", "❌", "❌", "❌", "✅", "✅"],
        "Apr-21": ["❌", "✅", "✅", "❌", "❌", "❌", "✅"]
    }
    df_assessment = pd.DataFrame(assessment_data)
    st.table(df_assessment)

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
    st.table(df_blood_work.iloc[:3])
    
    st.markdown("**MINERALS**")
    st.table(df_blood_work.iloc[3:])

    # Add navigation
    navigation()

if __name__ == "__main__":
    main()