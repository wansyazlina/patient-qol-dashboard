import streamlit as st
from components.explain_components import render_explainability_header,render_shap_local_section,render_clinical_interpretation_section,render_force_plot_section
from utils.predict import get_lime_explanation

def render_explainability_tab(patient_row, prediction_result):
    st.subheader("Explainability")
    render_explainability_header(patient_row, prediction_result)
    render_shap_local_section(patient_row, prediction_result)
    render_force_plot_section(prediction_result)
    
    lime_exp = get_lime_explanation(prediction_result["patient_id"])
   
    render_clinical_interpretation_section(prediction_result, lime_exp)