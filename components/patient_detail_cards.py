import streamlit as st


def get_status_colors(label_value):
    label_value = str(label_value).strip().lower()

    if label_value == "decline":
        return {
            "accent": "#ef4444",
            "bg": "rgba(239, 68, 68, 0.12)",
            "text": "#b91c1c",
            "display": "Decline"
        }
    elif label_value == "no_decline":
        return {
            "accent": "#22c55e",
            "bg": "rgba(34, 197, 94, 0.12)",
            "text": "#166534",
            "display": "No Decline"
        }
    else:
        return {
            "accent": "#6b7280",
            "bg": "rgba(107, 114, 128, 0.12)",
            "text": "#374151",
            "display": str(label_value).title()
        }


def get_qol_colors(score):
    try:
        score = float(score)
        if score <= 7:
            return {"accent": "#22c55e", "text": "#166534"}
        elif score <= 12:
            return {"accent": "#f59e0b", "text": "#92400e"}
        else:
            return {"accent": "#ef4444", "text": "#b91c1c"}
    except Exception:
        return {"accent": "#6b7280", "text": "#374151"}


def render_summary_item(title, value, colors, icon=""):
    value = str(value)

    html = f"""
<div style="border-left:5px solid {colors['accent']}; padding-left:14px; margin-bottom:18px;">
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px; font-family:'Space Grotesk', sans-serif; font-size:1.05rem; font-weight:700; color:#1f2937;">
        <span style="font-size:1.1rem;">{icon}</span>
        <span>{title}</span>
    </div>
    <span style="display:block; font-family:'Space Grotesk', sans-serif; font-size:1.8rem; font-weight:700; color:{colors['text']}; line-height:1.1; margin-left:2px;">{value}</span>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def render_label_badge(label_value):
    colors = get_status_colors(label_value)

    html = f"""
<div style="border-left:5px solid {colors['accent']}; padding-left:14px; margin-bottom:18px;">
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px; font-family:'Space Grotesk', sans-serif; font-size:1.05rem; font-weight:700; color:#1f2937;">
        <span style="font-size:1.1rem;">📊</span>
        <span>Outcome Label</span>
    </div>
    <span style="display:inline-block; padding:10px 18px; border-radius:999px; background:{colors['bg']}; color:{colors['text']}; font-family:'Space Grotesk', sans-serif; font-size:1rem; font-weight:700; border:1px solid {colors['accent']}; box-shadow:0 2px 8px rgba(0,0,0,0.04);">{colors['display']}</span>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

def patient_summary_cards(qol_pre, qol_post, label):
    pre_colors = get_qol_colors(qol_pre)
    post_colors = get_qol_colors(qol_post)

    render_summary_item("Overall Admission QoL Score", qol_pre, pre_colors, icon="🫀")
    render_summary_item("Overall Discharge QoL Score", qol_post, post_colors, icon="❤️")
    render_label_badge(label)