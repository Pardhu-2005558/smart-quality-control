
def calculate_pareto(df):

    # Consider only defective products
    defective_df = df[
        df["inspection_status"] == "Defective"
    ]

    # Count each defect type
    defect_counts = (
        defective_df["defect_type"]
        .value_counts()
        .reset_index()
    )

    defect_counts.columns = [
        "defect_type",
        "frequency"
    ]

    # Sort defects from highest to lowest
    defect_counts = defect_counts.sort_values(
        by="frequency",
        ascending=False
    )

    # Calculate percentage contribution
    total_defects = defect_counts["frequency"].sum()

    defect_counts["percentage"] = (
        defect_counts["frequency"] / total_defects
    ) * 100

    # Calculate cumulative percentage
    defect_counts["cumulative_percentage"] = (
        defect_counts["percentage"].cumsum()
    )

    # Round calculated values
    defect_counts["percentage"] = (
        defect_counts["percentage"].round(2)
    )

    defect_counts["cumulative_percentage"] = (
        defect_counts["cumulative_percentage"].round(2)
    )

    return defect_counts
