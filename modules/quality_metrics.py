
def calculate_quality_metrics(df):

    total_products = len(df)

    defective_products = (
        df["inspection_status"] == "Defective"
    ).sum()

    good_products = (
        df["inspection_status"] == "Good"
    ).sum()

    defect_rate = (
        defective_products / total_products
    ) * 100 if total_products > 0 else 0

    acceptance_rate = (
        good_products / total_products
    ) * 100 if total_products > 0 else 0

    return {
        "total_products": total_products,
        "defective_products": int(defective_products),
        "good_products": int(good_products),
        "defect_rate": round(defect_rate, 2),
        "acceptance_rate": round(acceptance_rate, 2)
    }
