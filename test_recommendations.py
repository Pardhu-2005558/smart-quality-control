
import pandas as pd

from modules.quality_recommendations import (
    generate_quality_recommendations
)

df = pd.read_csv("quality_inspection_sample.csv")

recommendations = generate_quality_recommendations(df)

print("\nQUALITY IMPROVEMENT RECOMMENDATIONS\n")

for item in recommendations:

    print("Category:", item["category"])
    print("Finding:", item["finding"])
    print("Recommendation:", item["recommendation"])
    print("Priority:", item["priority"])
    print("-" * 60)
