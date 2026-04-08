import json
from pathlib import Path

def load_feature_explanations():
    file_path = Path("data/features_explanations.json")

    if not file_path.exists():
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)