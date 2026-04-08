import numpy as np
from utils.feature_info import load_feature_explanations
import shap
import pandas as pd
import matplotlib.pyplot as plt
from components.clinical_interpretation import get_feature_value_dict
from utils.clinical_guidance import FEATURE_GUIDANCE
        
#------- Top 3 Risk Factor for patient row in cards 3 

def get_top_risk_factors(prediction_result, top_n=3, positive_only=True):
    shap_values = prediction_result.get("shap_values")
    feature_names = prediction_result.get("feature_names")
    feature_values = prediction_result.get("feature_values")

    if shap_values is None or feature_names is None:
        return []

    feature_info = load_feature_explanations()

    shap_values = np.array(shap_values)

    if shap_values.ndim == 1:
        patient_shap = shap_values

    elif shap_values.ndim == 2:
        if shap_values.shape[0] == 1:
            patient_shap = shap_values[0]
        elif shap_values.shape[1] == 2:
            patient_shap = shap_values[:, 0]
        else:
            print("Unexpected SHAP shape:", shap_values.shape)
            return []

    elif shap_values.ndim == 3:
        patient_shap = shap_values[0, :, 0]

    else:
        print("Unhandled SHAP shape:", shap_values.shape)
        return []

    factors = []
    for feature, shap_val in zip(feature_names, patient_shap):
        info = feature_info.get(feature, {})
        actual_value = feature_values.get(feature, None)

        factors.append({
            "feature": feature,
            "display_name": info.get("display_name", feature),
            "description": info.get("description", "No description available."),
            "clinical_note": info.get("clinical_note", ""),
            "shap_value": float(shap_val),
            "feature_value": actual_value
        })

    if positive_only:
        factors = [f for f in factors if f["shap_value"] > 0]

    factors = sorted(factors, key=lambda x: abs(x["shap_value"]), reverse=True)

    return factors[:top_n]


def get_shap_values_binary(explainer, X_data):
    shap_values = explainer.shap_values(X_data)

    if isinstance(shap_values, list):
        shap_decline = shap_values[0]
        shap_no_decline = shap_values[1]
    else:
        shap_decline = shap_values[:, :, 0]
        shap_no_decline = shap_values[:, :, 1]

    return shap_decline, shap_no_decline


def get_top_shap_factors(shap_values_row, feature_names, top_n=10):
    df = pd.DataFrame({
        "feature": feature_names,
        "value": shap_values_row
    })
    df["abs_value"] = df["value"].abs()
    df = df.sort_values("abs_value", ascending=False).head(top_n)
    return df[["feature", "value"]].to_dict(orient="records")

def get_top_shap_factors_2(prediction_result, top_n=3):
    shap_values = prediction_result.get("shap_values")
    feature_names = prediction_result.get("feature_names")
    feature_dict = get_feature_value_dict(prediction_result)

    if shap_values is None:
        return [], []

    shap_values = np.array(shap_values).flatten()

    rows = []
    for name, shap_val in zip(feature_names, shap_values):
        rows.append({
            "feature": name,
            "shap_value": float(shap_val),
            "feature_value": feature_dict.get(name)
        })

    decline_drivers = sorted(
        [r for r in rows if r["shap_value"] > 0],
        key=lambda x: x["shap_value"],
        reverse=True
    )[:top_n]

    protective_factors = sorted(
        [r for r in rows if r["shap_value"] < 0],
        key=lambda x: x["shap_value"]
    )[:top_n]

    return decline_drivers, protective_factors

def save_waterfall_plot(explainer, local_shap_values, patient_data_row, feature_names, output_path):
    base_value = explainer.expected_value
    if isinstance(base_value, (list, tuple)):
        base_value = base_value[0]

    explanation = shap.Explanation(
        values=local_shap_values,
        base_values=base_value,
        data=patient_data_row,
        feature_names=feature_names
    )

    plt.figure()
    shap.plots.waterfall(explanation, show=False)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    return output_path


def build_local_shap_context(explainer, X_data, patient_index, feature_names):
    shap_decline, shap_no_decline = get_shap_values_binary(explainer, X_data)

    local_shap = shap_decline[patient_index]
    patient_row_data = X_data.iloc[patient_index]

    top_factors = get_top_shap_factors(local_shap, feature_names, top_n=10)
    waterfall_plot_path = save_waterfall_plot(
        explainer=explainer,
        local_shap_values=local_shap,
        patient_data_row=patient_row_data,
        feature_names=feature_names,
        output_path="shap_waterfall.png"
    )

    return {
        "top_factors": top_factors,
        "waterfall_plot_path": waterfall_plot_path
    }
    


def interpret_feature_direction(feature_name, feature_value, shap_value):
    meta = FEATURE_GUIDANCE.get(feature_name, {})
    display_name = meta.get("display_name", feature_name)
    clinical_note = meta.get("clinical_note", "This feature contributed to the model prediction.")

    direction = "higher decline risk" if shap_value > 0 else "lower decline risk"

    # generic high/low logic
    recommendation = ""
    if feature_name == "adm_vas":
        # special case: low VAS is usually worse
        if feature_value is not None and float(feature_value) < 50:
            recommendation = meta.get("low_recommendation", "")
        else:
            recommendation = meta.get("high_recommendation", "")
    elif feature_name == "gender":
        recommendation = meta.get("high_recommendation", "")
    else:
        try:
            val = float(feature_value)
            if val >= 3:
                recommendation = meta.get("high_recommendation", "")
            else:
                recommendation = meta.get("low_recommendation", "")
        except Exception:
            recommendation = meta.get("low_recommendation", "")

    return {
        "display_name": display_name,
        "feature_name": feature_name,
        "feature_value": feature_value,
        "shap_value": shap_value,
        "direction": direction,
        "clinical_note": clinical_note,
        "recommendation": recommendation
    }
    
def build_clinical_interpretation(prediction_result, lime_exp=None, top_n=3):
    predicted_class = prediction_result.get("predicted_class", "Unknown")
    prob_decline = prediction_result.get("prob_decline", 0.0)
    prob_no_decline = prediction_result.get("prob_no_decline", 0.0)

    decline_drivers, protective_factors = get_top_shap_factors_2(prediction_result, top_n=top_n)

    decline_interpretations = [
        interpret_feature_direction(
            item["feature"],
            item["feature_value"],
            item["shap_value"]
        )
        for item in decline_drivers
    ]

    protective_interpretations = [
        interpret_feature_direction(
            item["feature"],
            item["feature_value"],
            item["shap_value"]
        )
        for item in protective_factors
    ]

    if predicted_class == "Decline":
        summary = (
            f"The model predicts this patient is at risk of QoL decline "
            f"(decline probability: {prob_decline:.1%}). "
            f"The strongest contributing factors were mainly related to the features pushing the prediction toward decline."
        )
    else:
        summary = (
            f"The model predicts this patient is more likely to remain in the no-decline group "
            f"(no-decline probability: {prob_no_decline:.1%}, decline probability: {prob_decline:.1%}). "
            f"Several protective factors helped push the prediction away from decline."
        )

    return {
        "summary": summary,
        "decline_factors": decline_interpretations,
        "protective_factors": protective_interpretations
    }
    
def extract_lime_rules(lime_exp, top_n=3):
    if lime_exp is None:
        return []

    try:
        rules = lime_exp.as_list()
        return rules[:top_n]
    except Exception:
        return []
    
