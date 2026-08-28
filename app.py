import streamlit as st
import pandas as pd
import plotly.express as px
from utils.styles import load_css
from components.cards import (
    colored_card,
    colored_border_card,
    section_header,
)
from utils.supabase_client import get_supabase_client

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Patient QoL Dashboard",
    layout="wide",
    page_icon="🏥",
)

# =========================================================
# HOME PAGE
# =========================================================

def home():

    # -----------------------------------------------------
    # LOAD SYNTHETIC DEMO DATA FROM SUPABASE
    # -----------------------------------------------------

    supabase = get_supabase_client()

    @st.cache_data(ttl=300)
    def load_patients():
        response = (
            supabase
            .table("demo_patients")
            .select("*")
            .execute()
        )
        return pd.DataFrame(response.data)
       

    df = load_patients()

    # -----------------------------------------------------
    # SAFETY CHECK
    # -----------------------------------------------------

    if df.empty:
        st.error(
            "No patient records were found in the "
            "'demo_patients' Supabase table."
        )
        st.stop()

    required_columns = [
        "patient_id",
        "age",
        "gender",
        "label",
        "qol_change",
        "adm_vas",
        "dis_vas",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        st.error(
            "The demo_patients table is missing the following "
            f"required columns: {', '.join(missing_columns)}"
        )
        st.stop()

    # -----------------------------------------------------
    # DATA TYPE CLEANING
    # -----------------------------------------------------

    numeric_columns = [
        "age",
        "gender",
        "qol_change",
        "adm_vas",
        "dis_vas",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # LOAD DASHBOARD STYLES
    # -----------------------------------------------------

    load_css("styles/main.css")

    # =====================================================
    # DASHBOARD HEADER
    # =====================================================

    st.title("🏥 Patient QoL Dashboard")

    st.markdown(
        """
        <div style="
            background-color: #e8e7dd;
            padding: 20px;
            border-radius: 10px;
            border-left: 6px solid #4CAF50;
            margin-bottom: 30px;">
            <p>
                This dashboard provides an overview of
                <b>patient quality-of-life (QoL)</b> and predicts the
                <b>risk of QoL decline</b> to support clinical
                decision-making.It integrates <b>machine learning</b> and
                <b>explainable AI</b> to improve transparency
                and interpretation of model predictions.
            </p>
            <p style="
                margin-top: 12px;
                font-size: 0.9rem;
                color: #555;">
                <b>Demo Mode:</b>
                All patient records displayed in this dashboard
                are synthetic and are used for demonstration purposes only.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # OVERALL STATISTICS
    # =====================================================

    total_patients = len(df)

    # Only patients with an actual discharge outcome
    completed_df = df[
        df["label"].isin(
            ["decline", "no_decline"]
        )
    ].copy()

    completed_cases = len(completed_df)

    pending_cases = total_patients - completed_cases

    decline_cases = (
        completed_df["label"] == "decline"
    ).sum()

    no_decline_cases = (
        completed_df["label"] == "no_decline"
    ).sum()

    decline_rate = (
        (decline_cases / completed_cases) * 100
        if completed_cases > 0
        else 0
    )

    # =====================================================
    # SUMMARY CARDS
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        colored_card(
            "Total Patients",
            total_patients,
            "#4A90E2",
        )

    with col2:
        colored_border_card(
            "Decline Cases",
            decline_cases,
            "#fdecea",
            "#ea1b64",
        )

    with col3:
        colored_border_card(
            "No Decline Cases",
            no_decline_cases,
            "#e8f5e9",
            "#7feb9f",
        )

    with col4:
        st.metric(
            "Decline Rate",
            f"{decline_rate:.1f}%",
            help=(
                "Calculated only from patients with "
                "completed discharge outcomes."
            ),
            border=True,
        )

    # Optional extra information about pending cases
    st.caption(
        f"{completed_cases} patients have completed discharge outcomes, "
        f"while {pending_cases} patients are still pending discharge."
    )

    # =====================================================
    # PATIENT DEMOGRAPHICS
    # =====================================================

    section_header(
        "Patient Demographics",
        icon="boy",
    )

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # GENDER PIE CHART
    # -----------------------------------------------------

    with col1:

        gender_labels = df["gender"].map(
            {
                0: "Male",
                1: "Female",
            }
        )

        gender_counts = (
            gender_labels
            .dropna()
            .value_counts()
        )

        fig_gender = px.pie(
            values=gender_counts.values,
            names=gender_counts.index,
            title="Gender Distribution",
            hole=0.4,
        )

        fig_gender.update_layout(
            title_font=dict(
                family="Space Grotesk",
                size=18,
            ),
            margin=dict(
                t=40,
                b=0,
                l=0,
                r=0,
            ),
        )

        st.plotly_chart(
            fig_gender,
            use_container_width=True,
        )

    # -----------------------------------------------------
    # AGE HISTOGRAM
    # -----------------------------------------------------

    with col2:

        fig_age = px.histogram(
            df,
            x="age",
            nbins=20,
            title="Age Distribution",
            color_discrete_sequence=[
                "#4A90E2"
            ],
        )

        fig_age.update_traces(
            marker_line_width=1,
            marker_line_color="white",
        )

        fig_age.update_layout(
            title_font=dict(
                family="Space Grotesk",
                size=18,
            ),
            margin=dict(
                t=40,
                b=0,
                l=0,
                r=0,
            ),
            bargap=0.1,
        )

        st.plotly_chart(
            fig_age,
            use_container_width=True,
        )

    # =====================================================
    # SPACING
    # =====================================================

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    # =====================================================
    # CLINICAL OUTCOMES
    # =====================================================

    section_header(
        "Clinical Outcomes",
        icon="monitor_heart",
    )

    # -----------------------------------------------------
    # QOL CHANGE CLASSIFICATION
    # -----------------------------------------------------

    completed_df["qol_change"] = pd.to_numeric(
        completed_df["qol_change"],
        errors="coerce",
    )

    def classify_qol_change(value):

        if pd.isna(value):
            return "Unknown"

        if value > 0:
            return "Decline"

        if value < 0:
            return "Improved"

        return "No Change"

    completed_df["qol_label"] = (
        completed_df["qol_change"]
        .apply(classify_qol_change)
    )

    # Remove unknown values from outcome chart
    outcome_df = completed_df[
        completed_df["qol_label"] != "Unknown"
    ]

    qol_counts = (
        outcome_df["qol_label"]
        .value_counts(normalize=True)
        * 100
    )

    # -----------------------------------------------------
    # QOL OUTCOME BAR CHART
    # -----------------------------------------------------

    if not qol_counts.empty:

        fig_qol = px.bar(
            x=qol_counts.values,
            y=qol_counts.index,
            orientation="h",
            color=qol_counts.index,
            color_discrete_map={
                "Decline": "#e74c3c",
                "Improved": "#2ecc71",
                "No Change": "#f39c12",
            },
        )

        fig_qol.update_layout(
            title=dict(
                text="QoL Outcome Distribution (%)",
                font=dict(
                    family="Space Grotesk",
                    size=18,
                ),
                x=0,
            ),
            margin=dict(
                t=40,
                b=0,
                l=0,
                r=0,
            ),
            xaxis_title="Percentage (%)",
            yaxis_title="",
            showlegend=False,
        )

        st.plotly_chart(
            fig_qol,
            use_container_width=True,
        )

    else:
        st.info(
            "No completed QoL outcomes are currently available."
        )

    # =====================================================
    # VAS SCORE COMPARISON
    # =====================================================

    avg_adm_vas = (
        df["adm_vas"]
        .mean()
    )

    # Only discharged patients contribute to discharge VAS
    avg_dis_vas = (
        completed_df["dis_vas"]
        .mean()
    )

    vas_df = pd.DataFrame(
        {
            "Stage": [
                "Admission VAS",
                "Discharge VAS",
            ],
            "Average Score": [
                avg_adm_vas,
                avg_dis_vas,
            ],
        }
    )

    fig_vas = px.bar(
        vas_df,
        x="Stage",
        y="Average Score",
        text="Average Score",
        color="Stage",
        color_discrete_map={
            "Admission VAS": "#4A90E2",
            "Discharge VAS": "#2ECC71",
        },
    )

    fig_vas.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside",
    )

    fig_vas.update_layout(
        title=dict(
            text=(
                "Average VAS Score: "
                "Admission vs Discharge"
            ),
            font=dict(
                family="Space Grotesk, sans-serif",
                size=18,
            ),
            x=0,
        ),
        font=dict(
            family="Space Mono, monospace"
        ),
        xaxis_title="",
        yaxis_title="Average VAS Score",
        margin=dict(
            t=50,
            b=20,
            l=20,
            r=20,
        ),
        showlegend=False,
    )

    st.plotly_chart(
        fig_vas,
        use_container_width=True,
    )


# =========================================================
# NAVIGATION
# =========================================================

pg = st.navigation(
    [
        st.Page(
            home,
            title="Home",
            icon=":material/home:",
            default=True,
        ),

        # Patient Admission page currently disabled
        # st.Page(
        #     "pages/1_Patient_Admission.py",
        #     title="Patient Admission",
        #     icon=":material/group:",
        # ),

        st.Page(
            "pages/2_Patient_Records.py",
            title="Patient Records",
            icon=":material/monitoring:",
        ),

        st.Page(
            "pages/3_SHAP_Explanation.py",
            title="QOL Risk Prediction",
            icon=":material/insights:",
        ),
    ]
)

pg.run()