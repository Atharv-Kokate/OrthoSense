import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import json
import os

def export():
    print("Exporting dependencies for real-time inference...")
    
    # 1. Load exact same dataset to fit identical distributions
    df = pd.read_csv("data_pipeline/clinical_dataset.csv")

    # 2. Duplicate exact same feature engineering
    df['left_knee_vel'] = df['left_knee_angle'].diff().fillna(0)
    df['right_knee_vel'] = df['right_knee_angle'].diff().fillna(0)
    df['back_vel'] = df['back_angle'].diff().fillna(0)
    df['left_knee_smooth'] = df['left_knee_angle'].rolling(window=5, min_periods=1).mean()
    df['back_smooth'] = df['back_angle'].rolling(window=5, min_periods=1).mean()

    features = [
        'left_knee_angle', 'right_knee_angle', 'back_angle', 'symmetry_score',
        'left_knee_vel', 'right_knee_vel', 'back_vel', 
        'left_knee_smooth', 'back_smooth'
    ]
    
    X_raw = df[features].values
    y_raw = df['label'].values

    # 3. Fit mathematical standardizer
    scaler = StandardScaler()
    scaler.fit(X_raw)

    # 4. Fit label text-to-integer mappings
    le = LabelEncoder()
    le.fit(y_raw)

    # 5. Save securely to models/ directory
    os.makedirs("models", exist_ok=True)
    joblib.dump(scaler, "models/scaler.pkl")

    label_map = {int(i): str(l) for i, l in enumerate(le.classes_)}
    with open("models/squat_label_map.json", "w") as f:
        json.dump(label_map, f)

    print("✅ Successfully exported `scaler.pkl` and `squat_label_map.json`!")

if __name__ == "__main__":
    export()