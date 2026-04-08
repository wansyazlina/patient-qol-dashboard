FEATURE_GUIDANCE = {
    "adm_mobility": {
        "display_name": "Mobility",
        "description": "Shows how much difficulty the patient has with walking or moving around at admission.",
        "clinical_note": "Higher values may indicate poorer physical function and may contribute to a higher risk of QoL decline.",
        "high_recommendation": "Consider mobility support, physiotherapy review, fall-risk assessment, and closer monitoring of physical function.",
        "low_recommendation": "Mobility appears relatively preserved. Encourage continued safe movement and routine functional monitoring."
    },
    "adm_personal_care": {
        "display_name": "Personal Care",
        "description": "Reflects the patient's ability to wash and dress independently at admission.",
        "clinical_note": "Higher impairment may suggest reduced independence and greater care needs.",
        "high_recommendation": "Consider nursing support, occupational therapy input, and assessment of daily living assistance needs.",
        "low_recommendation": "Personal care ability appears relatively maintained. Continue encouraging independence where appropriate."
    },
    "adm_normal_activity": {
        "display_name": "Normal Activity",
        "description": "Measures difficulty in performing usual daily activities such as work, study, or housework.",
        "clinical_note": "Greater limitation can indicate reduced day-to-day functioning.",
        "high_recommendation": "Review functional limitations, activity tolerance, and possible rehabilitation planning to support daily living.",
        "low_recommendation": "Daily activity function appears less impaired. Maintain activity participation as clinically appropriate."
    },
    "adm_pain_uncomfort": {
        "display_name": "Pain & Discomfort",
        "description": "Represents the patient's pain or physical discomfort level at admission.",
        "clinical_note": "Higher pain burden may worsen quality of life and recovery potential.",
        "high_recommendation": "Consider pain review, symptom management, medication optimization, and follow-up on comfort-related concerns.",
        "low_recommendation": "Pain burden appears relatively low. Continue monitoring for symptom changes."
    },
    "adm_anxiety_depress": {
        "display_name": "Anxiety / Depression",
        "description": "Captures emotional distress such as anxiety or depressive symptoms at admission.",
        "clinical_note": "Psychological distress can strongly affect perceived quality of life.",
        "high_recommendation": "Consider emotional support, mental health screening, counseling referral, and closer psychosocial follow-up.",
        "low_recommendation": "Psychological distress appears lower at this time. Continue supportive monitoring."
    },
    "adm_vas": {
        "display_name": "Admission VAS Score",
        "description": "The patient's self-rated health score at admission using the visual analogue scale.",
        "clinical_note": "Lower perceived health may reflect a more vulnerable condition.",
        "high_recommendation": "A higher self-rated health score is generally encouraging. Maintain current supportive care and monitor for changes.",
        "low_recommendation": "A lower self-rated health score may indicate vulnerability. Consider reviewing symptom burden, function, and patient concerns more closely."
    },
    "age": {
        "display_name": "Age",
        "description": "The patient's age in years.",
        "clinical_note": "Age may influence recovery pattern, resilience, and functional status.",
        "high_recommendation": "For older patients, consider closer monitoring of frailty, function, and recovery support needs.",
        "low_recommendation": "Younger age may be associated with greater resilience, but interpretation should still be guided by the full clinical picture."
    },
    "qol_pre_total": {
        "display_name": "Baseline QoL Score",
        "description": "The total admission quality-of-life score before discharge outcome is known.",
        "clinical_note": "Poorer baseline QoL may be linked to higher risk of adverse outcome.",
        "high_recommendation": "A higher baseline QoL burden may justify closer monitoring and earlier supportive intervention.",
        "low_recommendation": "A lower baseline QoL burden may be somewhat reassuring, though other factors still matter."
    },
    "gender": {
        "display_name": "Gender",
        "description": "Encoded gender variable used by the model.",
        "clinical_note": "This is a demographic feature and should be interpreted carefully.",
        "high_recommendation": "Interpret demographic effects cautiously. Gender should not be used alone for clinical decision-making.",
        "low_recommendation": "Interpret demographic effects cautiously. Gender should not be used alone for clinical decision-making."
    },
    "adm_total_burden": {
        "display_name": "Total Burden",
        "description": "Combined burden across the five admission EQ-5D dimensions.",
        "clinical_note": "Higher total burden reflects broader overall health difficulties.",
        "high_recommendation": "A high total burden suggests multidimensional needs. Consider broader multidisciplinary review.",
        "low_recommendation": "A lower total burden is relatively reassuring. Continue routine monitoring."
    },
    "adm_function_score": {
        "display_name": "Function Score",
        "description": "Combined score based on mobility, personal care, and normal activity.",
        "clinical_note": "Higher values suggest greater functional impairment.",
        "high_recommendation": "Consider functional rehabilitation planning and review of independence in daily living.",
        "low_recommendation": "Function score appears relatively favorable. Support maintenance of current functional ability."
    },
    "adm_distress_score": {
        "display_name": "Distress Score",
        "description": "Combined score based on pain/discomfort and anxiety/depression.",
        "clinical_note": "Higher values suggest greater physical and emotional distress.",
        "high_recommendation": "Consider integrated symptom and psychosocial support to address distress.",
        "low_recommendation": "Distress score appears lower, which may be protective. Continue supportive observation."
    },
    "adm_problem_count": {
        "display_name": "Problem Count",
        "description": "Counts how many admission QoL domains show problems.",
        "clinical_note": "A higher count suggests more dimensions of health are affected.",
        "high_recommendation": "A high problem count may indicate broader complexity. Consider more holistic assessment and follow-up.",
        "low_recommendation": "A lower problem count may indicate fewer affected domains. Continue monitoring for change."
    },
    "adm_severe_count": {
        "display_name": "Severe Problem Count",
        "description": "Counts how many admission QoL domains are in the severe range.",
        "clinical_note": "More severe problems may indicate a more fragile clinical state.",
        "high_recommendation": "A higher severe problem count may justify intensified support and closer review.",
        "low_recommendation": "A lower severe problem count is relatively reassuring, though not sufficient on its own."
    },
    "vas_gap": {
        "display_name": "VAS Gap",
        "description": "Represents a derived gap measure related to the VAS score used in the model.",
        "clinical_note": "This feature should be interpreted based on how it was engineered in your pipeline.",
        "high_recommendation": "Interpret this derived feature using your feature engineering definition. Review whether a larger gap suggests mismatch or higher vulnerability.",
        "low_recommendation": "Interpret this derived feature using your feature engineering definition. A smaller gap may be relatively reassuring depending on your pipeline logic."
    }
}