import csv
from collections import Counter

try:
    with open("data_pipeline/clinical_dataset.csv", 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        label_index = header.index("label")
        
        labels = [row[label_index] for row in reader if len(row) > label_index]
        
    counts = Counter(labels)
    print("Total rows:", len(labels))
    print("--- Label Counts ---")
    for k, v in counts.items():
        print(f"{k}: {v}")
except Exception as e:
    print(f"Error reading CSV: {e}")
