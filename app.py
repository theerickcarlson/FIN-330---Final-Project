import streamlit as st

st.set_page_config(
    page_title="Finance Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("FIN 330 - Final Project")

st.markdown("""
Created by: Erick Carlson, Philip Job, and Wyatt Paggen

Welcome! **Use the sidebar to navigate between pages**

### Pages:

- Individual Stock Analysis  
- Portfolio Performance Dashboard

""")

st.markdown("---")

st.info("Built using Python, Streamlit, and Yahoo Finance")
