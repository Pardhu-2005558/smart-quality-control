import pandas as pd

def generate_quality_recommendations(df):

    recommendations = []

    # --------------------------------
    # 1. Machine-wise analysis
    # --------------------------------

    machine_data = df.groupby("machine_id").agg(
        total_products=("product_id", "count"),
        defective_products=(
            "inspection_status",
            lambda x: (x == "Defective").sum()
        )
    ).reset_index()

    machine_data["defect_rate"] = (
        machine_data["defective_products"]
        / machine_data["total_products"]
    ) * 100

    if not machine_data.empty:

        worst_machine = machine_data.loc[
            machine_data["defect_rate"].idxmax()
        ]

        if worst_machine["defective_products"] > 0:

            recommendations.append({
                "category": "Machine Performance",
                "finding": (
                    f"Machine {worst_machine['machine_id']} "
                    f"has the highest defect rate of "
                    f"{worst_machine['defect_rate']:.2f}%."
                ),
                "recommendation": (
                    "Inspect machine calibration, tooling "
                    "condition, maintenance history and "
                    "operating settings."
                ),
                "priority": "High"
            })

    # --------------------------------
    # 2. Most frequent defect
    # --------------------------------

    defective_df = df[
        df["inspection_status"] == "Defective"
    ]

    if not defective_df.empty:

        defect_counts = defective_df["defect_type"].value_counts()

        top_defect = defect_counts.index[0]
        top_defect_count = int(defect_counts.iloc[0])

        defect_actions = {
            "Scratch": (
                "Check product handling, surface protection, "
                "and contact with machine components."
            ),

            "Crack": (
                "Inspect material quality, machine pressure, "
                "temperature and manufacturing conditions."
            ),

            "Dimension Error": (
                "Check machine calibration, cutting settings "
                "and measurement equipment."
            ),

            "Packaging Error": (
                "Review packaging procedures, sealing "
                "equipment and operator practices."
            )
        }

        action = defect_actions.get(
            top_defect,
            "Investigate the manufacturing process and "
            "inspect the affected products."
        )

        recommendations.append({
            "category": "Major Defect",
            "finding": (
                f"{top_defect} is the most frequent defect "
                f"with {top_defect_count} occurrences."
            ),
            "recommendation": action,
            "priority": "High"
        })

    # --------------------------------
    # 3. Specification limit analysis
    # --------------------------------

    dimension = pd.to_numeric(
        df["measured_dimension_cm"],
        errors="coerce"
    )

    lower_limit = pd.to_numeric(
        df["lower_spec_limit_cm"],
        errors="coerce"
    )

    upper_limit = pd.to_numeric(
        df["upper_spec_limit_cm"],
        errors="coerce"
    )

    valid_data = (
        dimension.notna()
        & lower_limit.notna()
        & upper_limit.notna()
    )

    out_of_spec = (
        (dimension < lower_limit)
        | (dimension > upper_limit)
    ) & valid_data

    out_of_spec_count = int(out_of_spec.sum())

    if out_of_spec_count > 0:

        recommendations.append({
            "category": "Dimensional Quality",
            "finding": (
                f"{out_of_spec_count} products are outside "
                "the specification limits."
            ),
            "recommendation": (
                "Inspect process settings, verify measuring "
                "equipment calibration and monitor product "
                "dimensions regularly."
            ),
            "priority": "High"
        })

    else:

        recommendations.append({
            "category": "Dimensional Quality",
            "finding": (
                "All valid product measurements are within "
                "the specification limits."
            ),
            "recommendation": (
                "Continue routine dimensional inspections "
                "and monitor process variation."
            ),
            "priority": "Low"
        })

    # --------------------------------
    # 4. Overall quality recommendation
    # --------------------------------

    total_products = len(df)

    total_defective = int(
        (df["inspection_status"] == "Defective").sum()
    )

    if total_products > 0:

        defect_rate = (
            total_defective / total_products
        ) * 100

        if defect_rate > 10:

            recommendations.append({
                "category": "Overall Quality",
                "finding": (
                    f"The overall defect rate is "
                    f"{defect_rate:.2f}%."
                ),
                "recommendation": (
                    "Strengthen quality inspections, "
                    "investigate recurring defects and "
                    "monitor improvement after corrective actions."
                ),
                "priority": "High"
            })

        else:

            recommendations.append({
                "category": "Overall Quality",
                "finding": (
                    f"The overall defect rate is "
                    f"{defect_rate:.2f}%."
                ),
                "recommendation": (
                    "Maintain existing quality checks and "
                    "continue monitoring defect trends."
                ),
                "priority": "Medium"
            })

    return recommendations
