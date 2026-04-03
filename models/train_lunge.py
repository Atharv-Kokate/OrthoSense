import os
import sys
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import json
import joblib

# Re-use the existing BiomechanicalLSTM from train_lstm
from train_lstm import BiomechanicalLSTM, create_sequences

def train_lunge_model():
    print("="*50)
    print("🧠 OrthoSense Clinical AI: LSTM Lunge Training Engine")
    print("="*50)

    csv_path = "../data_pipeline/lunge_dataset_augmented.csv"
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}. Run augmentation first.")
        return

    # 1. Load Data
    print("Loading mathematical dataset...")
    df = pd.read_csv(csv_path)

    # --- FEATURE ENGINEERING ---
    print("Engineering dynamic temporal features...")
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

    # 2. Encode Labels (Text -> Integers)
    print("Encoding diagnostic labels...")
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_raw)
    
    label_map = {int(index): label for index, label in enumerate(le.classes_)}
    with open('lunge_label_map.json', 'w') as f:
        json.dump(label_map, f)
    print(f"Detected Classes: {label_map}")

    # 3. Create Sequential Windows
    print("Slicing motion capture data into 1-second contiguous blocks...")
    SEQ_LENGTH = 30
    X_seq, y_seq = create_sequences(X_raw, y_encoded, seq_length=SEQ_LENGTH)
    print(f"Extracted {len(X_seq)} movement sequences.")

    # 4. Standardize Data
    print("Calibrating robust StandardScaler geometry...")
    num_samples, seq_len, num_features = X_seq.shape
    X_flattened = X_seq.reshape(-1, num_features)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_flattened)
    X_seq_scaled = X_scaled.reshape(num_samples, seq_len, num_features)

    joblib.dump(scaler, 'lunge_scaler.pkl')

    # 5. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_seq_scaled, y_seq, test_size=0.2, random_state=42)

    # 6. PyTorch Tensors
    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.LongTensor(y_train)
    X_test_tensor = torch.FloatTensor(X_test)
    y_test_tensor = torch.LongTensor(y_test)

    # 7. Initialize Subsystem Model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Deploying Neural Network architecture onto: {device}")
    
    num_classes = len(label_map)
    model = BiomechanicalLSTM(input_size=len(features), hidden_size=128, num_classes=num_classes, num_layers=3).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.002, weight_decay=1e-5)

    # 8. Training Loop
    epochs = 15  # Keep it quick for development
    batch_size = 64
    train_dataset = torch.utils.data.TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)

    print("Beginning Gradient Descent Optimization Strategy...")
    model.train()
    for epoch in range(epochs):
        epoch_loss = 0
        correct = 0
        total = 0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()

        accuracy = 100 * correct / total
        print(f"Epoch [{epoch+1}/{epochs}] | Loss: {epoch_loss/len(train_loader):.4f} | Accuracy: {accuracy:.2f}%")

    print("\nTraining Complete! Saving Expert Systems Core...")
    torch.save(model.state_dict(), 'lunge_expert_model.pth')
    print("-> Lunge weights exported successfully.")

if __name__ == "__main__":
    train_lunge_model()
