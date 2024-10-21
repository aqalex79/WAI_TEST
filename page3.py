import streamlit as st
from PIL import Image
import io

def main():
    st.set_page_config(page_title="Meal Log", page_icon="🍽️", layout="wide")
    
    # Custom CSS
    st.markdown("""
    <style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
        font-family: Arial, sans-serif;
    }
    .meal-item {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding: 10px;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    .meal-info {
        flex: 1;
    }
    .meal-image {
        width: 100px;
        height: 100px;
        object-fit: cover;
        border-radius: 10px;
        margin-left: 20px;
    }
    .star-rating {
        color: #FFD700;
    }
    .add-meal-btn {
        background-color: #a8d8bf !important;
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

    st.title("Meal Log")

    if st.button("+ Add Meal", key="add_meal", help="Add a new meal to the log"):
        st.write("Redirecting to meal recommendation page...")
        st.markdown("[Go to Meal Recommendation](app5)")  # 使用相对路径

    # Display meal log
    if 'meal_log' in st.session_state:
        for meal in reversed(st.session_state.meal_log):  # 倒序显示，最新的在最上面
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(meal['name'])
                    st.write(meal['time'])
                    st.write("⭐" * meal['rating'])
                with col2:
                    if isinstance(meal['image'], (str, bytes, io.BytesIO)):
                        st.image(meal['image'], width=100)
                    else:
                        # 如果image是UploadedFile对象
                        image = Image.open(meal['image'])
                        st.image(image, width=100)
    else:
        st.write("No meals logged yet. Add a meal to get started!")

    # Footer navigation
    footer_html = """
    <div class="footer-nav">
        <a href="page1">
            <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMCAyMXYtMmE0IDQgMCAwIDAtNC00SDhhNCA0IDAgMCAwLTQgNHYyIiAvPjxjaXJjbGUgY3g9IjEyIiBjeT0iNyIgcj0iNCI+PC9jaXJjbGU+PC9zdmc+" alt="Profile">
            <span>Profile</span>
        </a>
        <a href="app5">
            <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIj48L2NpcmNsZT48cG9seWxpbmUgcG9pbnRzPSIxMiA2IDEyIDEyIDE2IDE0Ij48L3BvbHlsaW5lPjwvc3ZnPg==" alt="Meal Recommendations">
            <span>Meal Recommendations</span>
        </a>
        <a href="#" class="active">
            <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xNCAySDZhMiAyIDAgMCAwLTIgMnYxNmEyIDIgMCAwIDAgMiAyaDEyYTIgMiAwIDAgMCAyLTJWOHoiIC8+PHBvbHlsaW5lIHBvaW50cz0iMTQgMiAxNCA4IDIwIDgiPjwvcG9seWxpbmU+PGxpbmUgeDE9IjE2IiB5MT0iMTMiIHgyPSI4IiB5Mj0iMTMiPjwvbGluZT48bGluZSB4MT0iMTYiIHkxPSIxNyIgeDI9IjgiIHkyPSIxNyI+PC9saW5lPjxwb2x5bGluZSBwb2ludHM9IjEwIDkgOSA5IDggOSI+PC9wb2x5bGluZT48L3N2Zz4=" alt="Meal Log">
            <span>Meal Log</span>
        </a>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()