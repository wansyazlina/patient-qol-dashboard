import streamlit as st

def top_bar(title="QoL Risk Prediction"):

    st.markdown("""
    <style>

    /* Remove default padding */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 0rem !important;
        padding-top: 1.5rem;
    }

    /* Full width header */
    .topbar {
        background-color: #282413;
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        padding: 16px 24px;
    }

    /* Inner content (keeps it aligned nicely) */
    .topbar-inner {
        max-width: 1200px;
        margin: 0 auto;
    }

    .topbar-title {
        color: white;
        font-size: 22px;
        font-weight: 600;
        font-family: 'Space Mono', monospace;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="topbar">
            <div class="topbar-inner">
                <div class="topbar-title">{title}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)