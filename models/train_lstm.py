import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import json
import os

# -----------------------------------------
# Neural Network Architecture (LSTM)
# -----------------------------------------
class BiomechanicalLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes, num_layers=2):
        super(BiomechanicalLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # The LSTM layer takes [batch_size, sequence_length, features]
        # UPGRADE: Added bidirectional=True. It now looks forward AND backward in time,
        # which is crucial for identifying the "apex" of a squat or lean.
        self.lstm = nn.LSTM(
            input_size, 
            hidden_size, 
            num_layers, 
            batch_first=True, 
            dropout=0.3, # Increased dropout slightly to prevent overfitting 
            bidirectional=True
        )
        
        # Fully connected layer to map LSTM output to our classes
        # UPGRADE: Multiply hidden_size by 2 because it's bidirectional
        self.fc = nn.Linear(hidden_size * 2, num_classes)
        
    def forward(self, x):
        # Initialize hidden state and cell state with zeros
        # UPGRADE: Multiply num_layers by 2 because of bidirectional
        h0 = torch.zeros(self.num_layers * 2, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers * 2, x.size(0), self.hidden_size).to(x.device)
        
        # Forward propagate LSTM
        # out shape: (batch, seq_len, hidden_size * 2)
        out, _ = self.lstm(x, (h0, c0))
        
        # We only care about the output of the LAST timestep in the sequence
        out = out[:, -1, :] 
        
        # Decode into our classes
        out = self.fc(out)
        return out


# -----------------------------------------
# Data Processing pipeline
# -----------------------------------------
def create_sequences(data, labels, seq_length=30):
    """
    Converts flat rows into sliding windows of time.
    Why? Because an LSTM needs to look at a 1-second 'wave' of motion, not a static photo.
    """
    xs, ys = [], []
    # We step by 5 frames (very high overlap) to generate way more sequence data
    for i in range(0, len(data) - seq_length, 5):
        window = data[i:i+seq_length]
        window_labels = labels[i:i+seq_length]
        
        # Instead of throwing away data that transitions, we label the sequence 
        # based on the most frequent label within this 1-second window
        # (This better mimics real-world fuzzy transitions)
        modes = pd.Series(window_labels).mode()
        majority_label = modes[0] if not modes.empty else window_labels[-1]
        
        xs.append(window)
        ys.append(majority_label)
            
    return np.array(xs), np.array(ys)


def train_model():
    print("="*50)
    print("🧠 OrthoSense Clinical AI: LSTM Training Engine")
    print("="*50)

    csv_path = "data_pipeline/clinical_dataset.csv"
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}. Please run dataset generation first.")
        return

    # 1. Load Data
    print("Loading mathematical dataset...")
    df = pd.read_csv(csv_path)
    
    # --- FEATURE ENGINEERING ---
    print("Engineering dynamic temporal features...")
    # 1. Angular Velocities (rate of change between frames - helps model understand movement direction)
    df['left_knee_vel'] = df['left_knee_angle'].diff().fillna(0)
    df['right_knee_vel'] = df['right_knee_angle'].diff().fillna(0)
    df['back_vel'] = df['back_angle'].diff().fillna(0)
    
    # 2. Moving Averages (Smooths out jitter/noise from MediaPipe)
    df['left_knee_smooth'] = df['left_knee_angle'].rolling(window=5, min_periods=1).mean()
    df['back_smooth'] = df['back_angle'].rolling(window=5, min_periods=1).mean()

    # Expanded Feature Suite (from 4 up to 9 features)
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
    
    # Save the encoder map so the live app knows what 0,1,2 mean!
    label_map = {int(i): str(l) for i, l in enumerate(le.classes_)}
    with open("models/squat_label_map.json", "w") as f:
        json.dump(label_map, f)
    print(f"Detected Classes: {label_map}")

    # 3. Normalize Features
    # (Deep learning models learn much faster if angles shrink from 0-180 down to -1 to +1)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # 4. Create Temporal Sequences (30 frames = 1 second of motion)
    print("Converting flat data into 3D Temporal Streams...")
    seq_length = 30
    X_seq, y_seq = create_sequences(X_scaled, y_encoded, seq_length)
    print(f"Generated {len(X_seq)} motion sequences of {seq_length} frames each.")

    # 5. Split Dataset into Training & Testing
    X_train, X_test, y_train, y_test = train_test_split(X_seq, y_seq, test_size=0.2, random_state=42)
    
    # Convert numpy arrays to PyTorch Tensors
    X_train_t = torch.FloatTensor(X_train)
    y_train_t = torch.LongTensor(y_train)
    X_test_t = torch.FloatTensor(X_test)
    y_test_t = torch.LongTensor(y_test)

    # 6. Build the Neural Network Matrix
    input_size = len(features)  # 4 features we extract
    hidden_size = 128           # Increased neurons for deeper understanding
    num_classes = len(label_map)
    
    # 3 Layers to learn complex temporal patterns
    model = BiomechanicalLSTM(input_size, hidden_size, num_classes, num_layers=3)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.002) # Boosted Learning Rate
    
    # 7. The Core Training Loop
    epochs = 600 # Run a deeper training cycle
    print("\n🚀 Initiating Deep Learning Subroutine (Training on CPU)...")
    
    # UPGRADE: Learning Rate Scheduler (Lowers the learning rate when validation accuracy plateaus)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=30)
    
    best_accuracy = 0.0
    os.makedirs("models", exist_ok=True)
    model_path = "models/squat_expert_model.pth"

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        # UPGRADE: Data Augmentation
        # We add slight mathematical "noise" to the training data. This simulates jittery
        # cameras, different body proportions, and forces the model to learn the true movement
        # rather than just memorizing the exact numbers in the dataset.
        noise = torch.randn_like(X_train_t) * 0.05
        noisy_X_train = X_train_t + noise
        
        # Forward pass on augmented data
        outputs = model(noisy_X_train)
        loss = criterion(outputs, y_train_t)
        
        # Backward pass & Math Adjustment
        loss.backward()
        optimizer.step()
        
        if (epoch+1) % 20 == 0:
            # Test accuracy every 20 epochs
            model.eval()
            with torch.no_grad():
                test_outputs = model(X_test_t)
                _, predicted = torch.max(test_outputs.data, 1)
                accuracy = (predicted == y_test_t).sum().item() / y_test_t.size(0) * 100
                print(f"Epoch [{epoch+1}/{epochs}] | Loss: {loss.item():.4f} | Validation Accuracy: {accuracy:.2f}%")
                
                # Step the scheduler based on accuracy
                scheduler.step(accuracy)
                
                # UPGRADE: Early Stopping / Best Model Checkpoint
                # Only save the brain if it's the smartest one we've seen so far
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    torch.save(model.state_dict(), model_path)
                    print(f"   🌟 New High Score! Checkpointed Model at {best_accuracy:.2f}% accuracy.")

    print("\n✅ TRAINING COMPLETE!")
    print(f"Highest Model Benchmark Achieved: {best_accuracy:.2f}%")
    print(f"Clinical AI weights saved to: {model_path}")
    print("OrthoSense is now ready to use this cognitive brain in real-time.")

if __name__ == "__main__":
    train_model()
