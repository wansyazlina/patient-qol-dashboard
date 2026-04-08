import streamlit as st
import pandas as pd
from utils.explain import get_top_risk_factors


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
        font-size: 22px;
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
    <div style="display:flex; align-items:center; gap:15px; 
            padding:15px; background:white; border-radius:10px;
            border-left:5px solid {border_color};">
        <!-- Avatar -->
        <div style="
            width:60px; height:60px; border-radius:50%;
            background:#e0e0e0;
            display:flex; align-items:center; justify-content:center;
            font-weight:bold; font-size:20px;">
            {initial}
        </div>
        <!-- Info -->
        <div>
            <div style="font-weight:600; font-size:16px;">{name}</div>
            <div style="color:gray; font-size:13px;">Patient ID: {patient_id}</div>
            <div style="margin-top:6px;">Age: {age} {gender_badge} {status_badge}</div>
            <div style="margin-top:6px;"><b>Prediction:</b> {pred_badge}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---RISK TAB --- FUNCTION CALL on 3_SHAP_explanation page

def render_prediction_cards(prediction_result):
    pred_class = prediction_result["predicted_class"]
    prob_decline = float(prediction_result["prob_decline"])
    prob_no_decline = float(prediction_result["prob_no_decline"])

    # Label + color
    # normalize
    pred_str = str(pred_class).lower().strip()

    if pred_str in ["0", "decline"]:
        pred_label = "Decline"
        pred_color = "#d9534f"
        pred_bg = "#fdeaea"

    elif pred_str in ["1", "no_decline", "no decline"]:
        pred_label = "No Decline"
        pred_color = "#2e8b57"
        pred_bg = "#eaf7ee"

    else:
        pred_label = str(pred_class)
        pred_color = "#444"
        pred_bg = "#f4f4f4"

    st.markdown(" ")

    c1, c2 = st.columns([1.2, 2])

    # --- LEFT CARD ---
    with c1:
        st.markdown(f"""
        <div style="
            background:{pred_bg};
            border-left:6px solid {pred_color};
            border-radius:12px;
            padding:18px;
            font-family:'Space Grotesk', sans-serif;height:100%;min-height:170px;
            display:flex;flex-direction:column;
            justify-content:center;">
            
        <div style="font-size:17px;color:#666;margin-bottom:6px;letter-spacing:0.5px;">Predicted Class</div>
        <div style="
                font-size:26px;
                font-weight:700;
                color:{pred_color};">{pred_label}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --- RIGHT SIDE (STACKED BARS) ---
    with c2:

        # Decline
        st.markdown(f"""
        <div style="
            background:white;
            border-radius:12px;
            padding:16px;
            margin-bottom:12px;
            font-family:'Space Grotesk', sans-serif;
        ">
            <div style="
                display:flex;
                justify-content:space-between;
                margin-bottom:6px;
            ">
                <span>Decline Risk</span>
                <span style="font-family:'Space Mono', monospace; font-weight:600;">
                    {prob_decline:.2%}
                </span>
            </div>
            <div style="
                width:100%;
                background:#eee;
                border-radius:10px;
                height:12px;">
            <div style="
                width:{prob_decline * 100:.1f}%;
                background:#d9534f;
                height:12px;
                border-radius:10px;">
            </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # No Decline
        st.markdown(f"""
        <div style="
            background:white;
            border-radius:12px;
            padding:16px;
            font-family:'Space Grotesk', sans-serif;">
            <div style="
                display:flex;
                justify-content:space-between;
                margin-bottom:6px;">
                <span>No Decline Risk</span>
                <span style="font-family:'Space Mono', monospace; font-weight:600;">
                    {prob_no_decline:.2%}
                </span>
            </div>
            <div style="
                width:100%;
                background:#eee;
                border-radius:10px;
                height:12px;">
                <div style="
                    width:{prob_no_decline * 100:.1f}%;
                    background:#2e8b57;
                    height:12px;
                    border-radius:10px;
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        

# --------ACTUAL VS PREDICTION outcome (r2) ----------------



def render_actual_outcome_match_cards(patient_row, prediction_result):
    
    #-----MAKING SURE it detect no_decline and no decline
    
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
    
    #---------
   
    st.markdown(f""" 
            <hr style="border:none; border-top:3px solid rgba(0,0,0,0.08); margin-top:5px;"> 
            """, unsafe_allow_html=True)
    
    # --- get values safely ---
    patient_status = str(patient_row.get("status", "")).strip().lower()
    actual_label = str(patient_row.get("label", "Unknown")).strip()
    predicted_label = str(prediction_result.get(
        "predicted_class", "Unknown")).strip()

    # discharge / actual outcome info
    adm_qol = patient_row.get("qol_pre_total", None)
    dis_qol = patient_row.get("qol_post_total", None)
    outcome = patient_row.get("qol_change", None)

    # optional top risk factor
    top_risk_factor = prediction_result.get("top_risk_factor", "Not available")

    # --- handle predicted label mapping if model returns 0/1 ---
    if predicted_label == "0":
        predicted_label = "decline"
    elif predicted_label == "1":
        predicted_label = "no_decline"

    # --- active / discharged logic ---
    is_active = patient_status == "active"

    # --- match logic ---
    if is_active:
        match_text = "Pending"
        match_icon = "⏳"
        match_color = "#d4a017"
        match_bg = "#fff8e6"
        match_note = "Patient is still active. Actual outcome is not final yet."

    else:
        is_match = pred_norm == actual_norm   # ✅ FIXED HERE

        if is_match:
            match_text = "Correct"
            match_icon = "✅"
            match_color = "#2e8b57"
            match_bg = "#eaf7ee"
            match_note = f"Prediction was {predicted_label} and actual was {actual_label}."
        else:
            match_text = "Incorrect"
            match_icon = "❌"
            match_color = "#d9534f"
            match_bg = "#fdeaea"
            match_note = f"Prediction was {predicted_label} but actual was {actual_label}."
            
    ##styling card length dynamic
            
    st.markdown("""<style>
                /* Make columns in the same row stretch to equal height */
                div[data-testid="stHorizontalBlock"] {
                    align-items: stretch;}
    /* Make each column fill available height */
    div[data-testid="column"] > div {
        height: 100%;
    }
    /* Shared equal-height card style */
    .equal-height-card {
        background: white;
        border-radius: 12px;
        padding: 18px;
        min-height: 180px;
        height: 100%;
        font-family: 'Space Grotesk', sans-serif;
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    display_outcome = actual_label if actual_label else "N/A"
    #clean formatting
    display_outcome = display_outcome.replace("_", " ").title()

    # --- CARD 1: Actual Outcome ---
    with c1:
        if is_active:
            st.markdown(f"""<div class="equal-height-card" style="
                        background:white;
                        border-radius:12px;
                        padding:18px;
                        border-left:6px solid #d4a017;
                        min-height:180px;
                        font-family:'Space Grotesk', sans-serif;">
                        <div style="font-size:20px; color:#666; margin-bottom:10px;">
                        Actual Outcome (Discharge)</div>
                    <div style="font-size:16px;
                    font-weight:700;
                    color:#d4a017;
                    margin-bottom:10px;">Patient Still Active</div>

            <div class="equal-height-card" style="font-size:13px; color:#555; line-height:1.5;">
                This patient has not been discharged yet, so the final discharge outcome is not available.
            </div>
        </div>
        """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
        <div class="equal-height-card" style="
            background:white;
            border-radius:12px;
            padding:18px;
            border-left:6px solid #6c8ebf;
            min-height:180px;
            font-family:'Space Grotesk', sans-serif;">
            <div style="font-size:20px; color:#666; margin-bottom:10px;">
                Actual Outcome (Discharge)
            </div>
            <div style="font-size:14px; color:#444; margin-bottom:8px;">
                QoL Score
            </div>
            <div style="
                display:flex;
                align-items:center;
                gap:10px;
                margin-bottom:14px;
                font-family:'Space Mono', monospace;">
                <div style="
                    background:#f4f4f4;
                    padding:6px 10px;
                    border-radius:6px;
                    font-weight:600;">
                    {adm_qol if adm_qol is not None else 'N/A'}
                </div>
                <div style="font-size:16px; color:#888;">→</div>
                <div style="
                    background:#eaf7ee;
                    padding:6px 10px;
                    border-radius:6px;
                    font-weight:700;">
                    {dis_qol if dis_qol is not None else 'N/A'}
                </div>
            </div>
            <div style="font-size:14px; color:#444; margin-bottom:6px;">
                Outcome
            </div>
            <div class="equal-height-card" style="
                font-size:18px;
                font-weight:700;
                color:#2c3e50;
                text-transform:capitalize;">
                {display_outcome}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- CARD 2: Model vs Actual ---
    with c2:
        st.markdown(f"""
        <div class="equal-height-card" style=" 
            background:{match_bg};
            border-radius:12px;
            padding:18px;
            border-left:6px solid {match_color};
            min-height:180px;
            font-family:'Space Grotesk', sans-serif;
        ">
            <div style="font-size:20px; color:#666; margin-bottom:10px;">
                Model vs Actual
            </div>
            <div style="margin-bottom:10px; font-size:14px; color:#444;"><b>Prediction:</b> <span style="text-transform:capitalize;">{predicted_label}</span>
            </div>
            <div style="margin-bottom:14px; font-size:14px; color:#444;">
                <b>Actual:</b> <span style="text-transform:capitalize;">{actual_label if not is_active else 'Pending'}</span>
            </div>
            <div style="
                font-size:20px;
                font-weight:700;
                color:{match_color};
                margin-bottom:8px;
            ">
                {match_icon} {match_text}
            </div>
            <div class="equal-height-card" style="
                font-size:13px;
                color:#555;
                line-height:1.5;
            ">
                {match_note}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- CARD 3: Top Risk Factor ---
    with c3:
        # --- CARD 3: Top Risk Contributors ---
        top_factors = get_top_risk_factors(prediction_result, top_n=3, positive_only=True)

        if not top_factors:
            factors_html = """
            <div style="font-size:13px; color:#555;">
                No explainability data available.
            </div>
            """
        else:
            max_abs_shap = max(abs(f["shap_value"]) for f in top_factors)

            factors_html = ""
            for f in top_factors:
                display_name = f.get("display_name", f["feature"])
                description = f.get("description", "No description available.")
                feature_value = f.get("feature_value", "N/A")
                shap_value = f.get("shap_value", 0)
                bar_width = max(10, int((abs(shap_value) / max_abs_shap) * 100))

                factors_html += f"""
        <div style="background:#f8f6fc; border-radius:10px; padding:10px 12px; margin-bottom:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:6px;">
                <div style="font-size:15px; font-weight:700; color:#5b3d8a;">
                    {display_name}
                </div>
                <div style="font-size:12px; font-family:'Space Mono', monospace; color:#7a5bb3; white-space:nowrap;">
                    value: {feature_value}
                </div>
            </div>
            <div style="width:100%; background:#e9e1f5; border-radius:8px; height:8px; margin-bottom:8px; overflow:hidden;">
                <div style="width:{bar_width}%; background:#8e6bbf; height:8px; border-radius:8px;"></div>
            </div>
            <div style="font-size:12px; color:#555; line-height:1.45;">
                {description}
            </div>
        </div>
        """
        st.markdown(f"""
        <div class="equal-height-card" style="
            background:white;
            border-radius:12px;
            padding:18px;
            border-left:6px solid #8e6bbf;
            min-height:180px;
            font-family:'Space Grotesk', sans-serif;
        ">
            <div style="font-size:20px; color:#666; margin-bottom:12px;">
                Top Decline Risk Contributors
            </div>
            {factors_html}
        </div>
        """, unsafe_allow_html=True)
                    
# --------Show Clinical Patient Records---------------

def render_clinical_info_table(patient_row):

    st.markdown("""
    <h3 style="
        font-family:'Space Grotesk', sans-serif;
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
        font-family:'Space Grotesk', sans-serif;
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