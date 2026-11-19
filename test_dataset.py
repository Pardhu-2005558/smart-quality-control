
import pandas as pd

file_path = "quality_inspection_sample.csv"

df = pd.read_csv(file_path)

print("DATASET LOADED SUCCESSFULLY")

print("\nFirst 5 Records:")
print(df.head())

print("\nTotal Products:", len(df))

print("\nInspection Status:")
print(df["inspection_status"].value_counts())

defective = (df["inspection_status"] == "Defective").sum()
good = (df["inspection_status"] == "Good").sum()

defect_rate = (defective / len(df)) * 100

print("\nDefective Products:", defective)
print("Good Products:", good)
print("Defect Rate:", round(defect_rate, 2), "%")
