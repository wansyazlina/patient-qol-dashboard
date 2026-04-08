import streamlit as st

def load_styles():
    st.markdown("""
          <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Space+Mono:wght@400;700&display=swap');

        /* Body text: target only text content areas */
        .stApp, .stMarkdown, .stText, .stCaption, p, li, label, input, textarea {
            font-family: 'Space Mono', monospace;
        }

        /* Headers only */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Space Grotesk', sans-serif;
        }

        /* Keep Material Symbols icons untouched */
        .material-symbols-rounded {
            font-family: 'Material Symbols Rounded' !important;
        }
            
        .stTextInput input, .stSelectbox div {
                font-family: 'Space Mono', monospace;}
        </style>
                
    """, unsafe_allow_html=True)