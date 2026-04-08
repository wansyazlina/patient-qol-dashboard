import numpy as np

def get_feature_value_dict(prediction_result):
    feature_values = prediction_result["feature_values"]
    feature_names = prediction_result["feature_names"]

    if isinstance(feature_values, dict):
        return feature_values

    return dict(zip(feature_names, feature_values))