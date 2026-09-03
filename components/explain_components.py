import os
from unittest import result
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import shap
import json
from pathlib import Path
import numpy as np
from utils.image_utils import get_icon_base64, FEATURE_ICONS
from utils.explain import (build_rag_clinical_interpretation)

def load_feature_explanations():

    path = Path("assets/feature_explanations.json")

    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
    
FEATURE_EXPLANATIONS = load_feature_explanations()

def render_explainability_header(patient_row, prediction_result):
    # =====================================================
    # PATIENT INFORMATION
    # =====================================================

    patient_name = str(
        patient_row.get(
            "name",
            "Unknown Patient"
        )
    ).strip()

    patient_id = str(
        patient_row.get(
            "patient_id",
            "N/A"
        )
    ).strip()

    # =====================================================
    # PREDICTION INFORMATION
    # =====================================================

    prob_decline = float(
        prediction_result.get(
            "prob_decline",
            0
        )
    )

    risk_percent = prob_decline * 100

    risk_level = prediction_result.get(
        "risk_level",
        "Unknown Risk"
    )


    # =====================================================
    # RISK CLASS
    # =====================================================

    risk_level_lower = str(
        risk_level
    ).lower()

    if "high" in risk_level_lower:

        risk_class = "current-risk-high"
        risk_icon = "⚠"

    elif "moderate" in risk_level_lower:

        risk_class = "current-risk-moderate"
        risk_icon = "!"

    else:

        risk_class = "current-risk-low"
        risk_icon = "✓"


    # =====================================================
    # PATIENT PLACEHOLDER IMAGE
    # Change this path to your actual image
    # =====================================================

    image_src = get_icon_base64(
        "assets/patient_placeholder.png"
    )


    if image_src:

        avatar_html = f"""<img
                src="{image_src}"
                class="current-patient-avatar"
                alt="Patient profile placeholder">"""

    else:

        # fallback if image is missing
        avatar_html = """<div class="current-patient-avatar-fallback">
                👤
            </div>"""


    # =====================================================
    # HEADER
    # =====================================================

    st.markdown(
        f"""<div class="explain-current-patient-card">
            <!-- LEFT SIDE -->
            <div class="explain-patient-info">
                <div class="explain-patient-avatar-wrapper">
                    {avatar_html}
                </div>
                <div class="explain-patient-text">
                    <div class="explain-patient-main-line">
                        <span class="explain-patient-label">
                            Current patient:
                        </span>
                        <span class="explain-patient-name">
                            {patient_name}
                        </span>
                    </div>
                    <div class="explain-patient-id">
                        Patient ID: {patient_id}
                    </div>
                </div>
            </div>
            <!-- RIGHT SIDE -->
            <div class="current-risk-badge {risk_class}">
                <div class="current-risk-icon">
                    {risk_icon}
                </div>
                <div class="current-risk-text">
                    {risk_level}: {risk_percent:.0f}%
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True)
    
def render_top_contributingrisks_section(patient_row,prediction_result):

    # =====================================================
    # GET PATIENT-LEVEL SHAP DATA
    # =====================================================

    shap_values = prediction_result.get(
        "shap_values",
        None
    )

    feature_values = prediction_result.get(
        "feature_values",
        {}
    )

    feature_names = prediction_result.get(
        "feature_names",
        []
    )

    # =====================================================
    # VALIDATE SHAP DATA
    # =====================================================

    if shap_values is None or len(feature_names) == 0:

        st.warning(
            "SHAP explanation could not be generated "
            "for this patient."
        )

        return


    shap_values = np.array(
        shap_values
    ).flatten()


    if len(shap_values) != len(feature_names):

        st.warning(
            "SHAP values and feature names do not match."
        )

        return


    # =====================================================
    # BUILD CLEAN FACTOR LIST
    # =====================================================

    clean_factors = []


    for index, feature_name in enumerate(feature_names):

        shap_value = float(
            shap_values[index]
        )


        # ---------------------------------------------
        # GET FEATURE VALUE
        # ---------------------------------------------

        if isinstance(feature_values, dict):

            feature_value = feature_values.get(
                feature_name,
                "N/A"
            )

        elif isinstance(
            feature_values,
            (list, tuple, np.ndarray)
        ):

            if index < len(feature_values):
                feature_value = feature_values[index]

            else:
                feature_value = "N/A"

        else:

            feature_value = "N/A"


        # ---------------------------------------------
        # DISPLAY NAME + DESCRIPTION
        # ---------------------------------------------

        feature_info = FEATURE_EXPLANATIONS.get(
            feature_name,
            {}
        )

        display_name = feature_info.get(
            "display_name",
            str(feature_name)
            .replace("adm_", "")
            .replace("_", " ")
            .title()
        )

        description = feature_info.get(
            "description",
            "This feature influenced the patient's predicted QoL risk."
        )

        clinical_note = feature_info.get(
            "clinical_note",
            ""
        )

        # ---------------------------------------------
        # ADD TO FACTOR LIST
        # ---------------------------------------------

        clean_factors.append(
            {
                "feature": feature_name,
                "display_name": display_name,
                "feature_value": feature_value,
                "description": description,
                "shap_value": shap_value,
            }
        )

    # =====================================================
    # SPLIT POSITIVE / NEGATIVE SHAP CONTRIBUTIONS
    # =====================================================
    increasing_factors = sorted(
        [
            factor
            for factor in clean_factors
            if factor["shap_value"] > 0
        ],
        key=lambda x: x["shap_value"],
        reverse=True
    )[:4]


    protective_factors = sorted(
        [
            factor
            for factor in clean_factors
            if factor["shap_value"] < 0
        ],
        key=lambda x: abs(x["shap_value"]),
        reverse=True
    )[:4]

    # =====================================================
    # FIND MAXIMUM ABSOLUTE SHAP FOR BAR SCALING
    # =====================================================

    all_visible_factors = (
        increasing_factors
        + protective_factors)

    max_abs_shap = max(
        (
            abs(f["shap_value"])
            for f in all_visible_factors
        ),
        default=1)

    # =====================================================
    # HELPER: BUILD EACH FACTOR ROW
    # =====================================================

    def build_factor_rows(
        factor_list,
        direction
    ):

        rows_html = ""
        if not factor_list:

            return """<div class="explain-factor-empty">
                    No contributing factors available.
                </div>"""


        for factor in factor_list:

            feature_name = factor["feature"]
            display_name = factor["display_name"]
            feature_value = factor["feature_value"]
            description = factor["description"]
            shap_value = factor["shap_value"]

            # ---------------------------------------------
            # ICON
            # ---------------------------------------------

            icon_path = FEATURE_ICONS.get(
                feature_name
            )

            icon_src = (
                get_icon_base64(icon_path)
                if icon_path
                else None
            )


            if icon_src:

                icon_html = f"""<img
                        src="{icon_src}"
                        class="explain-factor-icon"
                        alt="{display_name}">"""
            else:

                icon_html = """<div class="explain-factor-icon-fallback">
                        ?
                    </div>"""

            # ---------------------------------------------
            # BAR WIDTH
            # ---------------------------------------------

            if max_abs_shap > 0:

                bar_width = max(8,int(abs(shap_value)/ max_abs_shap* 100))

            else:
                bar_width = 8

            # ---------------------------------------------
            # SIGNED SHAP VALUE
            # ---------------------------------------------

            signed_shap = (
                f"+{shap_value:.2f}"
                if shap_value > 0
                else f"{shap_value:.2f}"
            )


            rows_html += f"""<div class="explain-factor-row">
                    <div
                        class="explain-factor-icon-wrapper
                        {direction}-icon">
                        {icon_html}
                    </div>
                    <div class="explain-factor-name-section">
                        <div class="explain-factor-name">
                            {display_name}
                        </div>
                        <div class="explain-factor-patient-value">
                            Value: {feature_value}
                        </div>
                    </div>
                    <div
                        class="explain-factor-shap
                        {direction}-value">
                        {signed_shap}
                    </div>
                    <div class="explain-factor-bar">
                        <div class="
                                explain-factor-bar-fill
                                {direction}-bar"
                            style="width:{bar_width}%;">
                        </div>
                    </div>
                    <div class="explain-factor-description">
                        {description}
                    </div>
                </div>"""

        return rows_html

    # =====================================================
    # CREATE HTML
    # =====================================================

    increasing_html = build_factor_rows(
        increasing_factors,
        "increasing"
    )

    protective_html = build_factor_rows(
        protective_factors,
        "protective"
    )

    # =====================================================
    # SECTION TITLE
    # =====================================================

    st.markdown("""<div class="explainability-section-heading">
            <div class="explainability-section-title">
                Clinical Risk Interpretation
            </div>
            <div class="explainability-section-subtitle">
                Patient-specific factors influencing
                the predicted Quality of Life decline risk.
            </div>
        </div>""",
        unsafe_allow_html=True
    )


    # =====================================================
    # RENDER BOTH CARDS
    # =====================================================

    col1, col2 = st.columns(
        2,
        gap="medium"
    )

    # -----------------------------------------------------
    # CARD 1 — INCREASING RISK
    # -----------------------------------------------------

    with col1:

        st.markdown(
            f"""<div class="
                explain-contributor-card
                increasing-risk-card">
                <div class="
                    explain-contributor-header
                    increasing-risk-header">
                    <div class="explain-header-symbol">
                        ↗
                    </div>
                    <div>
                        Factors Increasing Risk
                    </div>
                </div>
                <div class="explain-factor-list">
                    {increasing_html}
                </div>
                <div class="explain-factor-footer">
                    <span>
                        Positive values increase
                        predicted decline risk
                    </span>
                    <span class="explain-info-icon">
                        ⓘ
                    </span>
                </div>
            </div>""",unsafe_allow_html=True)


    # -----------------------------------------------------
    # CARD 2 — PROTECTIVE FACTORS
    # -----------------------------------------------------

    with col2:

        st.markdown(
            f"""<div class="
                explain-contributor-card
                protective-risk-card">
                <div class="
                    explain-contributor-header
                    protective-risk-header">
                    <div class="explain-header-symbol">
                        ♢
                    </div>
                    <div>
                        Protective / Risk Reducing Factors
                    </div>
                </div>
                <div class="explain-factor-list">
                    {protective_html}
                </div>
                <div class="explain-factor-footer">
                    <span>
                        Negative values reduce
                        predicted decline risk
                    </span>
                    <span class="explain-info-icon">
                        ⓘ
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True)
        
    return {
        "increasing": increasing_factors,
        "protective": protective_factors}
       

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
            bars_html += f""" <div style="
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
                        background:{bar_color};"></div>
                </div>
                <div style="
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
            box-shadow:0 1px 4px rgba(0,0,0,0.04);">
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
        
            st.markdown(f"""
            <div style="
                background:white;
                border:1px solid #d9e1ef;
                border-radius:14px;
                padding:18px;
                box-shadow:0 1px 4px rgba(0,0,0,0.04);">
                <div style="
                    font-size:18px;
                    font-weight:700;
                    color:#415c96;">
                    SHAP Waterfall Plot
                </div>
            """, unsafe_allow_html=True)

            # ---- SHAP PLOT ----
            explanation = shap.Explanation(
                values=shap_values,
                base_values=0.0,
                data=[feature_values.get(col, 0) for col in feature_names],
                feature_names=feature_names
            )

            fig, ax = plt.subplots(figsize=(8, 4.8))
            shap.plots.waterfall(explanation, max_display=10, show=False)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.markdown('</div>', unsafe_allow_html=True)

        

def render_force_plot_section(prediction_result):
    st.markdown("### SHAP Force Plot")
    st.caption("This plot shows which features pushed the prediction toward higher or lower decline risk.")
    try:
        expected_value = prediction_result["expected_value"]
        shap_values = prediction_result["shap_values"]
        feature_values = prediction_result["feature_values"]
        feature_names = prediction_result["feature_names"]

        # Convert feature values into a pandas Series so labels appear nicely
        features = pd.Series(feature_values, index=feature_names)

        plt.figure(figsize=(12, 3))
        shap.force_plot(
            expected_value,
            shap_values,
            features,
            matplotlib=True,
            show=False
        )

        fig = plt.gcf()
        st.pyplot(fig, clear_figure=True)

    except Exception as e:
        st.warning(f"Force plot could not be displayed: {e}")


##------------------------------------
###  FOR RAG CLINICAL INTERPRETATION
##------------------------------------
        
def render_clinical_interpretation_section(
    patient_row,
    prediction_result,
    factor_result
):

    # =====================================================
    # GET CURRENT PATIENT ID
    # =====================================================

    patient_id = str(
        patient_row.get(
            "patient_id",
            ""
        )
    ).strip()


    # Give each patient their own RAG cache
    rag_key = (
        f"clinical_rag_result_{patient_id}"
    )

    review_key = (
        f"clinical_rag_reviewed_{patient_id}"
    )

    edit_key = (
        f"clinical_rag_edit_{patient_id}"
    )


    # =====================================================
    # TOP FACTORS FOR RAG
    # =====================================================

    increasing_factors = factor_result.get(
        "increasing",
        []
    )

    top_factors = increasing_factors[:4]


    if not top_factors:

        st.info(
            "No risk-increasing model factors are "
            "available for clinical interpretation."
        )

        return


    # =====================================================
    # SECTION SPACING
    # =====================================================

    st.markdown(
        "<div style='height:24px;'></div>",
        unsafe_allow_html=True
    )


    # =====================================================
    # GENERATE BUTTON
    # =====================================================

    if rag_key not in st.session_state:

        st.markdown("""<div class="rag-generation-card">
            <div class="rag-generation-header">
                <div class="rag-generation-icon">
                    ✦
                </div>
                <div>
                    <div class="rag-generation-title">
                        AI Generated Clinical Summary
                    </div>
                    <div class="rag-generation-header-subtitle">
                        Evidence-grounded clinical decision support
                    </div>
                </div>
            </div>
            <div class="rag-generation-body">
                <div class="rag-generation-description">
                    Generate a patient-specific clinical summary using
                    the model's risk factors and evidence retrieved from
                    rehabilitation guidelines.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True)

    if st.button(
        "✦ Generate Clinical Interpretation",
        key=f"generate_rag_{patient_id}",
        type="primary"
    ):
        with st.spinner(
            "Searching clinical guidelines and generating interpretation..."
        ):

            try:
                result = (
                    build_rag_clinical_interpretation(
                        patient_row,
                        prediction_result,
                        top_factors
                    )
                )

                st.session_state[rag_key] = result

                st.rerun()

            except Exception as error:

                st.error(
                    "Clinical interpretation could not be generated."
                )

                st.exception(error)

        return

    # =====================================================
    # GET GENERATED RESULT
    # =====================================================

    result = st.session_state.get(
    rag_key,
    None)

    if result is None:
        return

    interpretation_text = result.get(
        "text",
        ""
    )

    sources = result.get(
        "sources",
        []
    )

    if not interpretation_text:
        st.warning(
            "The interpretation service returned an empty response. "
            "Please try generating it again."
        )
        return

    # =====================================================
    # RENDER GENERATED RESULT
    # =====================================================

    st.markdown("### AI Generated Clinical Interpretation")
    st.caption(
        "Decision-support draft only. Review and edit before using "
        "it in clinical documentation."
    )
    st.markdown(interpretation_text)

    if sources:
        with st.expander(
            f"Retrieved guideline evidence ({len(sources)} sources)"
        ):
            for index, source in enumerate(sources, start=1):
                metadata = getattr(source, "metadata", {}) or {}
                filename = metadata.get("filename", "Unknown source")
                page = metadata.get("page", "Unknown page")
                st.markdown(f"**{index}. {filename} — page {page}**")

                excerpt = getattr(source, "page_content", "")
                if excerpt:
                    st.caption(excerpt)
