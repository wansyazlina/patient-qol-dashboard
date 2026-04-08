import streamlit as st

def section_header(title, icon="insights"):
    icon_html = ""

    if icon is not None:
        icon_html = f"""
        <span class="material-icons" style="font-size: 25px; opacity: 0.8; margin: 0">{icon}</span>
        """
    st.markdown(f"""
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        
        <div style="margin-top: 20px;">
            <h4 style="margin: 0;padding: 0;
                font-family: 'Space Grotesk', sans-serif;
                line-height: 1.2;
                display: flex;
                align-items: center;
                gap: 8px;">{icon_html}{title}</h4>
            <hr style="border:none; border-top:3px solid rgba(0,0,0,0.08); margin-top:5px;">
        </div>
    """, unsafe_allow_html=True)


def colored_card(title, value, color):
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}, #00000010);
        padding: 20px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
        margin-bottom: 20px;  /* 👈 THIS ADDS SPACE */
    ">
        <p style="margin:0; font-size:14px; opacity:0.8;">{title}</p>
        <h2 style="margin:5px 0 0 0; font-family: 'Space Grotesk', sans-serif; ">{value}</h2>
    </div>
    """, unsafe_allow_html=True)

def colored_border_card(title, value, bg_color, accent_color):
    st.markdown(f"""
    <div style="
        background-color: {bg_color};
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.06);
        margin-bottom: 30px;  /* 👈 THIS ADDS SPACE */
        font-family: 'Space Mono', monospace;
    ">
    <div style="
        height: 4px;
        background-color: {accent_color};
        border-radius: 4px 4px 0 0;
        margin: -20px -20px 15px -20px;
    "></div>

    <p style="margin:0; font-size:14px; color:#555;">
        {title}
    </p>

    <h2 style="
        margin:5px 0 0 0;
        color:#111;
        font-family: 'Space Grotesk', sans-serif;
    ">{value}</h2>
    </div>
    """, unsafe_allow_html=True)

def metric_cards(total_records, total_male, total_female, average_age, total_decline):
    st.markdown("""
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        .metric-card {
            background-color: white;
            padding: 18px 20px;
            border-radius: 18px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 1px solid rgba(0,0,0,0.06);
            min-height: 120px;
        }

        .metric-label {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.95rem;
            color: #555;
            margin-bottom: 8px;
        }

        .metric-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2rem;
            font-weight: 700;
            color: #111;
            line-height: 1.1;
        }

        .metric-subtext {
            font-family: 'Space Mono', monospace;
            font-size: 0.85rem;
            color: #666;
            margin-top: 6px;
        }

        .gender-wrap {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-top: 6px;
            flex-wrap: wrap;
        }

        .gender-chip {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 10px;
            border-radius: 999px;
            font-family: 'Space Mono', monospace;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .male-chip {
            background-color: rgba(59,130,246,0.12);
            color: #2563eb;
        }

        .female-chip {
            background-color: rgba(236,72,153,0.12);
            color: #db2777;
        }

        .material-icons.metric-icon {
            font-size: 20px;
            vertical-align: middle;
            margin-right: 6px;
            color: #666;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">
                <span class="material-icons metric-icon">folder_open</span>
                Total Records
            </div>
            <div class="metric-value">{total_records}</div>
            <div class="metric-subtext">Patient entries available</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">
                <span class="material-icons metric-icon">groups</span>
                Gender Distribution
            </div>
            <div class="gender-wrap">
                <div class="gender-chip male-chip">♂ Male: {total_male}</div>
                <div class="gender-chip female-chip">♀ Female: {total_female}</div>
            </div>
            <div class="metric-subtext">Combined patient sex count</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">
                <span class="material-icons metric-icon">calendar_today</span>
                Average Age
            </div>
            <div class="metric-value">{average_age:.1f}</div>
            <div class="metric-subtext">Mean age of patients</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">
                <span class="material-icons metric-icon">monitor_heart</span>
                Total Decline Cases
            </div>
            <div class="metric-value">{total_decline}</div>
            <div class="metric-subtext">Patients with QoL decline</div>
        </div>
        """, unsafe_allow_html=True)