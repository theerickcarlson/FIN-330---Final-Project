import streamlit as st

st.set_page_config(
    page_title="FIN 330 - Final Project",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
Welcome to the **FIN 330 Final Project Dashboard**

### Pages

📈 Individual Stock Analysis  
Portfolio Performance Dashboard

Use the sidebar to navigate between pages.
""")

st.markdown("---")

st.info("Built using Python, Streamlit, and Yahoo Finance")
