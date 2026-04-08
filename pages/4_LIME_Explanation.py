import streamlit as st
import pandas as pd
from utils.styles import load_styles
from components.topbar import top_bar  

st.set_page_config(page_title="SHAP & LIME Explainability", layout="wide",page_icon="🏥")

load_styles()

@st.cache_data
def load_data():
    return pd.read_csv("data/patient_qol_cleaned.csv")

df = load_data()

top_bar("QoL Risk Prediction")

# --- SEARCH SECTION ---

col0, col1, col2 = st.columns([1,1,3])

with col0:
    st.markdown("### 🔍 Search")

with col1:
    search_type = st.selectbox(
        "Search by",
        ["Patient ID", "Patient Name"]
    )

with col2:
    search_value = st.text_input(
        "Enter search keyword",
        placeholder="Example: N0001 or Ali Ahmad"
    )

# --- FILTER LOGIC ---
filtered_df = df.copy()

if search_value:
    if search_type == "Patient ID":
        filtered_df = df[
            df["patient_id"].astype(str).str.contains(search_value, case=False, na=False)
        ]
    elif search_type == "Patient Name":
        filtered_df = df[
            df["name"].astype(str).str.contains(search_value, case=False, na=False)
        ]

# --- SHOW RESULTS ---
st.markdown("### Search Result")
st.dataframe(filtered_df, use_container_width=True)