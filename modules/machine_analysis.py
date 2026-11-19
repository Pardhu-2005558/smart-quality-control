
def calculate_machine_quality(df):

    # Group products by machine
    machine_data = df.groupby("machine_id").agg(
        total_products=("product_id", "count"),

        defective_products=(
            "inspection_status",
            lambda x: (x == "Defective").sum()
        ),

        good_products=(
            "inspection_status",
            lambda x: (x == "Good").sum()
        )
    ).reset_index()

    # Calculate defect percentage
    machine_data["defect_rate"] = (
        machine_data["defective_products"]
        / machine_data["total_products"]
    ) * 100

    machine_data["defect_rate"] = (
        machine_data["defect_rate"].round(2)
    )

    # Calculate acceptance percentage
    machine_data["acceptance_rate"] = (
        machine_data["good_products"]
        / machine_data["total_products"]
    ) * 100

    machine_data["acceptance_rate"] = (
        machine_data["acceptance_rate"].round(2)
    )

    # Identify highest and lowest defect-rate machines
    worst_machine = machine_data.loc[
        machine_data["defect_rate"].idxmax()
    ]

    best_machine = machine_data.loc[
        machine_data["defect_rate"].idxmin()
    ]

    summary = {
        "total_machines": len(machine_data),

        "worst_machine": worst_machine["machine_id"],
        "worst_defect_rate": worst_machine["defect_rate"],

        "best_machine": best_machine["machine_id"],
        "best_defect_rate": best_machine["defect_rate"]
    }

    return machine_data, summary
