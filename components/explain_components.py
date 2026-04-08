import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import shap
import numpy as np


def render_explainability_header(patient_row, prediction_result):
    patient_id = patient_row.get("patient_id", "N/A")
    age = patient_row.get("age", "N/A")
    mobility = patient_row.get("adm_mobility", "N/A")

    raw_pred = prediction_result.get("predicted_class", "N/A")
    prob_decline = float(prediction_result.get("prob_decline", 0.0))
    prob_no_decline = float(prediction_result.get("prob_no_decline", 0.0))

    pred_str = str(raw_pred).strip().lower().replace("_", " ")

    if pred_str in ["0", "decline"]:
        pred_label = "Decline"
        pred_color = "#e25b52"
        pred_bg = "#fbe7e5"
        confidence = prob_decline
        header_bg = "#f9dfdc"
        border_color = "#f0d8d5"
    elif pred_str in ["1", "no decline", "no_decline"]:
        pred_label = "No Decline"
        pred_color = "#2e8b57"
        pred_bg = "#eaf7ee"
        confidence = prob_no_decline
        header_bg = "#dff2e5"
        border_color = "#d2ead9"
    else:
        pred_label = str(raw_pred).replace("_", " ").title()
        pred_color = "#666666"
        pred_bg = "#f4f4f4"
        confidence = max(prob_decline, prob_no_decline)
        header_bg = "#ebebeb"
        border_color = "#dddddd"

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"""
        <div style="
            background:#eef4ff;
            border:1px solid #dbe4f3;
            border-radius:16px;
            overflow:hidden;
            box-shadow:0 1px 4px rgba(0,0,0,0.04);
            font-family:'Space Grotesk', sans-serif;
            min-height:150px;">
            <div style="
                background:#dfeafc;
                color:#4a78d1;
                padding:14px 18px;
                font-size:18px;
                font-weight:700;
                display:flex;
                align-items:center;
                gap:10px;">
                <span style="font-size:20px;">👤</span>
                <span>Patient</span>
            </div>
            <div style="display:flex;min-height:98px;">
                <div style="
                    flex:1;
                    padding:18px 22px;
                    border-right:1px solid #e2e8f0;
                    display:flex;
                    align-items:flex-start;
                    justify-content:flex-start;
                    font-size:18px;
                    color:#38507a;
                    font-weight:600;">
                    ID: {patient_id}
                </div>
                <div style="
                    flex:1;
                    padding:18px 22px;
                    display:flex;
                    flex-direction:column;
                    justify-content:flex-start;
                    gap:10px;
                    color:#4f5f7d;">
                    <div style="font-size:18px;">
                        Age: <span style="font-weight:700; font-size:20px; color:#3a4b6a;">{age}</span>
                    </div>
                    <div style="font-size:18px;">
                        Mobility Score: <span style="font-weight:700; font-size:20px; color:#3a4b6a;">{mobility}</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div style="
            background:{pred_bg};
            border:1px solid {border_color};
            border-radius:16px;
            overflow:hidden;
            box-shadow:0 1px 4px rgba(0,0,0,0.04);
            font-family:'Space Grotesk', sans-serif;
            min-height:150px;
        ">
            <div style="
                background:{header_bg};
                color:{pred_color};
                padding:14px 18px;
                font-size:18px;
                font-weight:700;
                display:flex;
                align-items:center;
                gap:8px;
            ">
                <span style="font-size:20px;">🎯</span>
                <span>Prediction Result</span>
            </div>
            <div style="
                padding:18px 22px;
                color:#4f5f7d;
                display:flex;
                flex-direction:column;
                gap:14px;
            ">
                <div style="font-size:18px;">
                    Predicted:
                    <span style="
                        color:{pred_color};
                        font-size:18px;
                        font-weight:800;
                        margin-left:8px;
                    ">
                        {pred_label}
                    </span>
                </div>
                <div style="font-size:18px;">
                    Confidence:
                    <span style="
                        font-family:'Space Mono', monospace;
                        font-weight:700;
                        font-size:20px;
                        color:#3a4b6a;
                        margin-left:8px;
                    ">
                        {confidence:.0%}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)



def render_shap_local_section(patient_row, prediction_result):
    shap_values = prediction_result.get("shap_values", None)
    feature_values = prediction_result.get("feature_values", {})
    feature_names = prediction_result.get("feature_names", [])

    if shap_values is None or len(feature_names) == 0:
        st.warning("SHAP explanation could not be generated for this patient.")
        return
    
    shap_values = np.array(shap_values)

    # 🔥 FORCE into 1D correctly
    if shap_values.ndim == 3:
        # (1, n_features, n_classes)
        shap_values = shap_values[0, :, 0]

    elif shap_values.ndim == 2:
        # (1, n_features) OR (n_features, n_classes)
        if shap_values.shape[0] == 1:
            shap_values = shap_values[0]   # (n_features,)
        else:
            shap_values = shap_values[:, 0]  # pick class 0

    # ensure final shape
    shap_values = shap_values.flatten()

    # -----------------------------
    # Build dataframe for top factors
    # -----------------------------
    shap_df = pd.DataFrame({
        "feature": feature_names,
        "shap_value": shap_values
    })

    shap_df["abs_value"] = shap_df["shap_value"].abs()
    shap_df = shap_df.sort_values("abs_value", ascending=False).head(10).copy()

    # prettier display names
    feature_label_map = {
        "adm_mobility": "Mobility Score",
        "adm_personal_care": "Personal Care",
        "adm_normal_activity": "Normal Activity",
        "adm_pain_uncomfort": "Pain Level",
        "adm_anxiety_depress": "Anxiety Score",
        "adm_vas": "Admission VAS",
        "age": "Age",
        "gender_0": "Male",
        "gender_1": "Female",
        "ethnicity_malay": "Malay",
        "ethnicity_chinese": "Chinese",
        "ethnicity_indian": "Indian",
    }

    shap_df["display_feature"] = shap_df["feature"].map(
        lambda x: feature_label_map.get(x, str(x).replace("_", " ").title())
    )

    # -----------------------------
    # Section header
    # -----------------------------
    st.markdown("""
    <div style="
        background:#eef3fb;
        border:1px solid #dbe4f3;
        border-radius:16px;
        overflow:hidden;
        margin-top:18px;
        font-family:'Space Grotesk', sans-serif;
    ">
        <div style="
            background:#7ea6e6;
            color:white;
            padding:14px 18px;
            font-size:18px;
            font-weight:700;
            display:flex;
            align-items:center;
            gap:10px;
        ">
            <span style="font-size:18px;">🧠</span>
            <span>Patient Risk Explanation</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    # -----------------------------
    # LEFT CARD: Top Factors
    # -----------------------------
    with c1:
        max_abs = shap_df["abs_value"].max() if not shap_df.empty else 1.0
        bars_html = ""

        for _, row in shap_df.iterrows():
            feature = row["display_feature"]
            value = float(row["shap_value"])

            bar_width = (abs(value) / max_abs) * 78 if max_abs > 0 else 0
            bar_color = "#e25555" if value >= 0 else "#74a84a"
            value_color = "#e25555" if value >= 0 else "#5c9441"
            sign = "+" if value > 0 else ""

            bars_html += f"""
            <div style="
                display:grid;
                grid-template-columns: 160px 1fr 80px;
                align-items:center;
                gap:12px;
                margin-bottom:14px;">
                <div style="
                    font-size:14px;
                    color:#4a5670;
                    font-weight:600;
                    white-space:nowrap;
                    overflow:hidden;
                    text-overflow:ellipsis;">
                    {feature}
                </div>
                <div style="
                    width:100%;
                    height:22px;
                    background:#f4f4f4;
                    border-radius:0px;
                    overflow:hidden;">
                    <div style="
                        width:{bar_width}%;
                        height:100%;
                        background:{bar_color};
                    "></div>
                </div>
                <div style="
                    font-family:'Space Mono', monospace;
                    font-size:14px;
                    font-weight:700;
                    color:{value_color};">
                    {sign}{value:.2f}
                </div>
            </div>
            """
        st.markdown(f"""
        <div style="
            background:white;
            border:1px solid #d9e1ef;
            border-radius:14px;
            padding:18px;
            min-height:390px;
            box-shadow:0 1px 4px rgba(0,0,0,0.04);
            font-family:'Space Grotesk', sans-serif;">
            <div style="
                font-size:18px;
                font-weight:700;
                color:#415c96;
                margin-bottom:10px;">
                Top Factors Impacting Risk
            </div>
            <div style="
                height:1px;
                background:#e7ebf3;
                margin-bottom:18px;"></div>
            {bars_html}
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------
    # RIGHT CARD: SHAP Waterfall Plot
    # -----------------------------
    with c2:
        st.markdown("""
        <div style="
            background:white;
            border:1px solid #d9e1ef;
            border-radius:14px;
            padding:18px;
            min-height:390px;
            box-shadow:0 1px 4px rgba(0,0,0,0.04);
            font-family:'Space Grotesk', sans-serif;
            margin-bottom:12px;">
            <div style="
                font-size:18px;
                font-weight:700;
                color:#415c96;
                margin-bottom:10px;">
                SHAP Waterfall Plot
            </div>
            <div style="
                height:1px;
                background:#e7ebf3;
                margin-bottom:18px;"></div>
        </div>
        """, unsafe_allow_html=True)

        try:
            # create Explanation object for a single patient
            values = shap_values
            base_value = 0.0
            data_values = [feature_values.get(col, 0) for col in feature_names]

            explanation = shap.Explanation(
                values=values,
                base_values=base_value,
                data=data_values,
                feature_names=feature_names
            )

            fig, ax = plt.subplots(figsize=(8, 4.8))
            shap.plots.waterfall(explanation, max_display=10, show=False)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        except Exception as e:
            st.warning("Unable to render SHAP waterfall plot.")


def render_lime_section():
    st.markdown("""
    <h3 style="font-family:'Space Grotesk', sans-serif; margin-bottom:10px;">
        LIME Explanation
    </h3>
    """, unsafe_allow_html=True)

    st.info("Place your LIME explanation output here.")


def render_clinical_interpretation_section():
    st.markdown("""
    <h3 style="font-family:'Space Grotesk', sans-serif; margin-bottom:10px;">
        Clinical Interpretation
    </h3>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background:white;
        border-radius:14px;
        padding:18px;
        font-family:'Space Grotesk', sans-serif;
        border:1px solid #ececec;
        color:#4f5f7d;
    ">
        Add a concise interpretation of the SHAP and LIME results here for clinicians.
    </div>
    """, unsafe_allow_html=True)
