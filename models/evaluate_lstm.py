import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import json
import os

# Import the model architecture directly from training script
from train_lstm import BiomechanicalLSTM, create_sequences

def evaluate_model():
    print("="*50)
    print("🧪 OrthoSense Model Evaluation Tool")
    print("="*50)

    csv_path = "../data_pipeline/clinical_dataset.csv"  # Relative to where we run it, assuming from root it's just data_pipeline/... wait, let's make it robust
    
    # Actually, we should run this from root, so path is data_pipeline/clinical_dataset.csv
    csv_path = "data_pipeline/clinical_dataset.csv"
    model_path = "models/squat_expert_model.pth"
    
    if not os.path.exists(csv_path) or not os.path.exists(model_path):
        print("Error: Missing dataset or trained model weights.")
        return

    print("Loading data & computing features...")
    df = pd.read_csv(csv_path)
    
    # 1. Feature Engineering matching training
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
    
    # Encode
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_raw)
    
    # Scale
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    
    # Sequence creation
    X_seq, y_seq = create_sequences(X_scaled, y_encoded, seq_length=30)
    
    # Split using the exact same random state to get the exact test set
    _, X_test, _, y_test = train_test_split(X_seq, y_seq, test_size=0.2, random_state=42)
    
    X_test_t = torch.FloatTensor(X_test)
    y_test_t = torch.LongTensor(y_test)
    
    # Determine dimensions
    input_size = len(features)
    hidden_size = 128
    num_classes = len(np.unique(y_encoded))
    
    # Initialize and load model
    print("\nLoading BiLSTM weights...")
    model = BiomechanicalLSTM(input_size, hidden_size, num_classes, num_layers=3)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()  # Set to evaluation mode!
    
    # Run Inference
    print("\nAnalyzing test dataset...")
    with torch.no_grad():
        outputs = model(X_test_t)
        _, predicted = torch.max(outputs.data, 1)
        
        y_true = y_test_t.numpy()
        y_pred = predicted.numpy()
        
    target_names = le.classes_
    
    print("\n📊 Evaluation Results:")
    print(classification_report(y_true, y_pred, target_names=target_names))
    
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    print("\nConfusion Matrix:")
    print(target_names)
    print(cm)
    
    # Display accuracy manually
    correct = (y_pred == y_true).sum()
    total = len(y_true)
    print(f"\nFinal Test Accuracy: {(correct/total)*100:.2f}% ({correct}/{total} sequences)")

if __name__ == "__main__":
    evaluate_model()
