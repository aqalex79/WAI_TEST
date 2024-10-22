import streamlit as st
from PIL import Image
import io
from datetime import datetime

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
        if st.button("👤 Profile", use_container_width=True):
            st.switch_page("pages/1_Profile.py")
    with col2:
        if st.button("🕒 Recommendations", use_container_width=True):
            st.switch_page("app.py")
    with col3:
        st.button("📝 Meal Log", use_container_width=True, type="primary")

def main():
    st.set_page_config(page_title="Meal Log", page_icon="🍽️", layout="wide")
    
    # 添加 CSS
    st.markdown(css, unsafe_allow_html=True)
    
    st.title("Meal Log")

    # Add Meal button
    if st.button("+ Add Meal", key="add_meal", help="Add a new meal to the log"):
        st.switch_page("app.py")  # This will redirect to the main page for meal recommendations

    # Display meal log
    if 'meal_log' in st.session_state and st.session_state.meal_log:
        for index, meal in enumerate(reversed(st.session_state.meal_log)):
            with st.expander(f"Meal: {meal['name']} - {meal['time']}", expanded=index == 0):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(meal['name'])
                    st.write(f"Time: {meal['time']}")
                    st.write("Rating: " + "⭐" * meal['rating'])
                with col2:
                    try:
                        if isinstance(meal['image'], bytes):
                            image = Image.open(io.BytesIO(meal['image']))
                            st.image(image, width=100)
                        else:
                            st.write("Image not available")
                    except Exception as e:
                        st.error(f"Error displaying image: {str(e)}")
                
                col3, col4 = st.columns([1, 1])
                with col3:
                    if st.button("Edit", key=f"edit_{index}"):
                        st.session_state.editing_meal = index
                        st.experimental_rerun()
                with col4:
                    if st.button("Delete", key=f"delete_{index}"):
                        st.session_state.meal_log.pop(len(st.session_state.meal_log) - 1 - index)
                        st.success("Meal deleted successfully!")
                        st.experimental_rerun()

        # Edit meal functionality
        if 'editing_meal' in st.session_state:
            edit_index = st.session_state.editing_meal
            meal = st.session_state.meal_log[len(st.session_state.meal_log) - 1 - edit_index]
            
            st.subheader("Edit Meal")
            new_name = st.text_input("Meal Name", meal['name'])
            new_time = st.text_input("Time", meal['time'])
            new_rating = st.slider("Rating", 1, 5, meal['rating'])
            
            col5, col6 = st.columns([1, 1])
            with col5:
                if st.button("Save Changes"):
                    meal['name'] = new_name
                    meal['time'] = new_time
                    meal['rating'] = new_rating
                    del st.session_state.editing_meal
                    st.success("Meal updated successfully!")
                    st.experimental_rerun()
            with col6:
                if st.button("Cancel"):
                    del st.session_state.editing_meal
                    st.experimental_rerun()

    else:
        st.info("No meals logged yet. Add a meal to get started!")

    # Add some statistics or summaries
    if 'meal_log' in st.session_state and st.session_state.meal_log:
        st.subheader("Meal Log Summary")
        total_meals = len(st.session_state.meal_log)
        average_rating = sum(meal['rating'] for meal in st.session_state.meal_log) / total_meals
        
        col7, col8 = st.columns(2)
        with col7:
            st.metric("Total Meals", total_meals)
        with col8:
            st.metric("Average Rating", f"{average_rating:.2f} ⭐")

    # Add an option to clear the entire log
    if st.button("Clear Entire Log", help="This will delete all logged meals"):
        if 'meal_log' in st.session_state:
            if st.warning("Are you sure you want to clear all meal logs?"):
                st.session_state.meal_log = []
                st.success("Meal log cleared successfully!")
                st.experimental_rerun()

    # Add navigation
    navigation()

if __name__ == "__main__":
    main()