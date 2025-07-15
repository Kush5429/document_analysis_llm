import streamlit as st

# This file can be used to define reusable Streamlit UI components
# For this project's scope, the UI logic is primarily in app/main.py.
# However, for larger applications, you might define functions here like:

def display_section_header(title, icon=None):
    """Displays a consistent section header."""
    if icon:
        st.subheader(f"{icon} {title}")
    else:
        st.subheader(title)
    st.markdown("---")

def show_info_box(message):
    """Displays an informational message box."""
    st.info(message)

# Example of how to use in main.py:
# from app.ui_components import display_section_header
# display_section_header("Document Upload", "⬆️")
