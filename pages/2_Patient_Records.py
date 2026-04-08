import streamlit as st
import pandas as pd
from utils.styles import load_styles
import plotly.express as px
from components.cards import metric_cards,section_header
from components.patient_detail_cards import patient_summary_cards

st.set_page_config(page_title="Patient Records", layout="wide",page_icon="🏥")

load_styles()

st.title("💾 Patient Records")
st.markdown("""
    <div style="
        background-color: #e8e7dd;
        padding: 20px;
        border-radius: 10px;
        border-left: 6px solid #4CAF50;
        margin-bottom: 30px;
    ">
    <p>
    Browse and filter patient records,review QoL information, and inspect outcome labels
    </p>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("data/patient_qol_cleaned.csv")

df = load_data()

# ---- Calculate statistics
total_records = len(df)
total_male = (df["gender"] == 0).sum()
total_female = (df["gender"] == 1).sum()
average_age = df["age"].mean()
total_decline = (df["label"].str.lower() == "decline").sum()


st.write("This dashboard provides an overview of patient quality-of-life outcomes and prediction insights.")

metric_cards(
    total_records=total_records,
    total_male=total_male,
    total_female=total_female,
    average_age=average_age,
    total_decline=total_decline
)


def patient_details_section(df):

    # ---------- OPTIONAL: create display labels ----------
    df_display = df.copy()

    # Example mapping if your gender is encoded
    if "gender" in df_display.columns:
        df_display["gender_label"] = df_display["gender"].map({
            0: "Male",
            1: "Female"
        })

    # Example mapping if your outcome is encoded
    # Uncomment and adjust if needed
    # if "qol_outcome" in df_display.columns:
    #     df_display["qol_outcome_label"] = df_display["qol_outcome"].map({
    #         0: "Decline",
    #         1: "No Decline"
    #     })

    # ---------- FILTER SECTION ----------
    st.markdown("")
    section_header("Filter Patients",icon="boy")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        gender_options = ["All"]
        if "gender_label" in df_display.columns:
            gender_options += sorted(df_display["gender_label"].dropna().unique().tolist())
        selected_gender = st.selectbox("Gender", gender_options)

    with col2:
        if "age" in df_display.columns:
            min_age = int(df_display["age"].min())
            max_age = int(df_display["age"].max())
            selected_age = st.slider("Age Range", min_age, max_age, (min_age, max_age))
        else:
            selected_age = None

    with col3:
        outcome_options = ["All"]

        if "label" in df_display.columns:
            outcome_options += sorted(
                df_display["label"]
                .dropna()
                .astype(str)
                .str.strip()
                .str.lower()
                .unique()
                .tolist()
            )

        selected_outcome = st.selectbox("QoL Outcome", outcome_options)

    with col4:
        search_text = st.text_input("Search Patient ID / Name", "")

    # ---------- APPLY FILTERS ----------
    filtered_df = df_display.copy()

    if selected_gender != "All" and "gender_label" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["gender_label"] == selected_gender]

    if selected_age is not None and "age" in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df["age"] >= selected_age[0]) &
            (filtered_df["age"] <= selected_age[1])
        ]

    if selected_outcome != "All":
        filtered_df = filtered_df[
            filtered_df["label"]
            .astype(str)
            .str.strip()
            .str.lower() == selected_outcome
        ]

    if search_text:
        search_text_lower = search_text.lower()

        searchable_cols = []
        if "patient_id" in filtered_df.columns:
            searchable_cols.append(filtered_df["patient_id"].astype(str).str.lower())
        if "name" in filtered_df.columns:
            searchable_cols.append(filtered_df["name"].astype(str).str.lower())

        if searchable_cols:
            combined_mask = False
            for col in searchable_cols:
                combined_mask = combined_mask | col.str.contains(search_text_lower, na=False)
            filtered_df = filtered_df[combined_mask]

    # ---------- SUMMARY ----------
    st.caption(f"Showing {len(filtered_df)} of {len(df_display)} records")

    # ---------- DOWNLOAD BUTTON ----------
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered CSV",
        data=csv,
        file_name="filtered_patient_records.csv",
        mime="text/csv"
    )

    # ---------- TABLE DISPLAY WITH ROW SELECTION ----------
    section_header("Patient Table", icon=None)

    table_key = f"patient_table_{selected_gender}_{selected_age[0]}_{selected_age[1]}_{selected_outcome}_{search_text}"

    event = st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key=table_key
    )

    # ---------- SELECTED PATIENT DETAILS ----------
    selected_rows = event.selection["rows"]

    if selected_rows:
        selected_idx = selected_rows[0]
        patient = filtered_df.iloc[selected_idx]

        st.markdown("---")
        section_header("Selected Patient Details", icon=None)

        # top summary cards / fields
        #info_col1, info_col2, info_col3 = st.columns(3)
       
        # 4 columns now (image + 3 info columns)
        img_col, info_col1, info_col2, info_col3 = st.columns([1.2, 2, 2, 3])

        # 🖼️ Image column
        with img_col:
            st.image("assets/profilepic_placeholder.png", width=200)

        with info_col1:
            st.markdown(f"**Patient ID:** {patient['patient_id'] if 'patient_id' in patient else 'N/A'}")
            st.markdown(f"**Name:** {patient['name'] if 'name' in patient else 'N/A'}")
            st.markdown(f"**Gender:** {patient['gender_label'] if 'gender_label' in patient else 'N/A'}")

        with info_col2:
            st.markdown(f"**Age:** {patient['age'] if 'age' in patient else 'N/A'}")
            if 'dis_vas' in patient:
                st.markdown(f"**Discharge VAS:** {patient['dis_vas']}")
            st.markdown(f"**Admission VAS:** {patient['adm_vas'] if 'adm_vas' in patient else 'N/A'}")

        with info_col3:
            # overall QoL score — adjust these names if your file uses different column names
            qol_pre = patient["qol_pre_total"] if "qol_pre_total" in patient else "N/A"
            qol_post = patient["qol_post_total"] if "qol_post_total" in patient else "N/A"
            label_value = patient["label"] if "label" in patient else "N/A"

            patient_summary_cards(
                qol_pre=qol_pre,
                qol_post=qol_post,
                label=label_value
            )
            

        st.markdown("")
        st.markdown("#### Admission QoL Dimension Scores")

        qol_cols = st.columns(5)

        with qol_cols[0]:
            st.metric("Mobility", patient["adm_mobility"] if "adm_mobility" in patient else "N/A")

        with qol_cols[1]:
            st.metric("Personal Care", patient["adm_personal_care"] if "adm_personal_care" in patient else "N/A")

        with qol_cols[2]:
            st.metric("Normal Activity", patient["adm_normal_activity"] if "adm_normal_activity" in patient else "N/A")

        with qol_cols[3]:
            st.metric("Pain / Discomfort", patient["adm_pain_uncomfort"] if "adm_pain_uncomfort" in patient else "N/A")

        with qol_cols[4]:
            st.metric("Anxiety / Depression", patient["adm_anxiety_depress"] if "adm_anxiety_depress" in patient else "N/A")

        st.markdown("")
        st.markdown("#### Discharge QoL Dimension Scores")

        qol_cols_2 = st.columns(5)

        with qol_cols_2[0]:
            st.metric("Mobility", patient["dis_mobility"] if "dis_mobility" in patient else "N/A")

        with qol_cols_2[1]:
            st.metric("Personal Care", patient["dis_personal_care"] if "dis_personal_care" in patient else "N/A")

        with qol_cols_2[2]:
            st.metric("Normal Activity", patient["dis_normal_activity"] if "dis_normal_activity" in patient else "N/A")

        with qol_cols_2[3]:
            st.metric("Pain / Discomfort", patient["dis_pain_uncomfort"] if "dis_pain_uncomfort" in patient else "N/A")

        with qol_cols_2[4]:
            st.metric("Anxiety / Depression", patient["dis_anxiety_depress"] if "dis_anxiety_depress" in patient else "N/A")

        
    else:
        st.info("Click one patient row in the table above to view detailed information.")


patient_details_section(df)