import streamlit as st
from components.risk_components import render_prediction_cards,render_clinical_info_table,render_patient_summary_cards,render_actual_outcome_match_cards


def render_risk_prediction_tab(patient_row, prediction_result):
    st.subheader("Risk Prediction")
    render_patient_summary_cards(patient_row, prediction_result)
    render_prediction_cards(prediction_result)
    render_actual_outcome_match_cards(patient_row, prediction_result)
    render_clinical_info_table(patient_row)