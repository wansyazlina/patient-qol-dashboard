import base64
from pathlib import Path


FEATURE_ICONS = {

    # Overall QoL
    "qol_pre_total":
        "assets/feature_icons/DATA.svg",

    # Burden / symptom load
    "adm_total_burden":
        "assets/feature_icons/gender.svg",

    # Functional ability
    "adm_function_score":
        "assets/feature_icons/mobility.svg",

    # Demographics
    "age":
        "assets/feature_icons/age.svg",

    "gender":
        "assets/feature_icons/gender.svg",

    # Daily activities
    "adm_normal_activity":
        "assets/feature_icons/mobility.svg",

    # Number of reported problems
    "adm_problem_count":
        "assets/feature_icons/pain.svg",

    # Mobility
    "adm_mobility":
        "assets/feature_icons/pain.svg",

    # Difference / change in VAS
    "vas_gap":
        "assets/feature_icons/pain.svg",

    # Distress
    "adm_distress_score":
        "assets/feature_icons/age.svg",

    # VAS health score
    "adm_vas":
        "assets/feature_icons/Data.svg",

    # Severe symptom count
    "adm_severe_count":
        "assets/feature_icons/Data.svg",

    # Personal care
    "adm_personal_care":
        "assets/feature_icons/Data.svg",

    # Anxiety / depression
    "adm_anxiety_depress":
        "assets/feature_icons/anxiety.svg",

    # Pain / discomfort
    "adm_pain_uncomfort":
        "assets/feature_icons/pain.svg",
}

def get_icon_base64(icon_path):

    path = Path(icon_path)

    if not path.exists():
        return None

    with open(path, "rb") as image_file:
        encoded = base64.b64encode(
            image_file.read()
        ).decode()

    if path.suffix.lower() == ".svg":
        mime_type = "image/svg+xml"

    elif path.suffix.lower() == ".png":
        mime_type = "image/png"

    else:
        return None

    return f"data:{mime_type};base64,{encoded}"