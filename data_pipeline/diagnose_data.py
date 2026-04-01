import pandas as pd
import numpy as np

df = pd.read_csv("data_pipeline/clinical_dataset.csv")

print("=== Dataset Shape ===")
print(f"Total rows: {len(df)}")
print(f"\n=== Label Distribution ===")
print(df['label'].value_counts())

print(f"\n=== Feature Statistics Per Class ===")
for label in df['label'].unique():
    subset = df[df['label'] == label]
    print(f"\n--- {label} ({len(subset)} rows) ---")
    for col in ['left_knee_angle', 'right_knee_angle', 'back_angle', 'symmetry_score']:
        print(f"  {col:>20s}: mean={subset[col].mean():.1f}  std={subset[col].std():.1f}  min={subset[col].min():.1f}  max={subset[col].max():.1f}")

print(f"\n=== Class Means Comparison ===")
print(df.groupby('label')[['left_knee_angle', 'right_knee_angle', 'back_angle', 'symmetry_score']].mean().round(1))
