import streamlit as st
from components.explain_components import render_explainability_header,render_top_contributingrisks_section,render_clinical_interpretation_section,render_force_plot_section
from utils.predict import get_lime_explanation

def render_explainability_tab(patient_row, prediction_result):
    render_explainability_header(patient_row, prediction_result) #shows current selected patient (including risk) as header
    
    render_top_contributingrisks_section(patient_row,prediction_result)
    
   
    lime_exp = get_lime_explanation(prediction_result["patient_id"])
    render_clinical_interpretation_section(prediction_result, lime_exp)
    
    

    #NOTE: Force plot and shap_local section is currently disabled due to performance issues. It can be enabled by uncommenting the line below.
     #render_force_plot_section(prediction_result)
     #render_shap_local_section(patient_row, prediction_result) #top risks and waterfall plot
        