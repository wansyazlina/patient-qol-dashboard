import streamlit as st
import pandas as pd

from utils.styles import load_styles
from components.cards import metric_cards, section_header
from components.patient_detail_cards import patient_summary_cards
from utils.supabase_client import get_supabase_client


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Patient Records",
    layout="wide",
    page_icon="🏥",
)


# =========================================================
# LOAD SYNTHETIC DEMO DATA
# =========================================================

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


# =========================================================
# SAFETY CHECK
# =========================================================

if df.empty:
    st.error(
        "No patient records were found in the "
        "'demo_patients' Supabase table."
    )
    st.stop()


required_columns = [
    "patient_id",
    "name",
    "age",
    "gender",
    "label",
    "adm_vas",
    "dis_vas",
    "qol_pre_total",
    "qol_post_total",
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


# =========================================================
# CLEAN DATA TYPES
# =========================================================

numeric_columns = [
    "age",
    "gender",
    "adm_vas",
    "dis_vas",
    "qol_pre_total",
    "qol_post_total",
    "qol_change",
    "adm_mobility",
    "adm_personal_care",
    "adm_normal_activity",
    "adm_pain_uncomfort",
    "adm_anxiety_depress",
    "dis_mobility",
    "dis_personal_care",
    "dis_normal_activity",
    "dis_pain_uncomfort",
    "dis_anxiety_depress",
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# Clean outcome labels
df["label"] = (
    df["label"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)


# =========================================================
# DISPLAY LABELS
# =========================================================

df["gender_label"] = df["gender"].map(
    {
        0: "Male",
        1: "Female",
    }
)


def get_outcome_label(value):

    if value == "decline":
        return "Decline"

    if value == "no_decline":
        return "No Decline"

    return "Pending Discharge"


df["outcome_label"] = (
    df["label"]
    .apply(get_outcome_label)
)


# =========================================================
# STYLES + HEADER
# =========================================================

load_styles()

st.title("💾 Patient Records")

st.markdown(
    """
    <div style="
        background-color: #e8e7dd;
        padding: 20px;
        border-radius: 10px;
        border-left: 6px solid #4CAF50;
        margin-bottom: 30px;">
        <p>
            Browse and filter synthetic patient records,
            review QoL information, and inspect available
            clinical outcomes.
        </p>
        <p style="
            margin-top: 10px;
            font-size: 0.9rem;
            color: #555;">
            <b>Demo Mode:</b>
            All patient records displayed here are synthetic
            and are used for demonstration purposes only.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SUMMARY STATISTICS
# =========================================================

total_records = len(df)

total_male = (
    df["gender"] == 0
).sum()

total_female = (
    df["gender"] == 1
).sum()

average_age = (
    df["age"]
    .mean()
)

total_decline = (
    df["label"] == "decline"
).sum()

completed_records = (
    df["label"]
    .isin(["decline", "no_decline"])
    .sum()
)

pending_records = (
    total_records
    - completed_records
)


metric_cards(
    total_records=total_records,
    total_male=total_male,
    total_female=total_female,
    average_age=average_age,
    total_decline=total_decline,
)


st.caption(
    f"{completed_records} patients have completed discharge outcomes, "
    f"while {pending_records} are still pending discharge."
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def display_value(value, decimals=None):

    if pd.isna(value):
        return "Pending"

    if decimals is not None:
        return f"{value:.{decimals}f}"

    if isinstance(value, float) and value.is_integer():
        return int(value)

    return value


# =========================================================
# PATIENT DETAILS SECTION
# =========================================================

def patient_details_section(df):

    df_display = df.copy()

    # -----------------------------------------------------
    # FILTER SECTION
    # -----------------------------------------------------

    st.markdown("")

    section_header(
        "Filter Patients",
        icon="boy",
    )

    col1, col2, col3, col4 = st.columns(4)

    # Gender filter
    with col1:

        gender_options = [
            "All",
            "Male",
            "Female",
        ]

        selected_gender = st.selectbox(
            "Gender",
            gender_options,
        )

    # Age filter
    with col2:

        valid_age = (
            df_display["age"]
            .dropna()
        )

        if not valid_age.empty:

            min_age = int(
                valid_age.min()
            )

            max_age = int(
                valid_age.max()
            )

            selected_age = st.slider(
                "Age Range",
                min_age,
                max_age,
                (
                    min_age,
                    max_age,
                ),
            )

        else:
            selected_age = None

    # Outcome filter
    with col3:

        outcome_options = [
            "All",
            "Decline",
            "No Decline",
            "Pending Discharge",
        ]

        selected_outcome = st.selectbox(
            "QoL Outcome",
            outcome_options,
        )

    # Search
    with col4:

        search_text = st.text_input(
            "Search Patient ID / Name",
            "",
        )


    # -----------------------------------------------------
    # APPLY FILTERS
    # -----------------------------------------------------

    filtered_df = df_display.copy()

    # Gender
    if selected_gender != "All":

        filtered_df = filtered_df[
            filtered_df["gender_label"]
            == selected_gender
        ]

    # Age
    if selected_age is not None:

        filtered_df = filtered_df[
            (
                filtered_df["age"]
                >= selected_age[0]
            )
            &
            (
                filtered_df["age"]
                <= selected_age[1]
            )
        ]

    # Outcome
    if selected_outcome != "All":

        filtered_df = filtered_df[
            filtered_df["outcome_label"]
            == selected_outcome
        ]

    # Search
    if search_text:

        search_text_lower = (
            search_text
            .strip()
            .lower()
        )

        patient_id_mask = (
            filtered_df["patient_id"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_text_lower,
                na=False,
            )
        )

        name_mask = (
            filtered_df["name"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_text_lower,
                na=False,
            )
        )

        filtered_df = filtered_df[
            patient_id_mask
            | name_mask
        ]


    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    st.caption(
        f"Showing {len(filtered_df)} "
        f"of {len(df_display)} records"
    )


    # -----------------------------------------------------
    # DOWNLOAD BUTTON
    # -----------------------------------------------------

    csv = (
        filtered_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        label="Download Filtered Demo CSV",
        data=csv,
        file_name="filtered_demo_patient_records.csv",
        mime="text/csv",
    )


    # -----------------------------------------------------
    # PATIENT TABLE
    # -----------------------------------------------------

    section_header(
        "Patient Table",
        icon=None,
    )

    # Keep table cleaner for display
    display_columns = [
        "patient_id",
        "name",
        "age",
        "gender_label",
        "adm_vas",
        "dis_vas",
        "qol_pre_total",
        "qol_post_total",
        "outcome_label",
    ]

    display_columns = [
        column
        for column in display_columns
        if column in filtered_df.columns
    ]

    table_df = (
        filtered_df[
            display_columns
        ]
        .copy()
    )

    table_df = table_df.rename(
        columns={
            "patient_id": "Patient ID",
            "name": "Name",
            "age": "Age",
            "gender_label": "Gender",
            "adm_vas": "Admission VAS",
            "dis_vas": "Discharge VAS",
            "qol_pre_total": "Admission QoL",
            "qol_post_total": "Discharge QoL",
            "outcome_label": "QoL Outcome",
        }
    )

    if selected_age is not None:

        age_key = (
            f"{selected_age[0]}_"
            f"{selected_age[1]}"
        )

    else:
        age_key = "all"

    table_key = (
        f"patient_table_"
        f"{selected_gender}_"
        f"{age_key}_"
        f"{selected_outcome}_"
        f"{search_text}"
    )

    event = st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key=table_key,
    )


    # -----------------------------------------------------
    # SELECTED PATIENT DETAILS
    # -----------------------------------------------------

    selected_rows = (
        event.selection["rows"]
    )

    if selected_rows:

        selected_idx = (
            selected_rows[0]
        )

        # IMPORTANT:
        # use original filtered_df, not table_df,
        # so all patient features remain available.
        patient = (
            filtered_df
            .iloc[selected_idx]
        )

        st.markdown("---")

        section_header(
            "Selected Patient Details",
            icon=None,
        )


        # -------------------------------------------------
        # PATIENT SUMMARY
        # -------------------------------------------------

        img_col, info_col1, info_col2, info_col3 = (
            st.columns(
                [
                    1.2,
                    2,
                    2,
                    3,
                ]
            )
        )

        with img_col:

            st.image(
                "assets/profilepic_placeholder.png",
                width=200,
            )

        with info_col1:

            st.markdown(
                f"**Patient ID:** "
                f"{patient['patient_id']}"
            )

            st.markdown(
                f"**Name:** "
                f"{patient['name']}"
            )

            st.markdown(
                f"**Gender:** "
                f"{patient['gender_label']}"
            )

        with info_col2:

            st.markdown(
                f"**Age:** "
                f"{display_value(patient['age'])}"
            )

            st.markdown(
                f"**Admission VAS:** "
                f"{display_value(patient['adm_vas'])}"
            )

            st.markdown(
                f"**Discharge VAS:** "
                f"{display_value(patient['dis_vas'])}"
            )

        with info_col3:

            qol_pre = display_value(
                patient["qol_pre_total"]
            )

            qol_post = display_value(
                patient["qol_post_total"]
            )

            label_value = (
                patient["outcome_label"]
            )

            patient_summary_cards(
                qol_pre=qol_pre,
                qol_post=qol_post,
                label=label_value,
            )


        # =================================================
        # ADMISSION EQ-5D SCORES
        # =================================================

        st.markdown("")

        st.markdown(
            "#### Admission QoL Dimension Scores"
        )

        admission_cols = st.columns(5)

        with admission_cols[0]:

            st.metric(
                "Mobility",
                display_value(
                    patient["adm_mobility"]
                ),
            )

        with admission_cols[1]:

            st.metric(
                "Personal Care",
                display_value(
                    patient[
                        "adm_personal_care"
                    ]
                ),
            )

        with admission_cols[2]:

            st.metric(
                "Normal Activity",
                display_value(
                    patient[
                        "adm_normal_activity"
                    ]
                ),
            )

        with admission_cols[3]:

            st.metric(
                "Pain / Discomfort",
                display_value(
                    patient[
                        "adm_pain_uncomfort"
                    ]
                ),
            )

        with admission_cols[4]:

            st.metric(
                "Anxiety / Depression",
                display_value(
                    patient[
                        "adm_anxiety_depress"
                    ]
                ),
            )


        # =================================================
        # DISCHARGE EQ-5D SCORES
        # =================================================

        st.markdown("")

        st.markdown(
            "#### Discharge QoL Dimension Scores"
        )

        if patient["outcome_label"] == "Pending Discharge":

            st.info(
                "This patient has not yet been discharged. "
                "Discharge QoL scores are not available."
            )

        else:

            discharge_cols = st.columns(5)

            with discharge_cols[0]:

                st.metric(
                    "Mobility",
                    display_value(
                        patient[
                            "dis_mobility"
                        ]
                    ),
                )

            with discharge_cols[1]:

                st.metric(
                    "Personal Care",
                    display_value(
                        patient[
                            "dis_personal_care"
                        ]
                    ),
                )

            with discharge_cols[2]:

                st.metric(
                    "Normal Activity",
                    display_value(
                        patient[
                            "dis_normal_activity"
                        ]
                    ),
                )

            with discharge_cols[3]:

                st.metric(
                    "Pain / Discomfort",
                    display_value(
                        patient[
                            "dis_pain_uncomfort"
                        ]
                    ),
                )

            with discharge_cols[4]:

                st.metric(
                    "Anxiety / Depression",
                    display_value(
                        patient[
                            "dis_anxiety_depress"
                        ]
                    ),
                )

    else:

        st.info(
            "Click one patient row in the table above "
            "to view detailed information."
        )


# =========================================================
# RUN PATIENT DETAILS
# =========================================================

patient_details_section(df)