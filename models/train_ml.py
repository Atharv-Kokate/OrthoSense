import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import json
import os

def train_instant_model():
    print("="*50)
    print("🧠 OrthoSense Clinical AI: Machine Learning Engine")
    print("="*50)

    csv_path = "data_pipeline/clinical_dataset.csv"
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}. Please run dataset generation first.")
        return

    # 1. Load Data
    print("Loading mathematical dataset...")
    df = pd.read_csv(csv_path)
    
    features = ['left_knee_angle', 'right_knee_angle', 'back_angle', 'symmetry_score']
    X = df[features].values
    y_raw = df['label'].values
    
    # 2. Encode Labels (Text -> Integers)
    print("Encoding diagnostic labels...")
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    
    # Save the encoder map
    label_map = {int(i): str(l) for i, l in enumerate(le.classes_)}
    os.makedirs("models", exist_ok=True)
    with open("models/squat_label_map.json", "w") as f:
        json.dump(label_map, f)
    print(f"Detected Classes: {label_map}")

    # 3. Split Dataset into Training & Testing
    # We randomize the frames to ensure the model perfectly maps biomechanics without rote memorization
    print("Splitting 5,000+ biomechanical frames into Train/Test subsets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Build the Diagnostic Machine Learning Model
    # A Random Forest maps exact threshold combinations (e.g. knee < 160 AND back > 90) instantaneously
    print("\n🚀 Initiating Clinical Heuristics Engine (Training on CPU)...")
    model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    
    # Train the Brain
    model.fit(X_train, y_train)

    # 5. Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred) * 100
    print(f"\n📊 FINAL VALIDATION ACCURACY: {accuracy:.2f}%\n")
    
    # Breakdown of accuracy by each exact error
    print("--- Clinical Diagnosis Breakdown ---")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # 6. Export the final brain
    model_path = "models/squat_expert_model.pkl"
    joblib.dump(model, model_path)
    
    print("\n✅ TRAINING COMPLETE!")
    print(f"Clinical AI weights saved to: {model_path}")
    print("OrthoSense is now ready to use this instantaneous brain in real-time.")

if __name__ == "__main__":
    train_instant_model()
