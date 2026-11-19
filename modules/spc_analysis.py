
import pandas as pd


def calculate_spc(df):

    # Extract measurements and specification limits
    spc_df = df[
        [
            "product_id",
            "production_date",
            "measured_dimension_cm",
            "lower_spec_limit_cm",
            "upper_spec_limit_cm"
        ]
    ].copy()

    numeric_columns = [
        "measured_dimension_cm",
        "lower_spec_limit_cm",
        "upper_spec_limit_cm"
    ]

    for col in numeric_columns:
        spc_df[col] = pd.to_numeric(
            spc_df[col],
            errors="coerce"
        )

    # Remove invalid measurements
    spc_df = spc_df.dropna(
        subset=numeric_columns
    )

    if spc_df.empty:
        raise ValueError("No valid measurement records found.")

    # Sort by production date
    spc_df["production_date"] = pd.to_datetime(
        spc_df["production_date"],
        errors="coerce"
    )

    spc_df = spc_df.dropna(
        subset=["production_date"]
    )

    spc_df = spc_df.sort_values(
        "production_date",
        kind="stable"
    ).reset_index(drop=True)

    if len(spc_df) < 2:
        raise ValueError(
            "At least two valid measurements are required."
        )

    # Get specification limits
    lsl_values = spc_df["lower_spec_limit_cm"]
    usl_values = spc_df["upper_spec_limit_cm"]

    if (lsl_values >= usl_values).any():
        raise ValueError(
            "Lower specification limit must be less than upper specification limit."
        )

    # Check specification limits are consistent
    if lsl_values.nunique() != 1 or usl_values.nunique() != 1:
        raise ValueError(
            "This SPC analysis requires the same specification limits for all records."
        )

    lsl = float(lsl_values.iloc[0])
    usl = float(usl_values.iloc[0])

    # Individuals chart calculations
    values = spc_df["measured_dimension_cm"]

    process_mean = values.mean()

    spc_df["moving_range"] = values.diff().abs()

    average_moving_range = spc_df["moving_range"].mean()

    sigma_estimate = average_moving_range / 1.128

    # Calculate control limits
    ucl = process_mean + (3 * sigma_estimate)
    lcl = process_mean - (3 * sigma_estimate)

    # Process Capability Analysis (Cp and Cpk)
    if sigma_estimate > 0:

        cp = (usl - lsl) / (6 * sigma_estimate)

        cpu = (usl - process_mean) / (3 * sigma_estimate)

        cpl = (process_mean - lsl) / (3 * sigma_estimate)

        cpk = min(cpu, cpl)

    else:
        cp = None
        cpk = None

    # Capability interpretation
    if cpk is None:
        capability_status = "Cannot be calculated"

    elif cpk >= 1.33:
        capability_status = "Capable"

    elif cpk >= 1.00:
        capability_status = "Marginal"

    else:
        capability_status = "Not Capable"

    # Moving Range chart limits
    mr_ucl = 3.267 * average_moving_range
    mr_cl = average_moving_range

    # Statistical control status
    spc_df["control_status"] = values.apply(
        lambda x: "Out of Control"
        if x > ucl or x < lcl
        else "In Control"
    )

    # Specification status
    spc_df["specification_status"] = values.apply(
        lambda x: "Out of Specification"
        if x > usl or x < lsl
        else "Within Specification"
    )

    out_of_control_count = int(
        (spc_df["control_status"] == "Out of Control").sum()
    )

    out_of_specification_count = int(
        (
            spc_df["specification_status"]
            == "Out of Specification"
        ).sum()
    )

    within_specification_count = (
        len(spc_df) - out_of_specification_count
    )

    # Summary
    summary = {
        "total_measurements": len(spc_df),
        "process_mean": round(process_mean, 4),

        "ucl": round(ucl, 4),
        "cl": round(process_mean, 4),
        "lcl": round(lcl, 4),

        "usl": round(usl, 4),
        "lsl": round(lsl, 4),

        "average_moving_range": round(average_moving_range, 4),
        "mr_ucl": round(mr_ucl, 4),
        "mr_cl": round(mr_cl, 4),
        "mr_lcl": 0,

        "cp": round(cp, 3) if cp is not None else None,
        "cpk": round(cpk, 3) if cpk is not None else None,
        "capability_status": capability_status,

        "out_of_control_count": out_of_control_count,
        "in_control_count": len(spc_df) - out_of_control_count,

        "out_of_specification_count": out_of_specification_count,
        "within_specification_count": within_specification_count
    }

    return spc_df, summary
