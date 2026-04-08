import streamlit as st
import pandas as pd
from utils.styles import load_styles
from utils.predict import load_model
import plotly.express as px
from components.cards import colored_card, colored_border_card,section_header
from utils.supabase_client import get_supabase_client


st.set_page_config(page_title="Patient QoL Dashboard", layout="wide",page_icon="🏥")

def home():

    #----LOAD DATA FROM SUPABASE 
    supabase = get_supabase_client()

    @st.cache_data(ttl=300)
    def load_patients():
        response = supabase.table("patients").select("*").execute()
        return pd.DataFrame(response.data)

    df = load_patients()
    
    load_styles()
    
    st.title("🏥 Patient QoL Dashboard")
    st.markdown("""
    <div style="
        background-color: #e8e7dd;
        padding: 20px;
        border-radius: 10px;
        border-left: 6px solid #4CAF50;
        margin-bottom: 30px;
    ">
    <p>
    This dashboard provides an overview of <b>patient quality-of-life (QoL)</b> and predicts the 
    <b>risk of QoL decline</b> to support clinical decision-making. 
    It integrates <b>machine learning</b> and <b>explainable AI</b> for transparency and insight.
    </p>
    </div>
    """, unsafe_allow_html=True)

    

 
    #--- Calculate statistics
    total_patients = len(df)
    decline_cases = (df["label"] == "decline").sum()
    no_decline_cases = (df["label"] == "no_decline").sum()
    decline_rate = (decline_cases / len(df)) * 100
    gender_counts = df["gender"].value_counts()
    df["qol_label"] = df["qol_change"].apply(
        lambda x: "Decline" if x > 0 else ("Improved" if x < 0 else "No Change")
    )

    qol_counts = df["qol_label"].value_counts(normalize=True) * 100

    df["adm_vas"] = pd.to_numeric(df["adm_vas"], errors="coerce")
    df["dis_vas"] = pd.to_numeric(df["dis_vas"], errors="coerce")
    avg_adm_vas = df["adm_vas"].mean()
    avg_dis_vas = df["dis_vas"].mean()

    vas_df = pd.DataFrame({
        "Stage": ["Admission VAS", "Discharge VAS"],
        "Average Score": [avg_adm_vas, avg_dis_vas]
    })


    # ---- CARDs ----- Create design columns (4cards)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with col1:
            colored_card("Total Patients", total_patients, "#4A90E2")  # blue

    with col2:
        colored_border_card("Decline Cases", decline_cases,"#fdecea", "#ea1b64") 

    with col3:
        colored_border_card("No Decline Cases", no_decline_cases,"#e8f5e9", "#7feb9f")

    with col4:
        st.metric(
        "Decline Rate",
        f"{decline_rate:.1f}%",
        delta=f"{decline_rate - 20:.1f}% vs baseline",  # example baseline
        border=True
    )
        

    # ---- QoL HORIZONTAL BAR (PATIENT DEMOGRAPHICS) ----
    section_header("Patient Demographics",icon="boy")
    
    col1, col2 = st.columns(2)

    # ---- Gender Pie ----
    with col1:
        gender_counts = df["gender"].value_counts()

        fig_gender = px.pie(
            values=gender_counts.values,
            names=gender_counts.index,
            title="Gender Distribution",
            hole=0.4
        )

        fig_gender.update_layout(
            title_font=dict(
                family="Space Grotesk",size=18
                ),
            margin=dict(t=40, b=0, l=0, r=0)
        )

        st.plotly_chart(fig_gender, use_container_width=True)


    # ---- Age Histogram ----
    with col2:
        fig_age = px.histogram(
            df,
            x="age",
            nbins=20,
            title="Age Distribution",
            color_discrete_sequence=["#4A90E2"]
        )

        fig_age.update_traces(
            marker_line_width=1,
            marker_line_color="white"
        )

        fig_age.update_layout(
            title_font=dict(
                family="Space Grotesk",size=18
                ),
            margin=dict(t=40, b=0, l=0, r=0),
            bargap=0.1
        )

        st.plotly_chart(fig_age, use_container_width=True)
   
   # ---- SPACING ----
    st.markdown("<br>", unsafe_allow_html=True)

   # ---- QoL HORIZONTAL BAR (CLINICAL OUTCOMES) ----
    section_header("Clinical Outcomes",icon="monitor_heart")

    fig_qol = px.bar(
        x=qol_counts.values,
        y=qol_counts.index,
        orientation='h',
        color=qol_counts.index,
        color_discrete_map={
            "Decline": "#e74c3c",
            "Improved": "#2ecc71",
            "No Change": "#f39c12"
        }
    )

    fig_qol.update_layout(
        title=dict(
            text="QoL Outcome Distribution (%)",
            font=dict(family="Space Grotesk", size=18),
            x=0
        ),
        margin=dict(t=40, b=0, l=0, r=0),
        xaxis_title="Percentage (%)",
        yaxis_title=""
    )

    st.plotly_chart(fig_qol, use_container_width=True)

    fig_vas = px.bar(
    vas_df,
    x="Stage",
    y="Average Score",
    title="Average VAS Score: Admission vs Discharge",
    text="Average Score",
    color="Stage",
    color_discrete_map={
        "Admission VAS": "#4A90E2",
        "Discharge VAS": "#2ECC71"
    }
    )

    fig_vas.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_vas.update_layout(
        title=dict(
            text="Average VAS Score: Admission vs Discharge",
            font=dict(
                family="Space Grotesk, sans-serif",
                size=18
            ),
            x=0
        ),
        font=dict(
            family="Space Mono, monospace"
        ),
        xaxis_title="",
        yaxis_title="Average VAS Score",
        margin=dict(t=50, b=20, l=20, r=20),
        showlegend=False
    )

    st.plotly_chart(fig_vas, use_container_width=True)
   
  
# NAVIGATION - side menu

pg = st.navigation([
    st.Page(home, title="Home", icon=":material/home:", default=True),
   # st.Page("pages/1_Patient_Admission.py", title="Patient Admission", icon=":material/group:"),
    st.Page("pages/2_Patient_Records.py", title="Patient Records", icon=":material/monitoring:"),
    st.Page("pages/3_SHAP_Explanation.py", title="QOL Risk Prediction", icon=":material/insights:"),
])

pg.run()

