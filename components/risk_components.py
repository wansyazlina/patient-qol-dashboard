import streamlit as st
import pandas as pd
from utils.image_utils import get_icon_base64, FEATURE_ICONS
from utils.explain import get_top_risk_factors
import base64
from pathlib import Path



def render_patient_summary_cards(patient_row, prediction_result):
    # ---------------------------
    # STYLE (load once ideally)
    # ---------------------------
    st.markdown("""
    <style>
    .patient-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border: 1px solid #ecece6;
    }
    .patient-name {
        font-size: 19px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .patient-id {
        font-size: 14px;
        color: #777;
        margin-bottom: 12px;
    }
    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------------------
    # DATA
    # ---------------------------
    name = patient_row.get("name", "Unknown")
    patient_id = patient_row.get("patient_id", "-")
    age = patient_row.get("age", "-")
    gender = str(patient_row.get("gender", "Unknown")).strip().lower()
    predicted_class = str(prediction_result.get("predicted_class", "Unknown")).strip()

    # ---------------------------
    # STATUS LOGIC FROM dis_vas
    # ---------------------------
    dis_vas = patient_row.get("dis_vas", None)

    # treat NaN / None / empty string as missing
    is_discharged = pd.notna(dis_vas) and str(dis_vas).strip() != ""

    if is_discharged:
        status = "discharged"
    else:
        status = "active"

    # ---------------------------
    # BADGES
    # ---------------------------
    if gender in ["0", "male"]:
        gender_badge = "<span class='badge' style='background:#e6f0ff;color:#1f4ed8;'>♂ Male</span>"
    elif gender in ["1", "female"]:
        gender_badge = "<span class='badge' style='background:#ffe6f0;color:#d81f60;'>♀ Female</span>"
    else:
        gender_badge = "<span class='badge' style='background:#eee;color:#555;'>Unknown</span>"

    if status == "active":
        status_badge = "<span class='badge' style='background:#e6f9ed;color:#1a7f37;'>● Active</span>"
    else:
        status_badge = "<span class='badge' style='background:#fdeaea;color:#b42318;'>● Discharged</span>"

    if predicted_class.lower() == "decline":
        pred_badge = "<span class='badge' style='background:#fdeaea;color:#b42318;'>Decline</span>"
        border_color = "#f5c2c0"
    else:
        pred_badge = "<span class='badge' style='background:#e6f9ed;color:#1a7f37;'>No Decline</span>"
        border_color = "#b7ebc6"

    # ---------------------------
    # LAYOUT
    # ---------------------------
    initial = str(name)[0].upper() if name else "P"

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:20px; 
            padding: 20px 30px; background:white; border-radius:10px;
            border-left:5px solid {border_color};">
        <!-- Avatar -->
        <div style="
            width:80px; height:80px; border-radius:50%;
            background:#e0e0e0;
            display:flex; align-items:center; justify-content:center;
            font-weight:bold; font-size:30px;">
            {initial}
        </div>
        <!-- Info -->
        <div>
            <div class="patient-name">{name}</div>
            <div class="patient-id">Patient ID: {patient_id}</div>
           <div class="patient-details">
                Age: {age} {gender_badge} {status_badge}
            </div>
            <div class="patient-prediction">
                <b>Prediction:</b> {pred_badge}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---RISK TAB --- FUNCTION CALL on 3_SHAP_explanation page


def render_prediction_cards(prediction_result):

    pred_class = prediction_result["predicted_class"]
    prob_decline = float(prediction_result["prob_decline"])

    risk_label = prediction_result["risk_level"]
    marker_color = prediction_result["risk_color"]
    risk_bg = prediction_result["risk_bg"]

    risk_percent = prob_decline * 100
    threshold = 0.35
    
    if prob_decline >= threshold:
        interpretation = (
            "This patient exceeds the screening threshold "
            "and may require closer QoL monitoring."
        )
    else:
        interpretation = (
            "This patient's predicted risk is below the "
            "screening threshold."
        )

    st.markdown(
        f"""
        <div class="prediction-card"
            style="
                background:{risk_bg};
                border:1px solid {marker_color}22;">
            <!-- LEFT SIDE -->
            <div class="prediction-summary">
                <div class="ai-prediction-header">
                    <span class="ai-prediction-icon">🧠</span>
                    <span class="ai-prediction-title">AI Prediction</span>
                </div>
                <div class="prediction-title">
                    Predicted QoL Decline Risk
                </div>
                <div class="prediction-main-row">
                    <div
                        class="prediction-score"
                        style="color:{marker_color};"
                    >
                        {prob_decline:.1%}
                    </div>
                    <div
                        class="risk-badge"
                        style="
                            color:{marker_color};
                            border-color:{marker_color};">
                        {risk_label}
                    </div>
                </div>
                <!-- Threshold + Interpretation on same row -->
                <div class="prediction-info-row">
                    <div
                        class="prediction-threshold"
                        style="color:{marker_color};">
                        Threshold: {threshold:.0%}
                    </div>
                    <div class="prediction-description">
                        {interpretation}
                    </div>
                </div>
            </div>
            <!-- RIGHT SIDE -->
            <div class="risk-section">
                <div class="risk-bar-container">
                    <!-- Percentage bubble -->
                    <div
                        class="risk-bubble"
                        style="
                            left:{risk_percent:.1f}%;
                            background:{marker_color};">
                        {prob_decline:.1%}
                        <div
                            class="risk-bubble-arrow"
                            style="
                                border-top:
                                7px solid {marker_color};
                            ">
                        </div>
                    </div>
                    <!-- Risk bar -->
                    <div class="risk-bar">
                        <div class="risk-low-bar"></div>
                        <div class="risk-moderate-bar"></div>
                        <div class="risk-high-bar"></div>
                    </div>
                    <!-- Current patient marker -->
                    <div
                        class="risk-marker"
                        style="
                            left:{risk_percent:.1f}%;
                            background:{marker_color};
                        ">
                    </div>
                </div>
                <!-- Risk range labels -->
                <div class="risk-labels">
                    <div class="risk-label-low">
                        Low Risk
                        <br>
                        <span class="risk-range">
                            0–34%
                        </span>
                    </div>
                    <div class="risk-label-moderate">
                        Moderate Risk
                        <br>
                        <span class="risk-range">
                            35–59%
                        </span>
                    </div>
                    <div class="risk-label-high">
                        High Risk
                        <br>
                        <span class="risk-range">
                            60–100%
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
        

# --------ACTUAL VS PREDICTION outcome (r2) ----------------


def render_actual_outcome_match_cards(patient_row, prediction_result):

    # ----- MAKING SURE it detects no_decline and no decline -----

    raw_predicted = prediction_result.get("predicted_class", "")
    raw_actual = patient_row.get("label", "")

    def normalize_label(label):
        if label is None:
            return ""
        return str(label).strip().lower().replace("_", " ")

    def display_label(label):
        if label is None:
            return "N/A"
        return str(label).strip().replace("_", " ").title()

    pred_norm = normalize_label(raw_predicted)
    actual_norm = normalize_label(raw_actual)

    predicted_label = display_label(raw_predicted)
    actual_label = display_label(raw_actual)

    # ---------------------------------------------------------
    # Divider
    # ---------------------------------------------------------

    st.markdown(
        """
        <hr style="
            border:none;
            border-top:3px solid rgba(0,0,0,0.08);
            margin:5px 0 0px 0;
        ">
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # Get values safely
    # ---------------------------------------------------------

    patient_status = str(
        patient_row.get("status", "")
    ).strip().lower()

    actual_label = str(
        patient_row.get("label", "Unknown")
    ).strip()

    predicted_label = str(
        prediction_result.get(
            "predicted_class",
            "Unknown"
        )
    ).strip()

    # discharge / actual outcome info
    adm_qol = patient_row.get("qol_pre_total", None)
    dis_qol = patient_row.get("qol_post_total", None)
    outcome = patient_row.get("qol_change", None)

    # optional top risk factor
    top_risk_factor = prediction_result.get(
        "top_risk_factor",
        "Not available"
    )

    # ---------------------------------------------------------
    # Handle predicted label mapping if model returns 0/1
    # ---------------------------------------------------------

    if predicted_label == "0":
        predicted_label = "decline"

    elif predicted_label == "1":
        predicted_label = "no_decline"

    # ---------------------------------------------------------
    # IMPORTANT:
    # No discharge QoL = actual outcome is still pending
    # ---------------------------------------------------------

    is_outcome_pending = (
        pd.isna(dis_qol)
        or str(dis_qol).strip() == ""
    )

    # You can still keep this if used elsewhere
    is_active = patient_status == "active"

    # ---------------------------------------------------------
    # Match logic
    # ---------------------------------------------------------

    if is_outcome_pending:

        match_text = "Pending"
        match_icon = "⏳"
        match_color = "#3478db"
        match_bg = "#eef5ff"
        match_note = (
            "The patient is still undergoing admission, "
            "so discharge and prediction match cannot yet be evaluated."
        )

    else:

        is_match = pred_norm == actual_norm

        if is_match:

            match_text = "Correct"
            match_icon = "✅"
            match_color = "#2e8b57"
            match_bg = "#eaf7ee"

            match_note = (
                f"Prediction was {predicted_label} "
                f"and actual was {actual_label}."
            )

        else:

            match_text = "Incorrect"
            match_icon = "❌"
            match_color = "#d9534f"
            match_bg = "#fdeaea"

            match_note = (
                f"Prediction was {predicted_label} "
                f"but actual was {actual_label}."
            )
            
    # ---------------------------------------------------------
    # Spacing above both cards
    # ---------------------------------------------------------

    st.markdown(
        "<div style='height: 18px;'></div>",
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # Equal-height card styling
    # ---------------------------------------------------------
    
    

    c1, c2 = st.columns(2, gap="medium")

    display_outcome = (
        actual_label
        if actual_label
        else "N/A"
    )

    display_outcome = (
        display_outcome
        .replace("_", " ")
        .title()
    )

# =========================================================
# CARD 1: Top Risk Contributors
# =========================================================

    with c1:

        top_factors = get_top_risk_factors(
            prediction_result,
            top_n=3,
            positive_only=True
        )

        if not top_factors:

            factors_html = """<div style="
                font-size:13px;
                color:#555;">
                No explainability data available.
            </div>"""

        else:

            max_abs_shap = max(
                abs(f["shap_value"])
                for f in top_factors
            )

            factors_html = ""

            for f in top_factors:

                # -------------------------------------------------
                # Feature information
                # -------------------------------------------------

                feature_name = f.get(
                    "feature",
                    ""
                )

                display_name = f.get(
                    "display_name",
                    feature_name
                )

                description = f.get(
                    "description",
                    "No description available."
                )

                feature_value = f.get(
                    "feature_value",
                    "N/A"
                )

                shap_value = f.get(
                    "shap_value",
                    0
                )

                # -------------------------------------------------
                # SHAP bar width
                # -------------------------------------------------

                if max_abs_shap > 0:

                    bar_width = max(10,int((abs(shap_value)/ max_abs_shap) * 100))

                else:
                    bar_width = 10

                # -------------------------------------------------
                # Feature icon
                # -------------------------------------------------

                icon_path = FEATURE_ICONS.get(
                    feature_name
                )

                icon_src = (
                    get_icon_base64(icon_path)
                    if icon_path
                    else None
                )
                if icon_src:
                    icon_html = f"""<div class="risk-feature-icon-wrapper">
                        <img
                            src="{icon_src}"
                            class="risk-feature-icon"
                            alt="{display_name}"></div>"""
                else:

                    icon_html = """<div class="risk-feature-icon-wrapper">
                        ?
                    </div>"""


                # -------------------------------------------------
                # Individual contributor card
                # -------------------------------------------------

                factors_html += f"""<div class="risk-factor-item">
                    <!-- LEFT: ICON -->
                    <div class="risk-factor-icon-column">
                        {icon_html}
                    </div>
                    <!-- RIGHT: CONTENT -->
                    <div class="risk-factor-content">
                        <!-- FEATURE NAME + VALUE -->
                        <div class="risk-factor-header">
                            <div class="risk-factor-name">
                                {display_name}
                            </div>
                            <div class="risk-factor-value">
                                Value: {feature_value}
                            </div>
                        </div>
                        <!-- DESCRIPTION -->
                        <div class="risk-factor-description">
                            {description}
                        </div>
                        <!-- SHAP CONTRIBUTION BAR -->
                        <div class="risk-factor-bar-background">
                            <div
                                class="risk-factor-bar-fill"
                                style="width:{bar_width}%;">
                            </div>
                        </div>
                    </div>
                </div>"""

        # ---------------------------------------------------------
        # Render Card 1
        # ---------------------------------------------------------
        
        st.markdown(
            f"""<div
                class="equal-height-card"
                style="
                    background:white;
                    border-radius:12px;
                    padding:18px;
                    border-left:6px solid #8e6bbf;
                    min-height:300px;
                    box-sizing:border-box;">
                <div class="observed-outcome-header">
                    <div
                        class="observed-outcome-icon"
                        style="background:#8e6bbf;">
                        📊
                    </div>
                    <div>
                        <div class="observed-outcome-title">
                            Why this prediction?
                        </div>
                        <div class="observed-outcome-subtitle">
                            Top 3 Factors contributing risks
                        </div>
                    </div>
                </div>
                {factors_html}
            </div>
            """,
            unsafe_allow_html=True)
    # =========================================================
    # CARD 2: Observed Outcome
    # =========================================================

    with c2:
        

        # -----------------------------------------------------
        # Actual outcome display
        # -----------------------------------------------------

        actual_display = (
            "Not Available Yet"
            if is_outcome_pending
            else actual_label.replace("_", " ").title()
        )

        actual_color_class = (
            "outcome-pending"
            if is_outcome_pending
            else "outcome-good"
            if actual_norm == "no decline"
            else "outcome-bad"
            if actual_norm == "decline"
            else "outcome-pending"
        )

        # -----------------------------------------------------
        # Discharge display
        # -----------------------------------------------------

        discharge_display = (
            "Pending"
            if is_outcome_pending
            else dis_qol
        )

        discharge_class = (
            "discharge-value-pending"
            if is_outcome_pending
            else "discharge-value-score"
        )

        actual_icon = (
            "⏳"
            if is_outcome_pending
            else "✓"
        )
        # -----------------------------------------------------
        # Different bottom section depending on pending state
        # -----------------------------------------------------

        if is_outcome_pending:
            comparison_html = """<div class="model-comparison comparison-pending">
                    <div class="comparison-status-icon pending-icon">i</div>
                    <div class="comparison-content">
                        <div class="comparison-title">
                            Model comparison unavailable
                        </div>
                        <div class="comparison-note">
                            The patient is still undergoing admission, so discharge outcome
                            and prediction match cannot yet be evaluated.
                        </div>
                    </div>
                </div>"""

        else:
            is_match = pred_norm == actual_norm
            if is_match:
                comparison_html = f"""<div class="model-comparison comparison-correct">
                        <div class="comparison-status-icon correct-icon">✓</div>
                        <div class="comparison-content">
                            <div class="comparison-title">
                                Prediction matched actual outcome
                            </div>
                            <div class="comparison-note">
                                Prediction was {predicted_label} and actual was {actual_label}.
                            </div>
                        </div>
                    </div>"""

            else:
                comparison_html = f"""<div class="model-comparison comparison-incorrect">
                        <div class="comparison-status-icon incorrect-icon">×</div>
                        <div class="comparison-content">
                            <div class="comparison-title">
                                Prediction did not match actual outcome
                            </div>
                            <div class="comparison-note">
                                Prediction was {predicted_label} and actual was {actual_label}.
                            </div>
                        </div>
                    </div>"""
        # -----------------------------------------------------
        # Render observed outcome card
        # -----------------------------------------------------

        # Clean, single-line class attributes to avoid unintended whitespace
        st.markdown(
            f"""
            <div class="observed-outcome-card">
                <div class="observed-outcome-header">
                    <div class="observed-outcome-icon">📋</div>
                    <div>
                        <div class="observed-outcome-title">Observed Outcome</div>
                        <div class="observed-outcome-subtitle">Actual observed data</div>
                    </div>
                </div>
                <div class="observed-outcome-grid">
                    <!-- Admission QoL -->
                    <div class="outcome-metric-card admission-card">
                        <div class="outcome-metric-label">Admission QoL</div>
                        <div class="outcome-metric-value admission-value">{adm_qol if pd.notna(adm_qol) else 'N/A'}</div>
                    </div>
                    <!-- Discharge QoL -->
                    <div class="outcome-metric-card discharge-card">
                        <div class="outcome-metric-label">Discharge QoL</div>
                        <div class="outcome-metric-value {discharge_class}">{discharge_display}</div>
                    </div>
                    <!-- Actual Outcome -->
                    <div class="outcome-metric-card actual-outcome-card">
                        <div>
                            <div class="outcome-metric-label">Actual Outcome</div>
                            <div class="actual-outcome-value {actual_color_class}">{actual_display}</div>
                        </div>
                        <div class="actual-outcome-icon {actual_color_class}">{actual_icon}</div>
                    </div>
                </div>
                <div class="outcome-divider"></div>
                {comparison_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
                    
# --------Show Clinical Patient Records---------------


def render_clinical_info_table(patient_row):

    st.markdown("""
    <h3 style="
        margin-bottom:10px;
        margin-top:20px">
        Patient Clinical Info
    </h3>
    """, unsafe_allow_html=True)

    measures = [
        ("Mobility", "adm_mobility", "dis_mobility"),
        ("Personal Care", "adm_personal_care", "dis_personal_care"),
        ("Normal Activity", "adm_normal_activity", "dis_normal_activity"),
        ("Pain / Discomfort", "adm_pain_uncomfort", "dis_pain_uncomfort"),
        ("Anxiety / Depression", "adm_anxiety_depress", "dis_anxiety_depress"),
        ("VAS Score", "adm_vas", "dis_vas"),
    ]

    rows_html = ""

    for label, adm_col, dis_col in measures:

        adm_val = patient_row.get(adm_col, "")
        dis_val = patient_row.get(dis_col, "")
        trend_html = ""

        # Only calculate if discharge exists
        if pd.notna(dis_val) and str(dis_val).strip() != "":
            try:
                adm_num = float(adm_val)
                dis_num = float(dis_val)
                # Special logic for VAS (higher = better)
                if label == "VAS Score":
                    if dis_num > adm_num:
                        trend_html = """
                        <span style="padding:4px 10px;border-radius:999px;
                        background:#eaf7ee;color:#1a7f37;font-weight:600;font-size:13px;">
                        ↑ Improved
                        </span>
                        """
                    elif dis_num < adm_num:
                        trend_html = """
                        <span style="padding:4px 10px;border-radius:999px;
                        background:#fdeaea;color:#b42318;font-weight:600;font-size:13px;">
                        ↓ Worsened
                        </span>
                        """
                    else:
                        trend_html = """
                        <span style="padding:4px 10px;border-radius:999px;
                        background:#f4f4f4;color:#666;font-weight:600;font-size:13px;">
                        → No Change
                        </span>
                        """
                # Normal EQ-5D (lower = better)
                else:
                    if dis_num > adm_num:
                        trend_html = """
                        <span style="padding:4px 10px;border-radius:999px;
                        background:#fdeaea;color:#b42318;font-weight:600;font-size:13px;">
                        ↑ Worsened
                        </span>
                        """
                    elif dis_num < adm_num:
                        trend_html = """
                        <span style="padding:4px 10px;border-radius:999px;
                        background:#eaf7ee;color:#1a7f37;font-weight:600;font-size:13px;">
                        ↓ Improved
                        </span>
                        """
                    else:
                        trend_html = """
                        <span style="padding:4px 10px;border-radius:999px;
                        background:#f4f4f4;color:#666;font-weight:600;font-size:13px;">
                        → No Change
                        </span>
                        """
            except:
                trend_html = ""
            # Build row HTML
            rows_html += f"""<tr style="border-top:1px solid #eee;"><td style="padding:12px 16px;">{label}</td><td style="padding:12px 16px;">{adm_val}</td><td style="padding:12px 16px;">{dis_val if pd.notna(dis_val) else ""}</td><td style="padding:12px 16px;">{trend_html}</td></tr>"""

    # Final table HTML
    table_html = f"""
    <table style="
        width:100%;
        border-collapse:collapse;
        background:white;
        border-radius:12px;
        overflow:hidden;
        box-shadow:0 4px 12px rgba(0,0,0,0.04);">
        <thead>
            <tr style="background:#f8f8f5; text-align:left;">
                <th style="padding:12px 16px;">Clinical Measure</th>
                <th style="padding:12px 16px;">Admission</th>
                <th style="padding:12px 16px;">Discharge</th>
                <th style="padding:12px 16px;">Change</th>
            </tr>
        </thead>
            <tbody>
                {rows_html}
            </tbody>
    </table>
    """

    # ✅ IMPORTANT: This line renders HTML correctly
    st.markdown(table_html, unsafe_allow_html=True)