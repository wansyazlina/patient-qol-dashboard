import streamlit as st
import pandas as pd
import joblib
from utils.styles import load_styles
from components.topbar import top_bar  
from utils.predict import get_prediction
from components.risk_tab import render_risk_prediction_tab
from components.explain_tab import render_explainability_tab
from utils.explain import build_local_shap_context
import shap
from utils.supabase_client import get_supabase_client


st.set_page_config(page_title="QoL Risk Prediction", layout="wide",page_icon="🏥")

load_styles()

supabase = get_supabase_client()

@st.cache_data(ttl=300)
def load_patients():
    response = supabase.table("patients").select("*").execute()
    return pd.DataFrame(response.data)

df = load_patients()

st.markdown(
    """
    <div style="
        background-color: #282413;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
    ">
        <h2 style="color:white; margin:0;"> 📌 QoL Risk Prediction</h2>
    </div>
    """,
    unsafe_allow_html=True
)


# -------------------------------
# SEARCH SECTION
# -------------------------------

st.markdown(
    "<h3 style='font-size:20px; font-weight:600;'>🔍 Search Patient</h3>",
    unsafe_allow_html=True
)

col1, col2 = st.columns([1, 2])

with col1:
    search_type = st.selectbox(
        "Search by",
        ["Patient ID", "Patient Name"]
    )

with col2:
    search_value = st.text_input(
        "Enter keyword",
        placeholder="Example: N0001 or Ali"
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


st.markdown("---")


# -------------------------------
# RESULT SECTION
# -------------------------------
if search_value:
    if filtered_df.empty:
        st.warning("No patient found.")
    else:
        st.success(f"Found {len(filtered_df)} patient(s).")

        # let user choose one
        if len(filtered_df) > 1:
            selected_patient_id = st.selectbox(
                "Select patient",
                filtered_df["patient_id"].astype(str).tolist()
            )
            patient_row = filtered_df[
                filtered_df["patient_id"].astype(str) == selected_patient_id
            ].iloc[0]
        else:
            patient_row = filtered_df.iloc[0]

        # get model prediction
        patient_id = str(patient_row["patient_id"]).strip()
        prediction_result = get_prediction(patient_id)


        # --- TABS ---
        tab1, tab2 = st.tabs(["📊 Risk Prediction", "🧠 Explainability (SHAP & LIME)"])

        with tab1:
            if prediction_result is None:
                st.error("Prediction data for this patient was not found.")
            else:
                render_risk_prediction_tab(patient_row, prediction_result)

        with tab2:
            if prediction_result is None:
                st.error("Prediction data for this patient was not found.")
            else:
                render_explainability_tab(patient_row, prediction_result)
        

else:
    st.info("Search for a patient by ID or name to view risk prediction and explainability.")