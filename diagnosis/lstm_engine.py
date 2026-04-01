import os
import sys
import torch
import numpy as np
import joblib
import json

# Import the model architecture
models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
sys.path.append(models_dir)
from train_lstm import BiomechanicalLSTM

class LSTMEngine:
    def __init__(self, exercise="squat", 
                 model_path="models/squat_expert_model.pth", 
                 scaler_path="models/scaler.pkl", 
                 label_map_path="models/squat_label_map.json"):
        
        self.exercise = exercise
        
        if not os.path.exists(model_path):
            print(f"[Warning] Deep learning weights not found at {model_path}.")
            self.ready = False
            return
            
        print("🧠 Booting up BiLSTM Diagnostic Subsystem...")
        
        # 1. Load Scaler
        self.scaler = joblib.load(scaler_path)
        
        # 2. Load Label Map
        with open(label_map_path, 'r') as f:
            # json saves keys as strings; convert explicitly back to int
            self.label_map = {int(k): v for k, v in json.load(f).items()}
            
        # 3. Initialize PyTorch Structural Topology
        input_size = 9
        hidden_size = 128
        num_classes = len(self.label_map)
        
        self.model = BiomechanicalLSTM(input_size, hidden_size, num_classes, num_layers=3)
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        
        # Set to Evaluation mode (disables dropout layers to make predictions deterministic)
        self.model.eval() 
        self.ready = True
        
    def analyze(self, sequence_array):
        """
        Receives a (30, 9) numpy matrix from the TemporalBuffer and executes 
        a single rapid dense forward-pass to evaluate posture.
        Returns a list of active errors found by the neural network.
        """
        errors = []
        if not self.ready or sequence_array is None:
            return {"errors": errors}
            
        # 1. Normalize live tracking data using trained scaler
        scaled_seq = self.scaler.transform(sequence_array)
        
        # 2. Add batch dimension: changes shape from (30, 9) -> (1, 30, 9)
        tensor_seq = torch.FloatTensor(scaled_seq).unsqueeze(0)
        
        # 3. Model Inference Execution!
        with torch.no_grad():
            outputs = self.model(tensor_seq)
            # Find the highest probability class
            _, predicted = torch.max(outputs.data, 1)
            
            class_idx = predicted.item()
            label_string = self.label_map[class_idx]
            
        # 4. Neural Network Mapping
        if label_string == "forward_lean_error":
            errors.append({"type": "forward_lean", "severity": 0.9})
        elif label_string == "knee_caving_error":
            errors.append({"type": "imbalance", "severity": 0.95}) 
            # (imbalance maps well to lunge/squat symmetry alerts)

        return {"errors": errors}