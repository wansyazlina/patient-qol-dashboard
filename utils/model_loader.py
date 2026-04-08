import json
import joblib
import pandas as pd
import streamlit as st

@st.cache_resource
def load_model():
    return joblib.load("models/rf_model.pkl")

@st.cache_resource
def load_label_encoder():
    return joblib.load("models/label_encoder.pkl")

@st.cache_data
def load_feature_columns():
    with open("data/feature_columns.json", "r") as f:
        return json.load(f)

@st.cache_data
def load_shap_background():
    return pd.read_csv("explainers/shap_background.csv")

@st.cache_data
def load_lime_train_sample():
    return pd.read_csv("explainers/lime_train_sample.csv")