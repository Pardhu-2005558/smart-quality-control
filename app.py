
import plotly.graph_objects as go
import plotly
import json
import os

from flask import Flask, render_template, request, redirect, url_for, flash
from modules.spc_analysis import calculate_spc
from modules.fishbone_analysis import generate_fishbone_causes
from modules.quality_recommendations import generate_quality_recommendations
from modules.machine_analysis import calculate_machine_quality
import pandas as pd
from io import BytesIO

from modules.quality_metrics import calculate_quality_metrics
from modules.pareto_analysis import calculate_pareto

app = Flask(__name__)
app.secret_key = "tqm_quality_control_secret"

# Maximum upload size: 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# Required dataset columns
REQUIRED_COLUMNS = [
    "product_id",
    "production_date",
    "batch_id",
    "machine_id",
    "operator_id",
    "defect_type",
    "inspection_status",
    "measured_dimension_cm",
    "lower_spec_limit_cm",
    "upper_spec_limit_cm"
]

ALLOWED_EXTENSIONS = {"csv", "xlsx"}

# Load default dataset
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "quality_inspection_sample.csv"
)

df = pd.read_csv(DATASET_PATH)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():

    metrics = calculate_quality_metrics(df)

    preview = df.head(10).fillna("").to_dict(orient="records")

    return render_template(
        "index.html",
        metrics=metrics,
        preview=preview,
        columns=df.columns.tolist(),
        total_rows=len(df),
        dataset_name=os.path.basename(DATASET_PATH)
    )


@app.route("/upload", methods=["POST"])
def upload_dataset():

    global df

    if "dataset" not in request.files:
        flash("Please select a dataset file.", "error")
        return redirect(url_for("home"))

    file = request.files["dataset"]

    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("home"))

    if not allowed_file(file.filename):
        flash("Only CSV and Excel (.xlsx) files are allowed.", "error")
        return redirect(url_for("home"))

    try:
        file_bytes = BytesIO(file.read())

        if file.filename.lower().endswith(".csv"):
            new_df = pd.read_csv(file_bytes)
        else:
            new_df = pd.read_excel(file_bytes)

        if new_df.empty:
            flash("The uploaded dataset is empty.", "error")
            return redirect(url_for("home"))

        missing_columns = [
            col for col in REQUIRED_COLUMNS
            if col not in new_df.columns
        ]

        if missing_columns:
            flash(
                "Missing required columns: " + ", ".join(missing_columns),
                "error"
            )
            return redirect(url_for("home"))

        new_df["inspection_status"] = (
            new_df["inspection_status"].astype(str).str.strip().str.title()
        )

        valid_statuses = {"Good", "Defective"}

        if not new_df["inspection_status"].isin(valid_statuses).all():
            flash(
                "Inspection status must contain only Good or Defective.",
                "error"
            )
            return redirect(url_for("home"))

        numeric_columns = [
            "measured_dimension_cm",
            "lower_spec_limit_cm",
            "upper_spec_limit_cm"
        ]

        for col in numeric_columns:
            new_df[col] = pd.to_numeric(new_df[col], errors="coerce")

        if new_df[numeric_columns].isnull().any().any():
            flash(
                "Measurement columns contain missing or invalid values.",
                "error"
            )
            return redirect(url_for("home"))

        df = new_df

        flash(
            f"Dataset uploaded successfully! {len(df)} records loaded.",
            "success"
        )

    except Exception as e:
        flash(f"Unable to process dataset: {str(e)}", "error")

    return redirect(url_for("home"))


@app.errorhandler(413)
def file_too_large(error):

    flash("File is too large. Maximum upload size is 10 MB.", "error")

    return redirect(url_for("home"))


# PARETO ANALYSIS ROUTE
@app.route("/pareto")
def pareto():

    pareto_df = calculate_pareto(df)

    total_defects = int(pareto_df["frequency"].sum())

    if total_defects > 0:

        highest_defect = pareto_df.iloc[0]["defect_type"]

        highest_percentage = float(
            pareto_df.iloc[0]["percentage"]
        )

        fig = go.Figure()

        # Defect frequency bars
        fig.add_trace(
            go.Bar(
                x=pareto_df["defect_type"],
                y=pareto_df["frequency"],
                name="Defect Frequency"
            )
        )

        # Cumulative percentage line
        fig.add_trace(
            go.Scatter(
                x=pareto_df["defect_type"],
                y=pareto_df["cumulative_percentage"],
                name="Cumulative Percentage",
                mode="lines+markers",
                yaxis="y2"
            )
        )

        fig.update_layout(
            title="Pareto Chart - Manufacturing Defects",
            xaxis_title="Defect Type",
            yaxis_title="Number of Defects",
            yaxis2=dict(
                title="Cumulative Percentage",
                overlaying="y",
                side="right",
                range=[0, 110],
                ticksuffix="%"
            ),
            template="plotly_white",
            legend=dict(
                orientation="h",
                y=1.12
            )
        )

        chart_json = json.dumps(
            fig,
            cls=plotly.utils.PlotlyJSONEncoder
        )

    else:

        highest_defect = "None"
        highest_percentage = 0

        chart_json = json.dumps({})

    pareto_data = pareto_df.to_dict(orient="records")

    return render_template(
        "pareto.html",
        pareto_data=pareto_data,
        total_defects=total_defects,
        highest_defect=highest_defect,
        highest_percentage=highest_percentage,
        chart_json=chart_json
    )


# FISHBONE ANALYSIS ROUTE
@app.route("/fishbone")
def fishbone():

    # Get defect types from defective products
    defect_types = sorted(
        df.loc[
            df["inspection_status"] == "Defective",
            "defect_type"
        ]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != ""]
        .unique()
        .tolist()
    )

    selected_defect = request.args.get("defect_type", "")

    # Use the first available defect by default
    if not selected_defect and defect_types:
        selected_defect = defect_types[0]

    if selected_defect not in defect_types:
        selected_defect = defect_types[0] if defect_types else ""

    # Count selected defect records
    defect_count = 0

    if selected_defect:
        defect_count = int(
            (
                (df["inspection_status"] == "Defective") &
                (df["defect_type"].astype(str).str.strip() == selected_defect)
            ).sum()
        )

    # Generate possible causes
    causes = (
        generate_fishbone_causes(selected_defect)
        if selected_defect else {}
    )

    return render_template(
        "fishbone.html",
        defect_types=defect_types,
        selected_defect=selected_defect,
        defect_count=defect_count,
        causes=causes
    )


# STATISTICAL PROCESS CONTROL ROUTE
@app.route("/spc")
def spc():

    try:
        spc_df, summary = calculate_spc(df)

        x_values = spc_df["product_id"].astype(str).tolist()
        measurements = spc_df["measured_dimension_cm"].tolist()
        moving_ranges = spc_df["moving_range"].fillna(0).tolist()

        # Individuals Control Chart
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=measurements,
                mode="lines+markers",
                name="Measured Dimension"
            )
        )

        fig.add_hline(
            y=summary["ucl"],
            line_dash="dash",
            line_color="red",
            annotation_text="UCL"
        )

        fig.add_hline(
            y=summary["cl"],
            line_dash="solid",
            line_color="green",
            annotation_text="Center Line"
        )

        fig.add_hline(
            y=summary["lcl"],
            line_dash="dash",
            line_color="red",
            annotation_text="LCL"
        )

        # Upper Specification Limit
        fig.add_hline(
            y=summary["usl"],
            line_dash="dot",
            line_color="blue",
            annotation_text="USL"
        )

        # Lower Specification Limit
        fig.add_hline(
            y=summary["lsl"],
            line_dash="dot",
            line_color="blue",
            annotation_text="LSL"
        )



        # Highlight out-of-control observations
        outliers = spc_df[
            spc_df["control_status"] == "Out of Control"
        ]

        fig.add_trace(
            go.Scatter(
                x=outliers["product_id"].astype(str).tolist(),
                y=outliers["measured_dimension_cm"].tolist(),
                mode="markers",
                name="Out of Control",
                marker=dict(size=10, color="red")
            )
        )

        fig.update_layout(
            title="Individuals Control Chart",
            xaxis_title="Product ID",
            yaxis_title="Measured Dimension (cm)",
            template="plotly_white",
            xaxis=dict(
                type="category",
                rangeslider=dict(visible=True)
            )
        )

        individuals_chart = json.dumps(
            fig,
            cls=plotly.utils.PlotlyJSONEncoder
        )

        # Moving Range Control Chart
        mr_fig = go.Figure()

        mr_fig.add_trace(
            go.Scatter(
                x=x_values,
                y=moving_ranges,
                mode="lines+markers",
                name="Moving Range"
            )
        )

        mr_fig.add_hline(
            y=summary["mr_ucl"],
            line_dash="dash",
            line_color="red",
            annotation_text="UCL"
        )

        mr_fig.add_hline(
            y=summary["mr_cl"],
            line_dash="solid",
            line_color="green",
            annotation_text="Center Line"
        )

        mr_fig.add_hline(
            y=summary["mr_lcl"],
            line_dash="dash",
            line_color="red",
            annotation_text="LCL"
        )

        mr_fig.update_layout(
            title="Moving Range Control Chart",
            xaxis_title="Product ID",
            yaxis_title="Moving Range (cm)",
            template="plotly_white",
            xaxis=dict(
                type="category",
                rangeslider=dict(visible=True)
            )
        )

        moving_range_chart = json.dumps(
            mr_fig,
            cls=plotly.utils.PlotlyJSONEncoder
        )

        return render_template(
            "spc.html",
            summary=summary,
            individuals_chart=individuals_chart,
            moving_range_chart=moving_range_chart,
            error=None
        )

    except ValueError as e:

        return render_template(
            "spc.html",
            summary=None,
            individuals_chart="{}",
            moving_range_chart="{}",
            error=str(e)
        )


@app.route("/machine-analysis")
def machine_analysis():

    # Calculate machine-wise quality
    machine_data, summary = calculate_machine_quality(df)

    # Prepare machine data
    machines = machine_data["machine_id"].astype(str).tolist()

    defective_counts = (
        machine_data["defective_products"].tolist()
    )

    defect_rates = (
        machine_data["defect_rate"].tolist()
    )

    # Chart 1: Defective products by machine
    fig_count = go.Figure()

    fig_count.add_trace(
        go.Bar(
            x=machines,
            y=defective_counts,
            text=defective_counts,
            textposition="auto",
            name="Defective Products"
        )
    )

    fig_count.update_layout(
        title="Machine-wise Defective Products",
        xaxis_title="Machine",
        yaxis_title="Number of Defective Products",
        template="plotly_white"
    )

    # Chart 2: Defect rate by machine
    fig_rate = go.Figure()

    fig_rate.add_trace(
        go.Bar(
            x=machines,
            y=defect_rates,
            text=defect_rates,
            texttemplate="%{text}%",
            textposition="auto",
            name="Defect Rate"
        )
    )

    fig_rate.update_layout(
        title="Machine-wise Defect Rate",
        xaxis_title="Machine",
        yaxis_title="Defect Rate (%)",
        template="plotly_white"
    )

    # Convert charts to HTML
    defect_chart = fig_count.to_html(
        full_html=False,
        include_plotlyjs="cdn"
    )

    rate_chart = fig_rate.to_html(
        full_html=False,
        include_plotlyjs=False
    )

    return render_template(
        "machine_analysis.html",
        machine_data=machine_data.to_dict(orient="records"),
        summary=summary,
        defect_chart=defect_chart,
        rate_chart=rate_chart
    )

@app.route("/recommendations")
def recommendations():

    recommendations_data = generate_quality_recommendations(df)

    return render_template(
    "recommendations.html",
    recommendations=recommendations_data
)

if __name__ == "__main__":
    app.run(debug=True)
