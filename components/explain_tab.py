import streamlit as st
from components.explain_components import render_explainability_header,render_shap_local_section,render_lime_section,render_clinical_interpretation_section

def render_explainability_tab(patient_row, prediction_result):
    st.subheader("Explainability")
    render_explainability_header(patient_row, prediction_result)
    render_shap_local_section(patient_row, prediction_result)
    render_lime_section()
    render_clinical_interpretation_section()