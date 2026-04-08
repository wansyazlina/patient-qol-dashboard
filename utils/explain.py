import numpy as np
from utils.feature_info import load_feature_explanations
import shap
import pandas as pd
import matplotlib.pyplot as plt
        
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