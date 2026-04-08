import pandas as pd
import streamlit as st
import shap

from utils.model_loader import (
    load_model,
    load_label_encoder,
    load_feature_columns,
)

@st.cache_data
def load_model_data():
    return pd.read_csv("data/model_ready_patients.csv", dtype={"patient_id": str})

##---------------------------------------------
## WHERE THE MAGIC OF MACHINE LEARNING HAPPENS - change threshold of model here
##---------------------------------------------


def get_prediction(patient_id, threshold=0.35):
    """
    Return prediction result for one patient_id using the saved Random Forest model.
    """

    model = load_model()
    label_encoder = load_label_encoder()
    feature_columns = load_feature_columns()
    model_df = load_model_data()

    patient_id = str(patient_id).strip()

    # find patient in model-ready csv
    model_match = model_df[
        model_df["patient_id"].astype(str).str.strip() == patient_id
    ]

    if model_match.empty:
        return None

    # remove patient_id before prediction
    model_patient_row = model_match.iloc[0].drop(labels=["patient_id"])

    # make into 1-row dataframe
    patient_input = pd.DataFrame([model_patient_row])

    # force exact training columns and order
    patient_input = patient_input.reindex(columns=feature_columns, fill_value=0)

    # predict probabilities
    probs = model.predict_proba(patient_input)[0]
    raw_classes = model.classes_

    # decode classes if model stores numeric labels
    try:
        class_labels = label_encoder.inverse_transform(raw_classes)
    except Exception:
        class_labels = raw_classes

    prob_dict = dict(zip(class_labels, probs))

    prob_decline = float(prob_dict.get("decline", 0.0))
    prob_no_decline = float(prob_dict.get("no_decline", 0.0))

    predicted_class = "Decline" if prob_decline >= threshold else "No Decline"
    
    # =========================================================
    # ADDED: SHAP EXPLAINABILITY PART
    # This computes SHAP values for this single patient row
    # This shows the top risk factors for card3 (Qol Prediction Page)
    # =========================================================
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(patient_input)

        # For binary classification:
        # shap_values may be:
        # 1. a list of 2 arrays -> [class_0_array, class_1_array]
        # 2. a single array depending on SHAP/version/model behavior
        #
        # We want the SHAP values for the "decline" class.
        if isinstance(shap_values, list):
            # Find the index of "decline" in class_labels
            decline_index = list(class_labels).index("decline")
            patient_shap_values = shap_values[decline_index][0]
        else:
            # fallback for newer SHAP formats
            patient_shap_values = shap_values[0]

        # Also keep the actual feature values for this patient
        patient_feature_values = patient_input.iloc[0].to_dict()

    except Exception as e:
        # fallback if SHAP fails for any reason
        patient_shap_values = None
        patient_feature_values = patient_input.iloc[0].to_dict()
    # =========================================================
    # END SHAP ADDITION
    # =========================================================


    return {
        "patient_id": patient_id,
        "predicted_class": predicted_class,
        "prob_decline": prob_decline,
        "prob_no_decline": prob_no_decline,
    
        # =====================================================
        # ADDED: return SHAP values + feature values
        # =====================================================
        "shap_values": patient_shap_values,
        "feature_values": patient_feature_values,
        "feature_names": feature_columns,
        # =====================================================
    }