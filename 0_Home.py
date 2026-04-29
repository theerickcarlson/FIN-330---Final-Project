# ==============================
# Import Library
# ==============================

import streamlit as st  # Streamlit is used to build the web app interface

# ==============================
# Page Configuration
# ==============================

# Sets up the layout and appearance of the app
st.set_page_config(
    page_title="Finance Dashboard",      # Title shown in browser tab
    page_icon="📈",                     # Icon shown in browser tab
    layout="wide",                      # Uses full screen width for layout
    initial_sidebar_state="expanded"    # Sidebar is open by default
)

# ==============================
# Main Title
# ==============================

# Displays the main title at the top of the page
st.title("FIN 330 - Final Project")

# ==============================
# Project Description Section
# ==============================

# Markdown allows formatted text (headings, bold, lists)
st.markdown("""
### Created by: Erick Carlson, Philip Job, and Wyatt Paggen

#### Welcome! **Use the sidebar to navigate between pages**

- Individual Stock Analysis  
- Portfolio Performance Dashboard

""")

# ==============================
# Divider Line
# ==============================

# Adds a horizontal line for visual separation
st.markdown("---")

# ==============================
# Footer / Info Section
# ==============================

# Displays an informational message box about the tools used
st.info("Built using Python, Streamlit, and Yahoo Finance")
