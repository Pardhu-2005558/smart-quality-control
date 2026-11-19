
import pandas as pd

from modules.machine_analysis import calculate_machine_quality

df = pd.read_csv("quality_inspection_sample.csv")

machine_data, summary = calculate_machine_quality(df)

print("\nMACHINE-WISE QUALITY ANALYSIS\n")

print(machine_data.to_string(index=False))

print("\nSUMMARY\n")

print(summary)
