import json
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report

# -------------------------
# LOAD ARTIFACTS
# -------------------------
model = joblib.load("models/rf_model.pkl")
label_encoder = joblib.load("models/label_encoder.pkl")

with open("data/feature_columns.json", "r") as f:
    feature_columns = json.load(f)

# Load the same test dataset you used in Colab
# Replace this with your actual exported X_test / y_test files
X_test = pd.read_csv("data/X_test.csv")
y_test = pd.read_csv("data/y_test.csv").squeeze()

# force exact column order
X_test = X_test.reindex(columns=feature_columns, fill_value=0)

print("Model classes_:", model.classes_)
print("Label encoder classes_:", label_encoder.classes_)
print("X_test shape:", X_test.shape)
print("First 5 feature columns:", X_test.columns[:5].tolist())

# -------------------------
# DEFAULT PREDICTION
# -------------------------
y_pred_default = model.predict(X_test)

# decode if needed
try:
    y_pred_default_decoded = label_encoder.inverse_transform(y_pred_default)
except Exception:
    y_pred_default_decoded = y_pred_default

# decode y_test if numeric
if pd.api.types.is_numeric_dtype(y_test):
    try:
        y_test_decoded = label_encoder.inverse_transform(y_test.astype(int))
    except Exception:
        y_test_decoded = y_test
else:
    y_test_decoded = y_test

print("\nBalanced RF (Tuned) Accuracy:",
      accuracy_score(y_test_decoded, y_pred_default_decoded))

print(classification_report(
    y_test_decoded,
    y_pred_default_decoded,
    digits=3,
    target_names=label_encoder.classes_
))

# -------------------------
# THRESHOLD PREDICTION
# -------------------------
y_probs = model.predict_proba(X_test)

# IMPORTANT:
# in your Colab, decline is index 0
decline_probs = y_probs[:, 0]

threshold = 0.35

# exactly match Colab logic
y_pred_threshold = label_encoder.inverse_transform(
    np.where(decline_probs > threshold, 0, 1)
)

print("\nBalanced RF (Threshold = 0.35) Accuracy:",
      accuracy_score(y_test_decoded, y_pred_threshold))

print(classification_report(
    y_test_decoded,
    y_pred_threshold,
    digits=3,
    target_names=label_encoder.classes_
))