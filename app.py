import streamlit as st
import pandas as pd
import plotly.express as px

from data_generator import generate_data
from analysis import calculate_kpis

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Ferry Analytics Dashboard",
    page_icon="⛴️",
    layout="wide"
)

st.title("⛴️ Ferry Capacity Utilization & Operational Efficiency")
st.caption(
    "Unified Mentor Project | Simulated historical data: 2015–2025"
)

# ---------------- DATA UPLOAD ----------------

st.subheader("Upload Your Ferry Data")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx"],
    help="Required columns: Date, Route, Capacity, Passengers"
)

# ---------------- LOAD DATA ----------------

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("Your file was uploaded successfully.")

    except Exception as e:
        st.error(f"Unable to read the uploaded file: {e}")
        st.stop()

else:
    @st.cache_data
    def load_sample_data():
        return generate_data()

    with st.spinner("Loading sample ferry data..."):
        df = load_sample_data()

    st.info("Using generated sample data. Upload your own file above to analyze it.")

# ---------------- STANDARDIZE COLUMN NAMES ----------------

df.columns = [str(column).strip() for column in df.columns]

aliases = {
    "date": "Date",
    "route": "Route",
    "hour": "Hour",
    "season": "Season",
    "day_type": "Day_Type",
    "capacity": "Capacity",
    "passengers": "Passengers",
    "utilization_pct": "Utilization_Pct",
    "estimated_delay_min": "Estimated_Delay_Min"
}

rename_columns = {
    column: aliases[column.lower()]
    for column in df.columns
    if column.lower() in aliases
}

df = df.rename(columns=rename_columns)

# ---------------- VALIDATE DATA ----------------

required_columns = [
    "Date",
    "Route",
    "Capacity",
    "Passengers"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "Your file is missing these required columns: "
        + ", ".join(missing_columns)
    )
    st.info(
        "Required columns: Date, Route, Capacity, Passengers."
    )
    st.stop()

if df.empty:
    st.error("The uploaded file contains no records.")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Capacity"] = pd.to_numeric(df["Capacity"], errors="coerce")
df["Passengers"] = pd.to_numeric(
    df["Passengers"], errors="coerce"
)

invalid_values = df[
    ["Date", "Capacity", "Passengers"]
].isna().any(axis=1)

if invalid_values.any():
    st.error(
        f"{int(invalid_values.sum())} row(s) have invalid dates, "
        "capacity, or passenger values. Correct them and upload again."
    )
    st.stop()

if (df["Capacity"] <= 0).any():
    st.error("Capacity must be greater than zero.")
    st.stop()

if (df["Passengers"] < 0).any():
    st.error("Passenger counts cannot be negative.")
    st.stop()

if (df["Passengers"] > df["Capacity"]).any():
    st.warning(
        "Some records have more passengers than stated capacity. "
        "Their utilization will exceed 100%."
    )

df["Route"] = df["Route"].astype(str).str.strip()

if (df["Route"] == "").any():
    st.error("Route names cannot be empty.")
    st.stop()

# ---------------- FILL OPTIONAL COLUMNS ----------------

if "Hour" not in df.columns:
    df["Hour"] = 0

df["Hour"] = pd.to_numeric(df["Hour"], errors="coerce")

if df["Hour"].isna().any() or not df["Hour"].between(0, 23).all():
    st.error("Hour must contain numbers from 0 to 23.")
    st.stop()

if "Season" not in df.columns:
    def get_season(month):
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5, 6]:
            return "Summer"
        elif month in [7, 8, 9]:
            return "Monsoon"
        return "Post-monsoon"

    df["Season"] = df["Date"].dt.month.map(get_season)

if "Day_Type" not in df.columns:
    df["Day_Type"] = df["Date"].dt.dayofweek.map(
        lambda day: "Weekend" if day >= 5 else "Weekday"
    )

df["Utilization_Pct"] = (
    df["Passengers"] / df["Capacity"] * 100
)

if "Estimated_Delay_Min" not in df.columns:
    df["Estimated_Delay_Min"] = 0

# ---------------- DATA SUMMARY ----------------

st.caption(f"Total records loaded: {len(df):,}")

with st.expander("Preview loaded data"):
    st.dataframe(df.head(20), use_container_width=True)

# ---------------- DASHBOARD FILTERS ----------------

st.sidebar.header("Dashboard Filters")

all_routes = sorted(df["Route"].unique().tolist())

selected_routes = st.sidebar.multiselect(
    "Select Routes",
    options=all_routes,
    default=all_routes
)

all_seasons = sorted(df["Season"].dropna().unique().tolist())

selected_seasons = st.sidebar.multiselect(
    "Select Seasons",
    options=all_seasons,
    default=all_seasons
)

minimum_year = int(df["Date"].dt.year.min())
maximum_year = int(df["Date"].dt.year.max())

if minimum_year < maximum_year:
    selected_years = st.sidebar.slider(
        "Select Years",
        min_value=minimum_year,
        max_value=maximum_year,
        value=(minimum_year, maximum_year)
    )
else:
    selected_years = (minimum_year, maximum_year)
    st.sidebar.write(f"Year: {minimum_year}")

threshold = st.sidebar.slider(
    "Peak Utilization Threshold (%)",
    min_value=50,
    max_value=100,
    value=80
)

# ---------------- FILTER DATA ----------------

filtered_data = df[
    df["Route"].isin(selected_routes)
    & df["Season"].isin(selected_seasons)
    & df["Date"].dt.year.between(
        selected_years[0], selected_years[1]
    )
].copy()

if filtered_data.empty:
    st.warning(
        "No records match these filters. Please change your selections."
    )
    st.stop()

# ---------------- CALCULATE KPIs ----------------

kpis = calculate_kpis(filtered_data, threshold)

st.subheader("Key Performance Indicators")

columns = st.columns(5)

for column, (name, value) in zip(columns, kpis.items()):
    if "(%)" in name:
        display_value = f"{value}%"
    else:
        display_value = str(value)

    column.metric(name, display_value)

if kpis["Peak Strain Records"] > 0:
    st.warning(
        f'{kpis["Peak Strain Records"]} records have utilization '
        f'at or above {threshold}%.'
    )
else:
    st.success(
        "No records meet the selected peak utilization threshold."
    )

# ---------------- DASHBOARD TABS ----------------

overview_tab, heatmap_tab, seasonal_tab, data_tab = st.tabs([
    "Overview",
    "Utilization Heatmap",
    "Seasonal Analysis",
    "Data and Export"
])

# ---------------- OVERVIEW ----------------

with overview_tab:
    st.subheader("Capacity Utilization Trend")

    trend = filtered_data.groupby(
        "Date", as_index=False
    ).agg(
        Utilization_Pct=("Utilization_Pct", "mean")
    )

    trend_chart = px.line(
        trend,
        x="Date",
        y="Utilization_Pct",
        title="Average Daily Capacity Utilization",
        labels={
            "Date": "Date",
            "Utilization_Pct": "Utilization (%)"
        }
    )

    trend_chart.add_hline(
        y=threshold,
        line_dash="dash",
        annotation_text="Peak threshold"
    )

    st.plotly_chart(
        trend_chart,
        use_container_width=True
    )

    st.subheader("Route Performance Comparison")

    route_summary = filtered_data.groupby(
        "Route", as_index=False
    ).agg(
        Passengers=("Passengers", "sum"),
        Capacity=("Capacity", "sum")
    )

    route_summary["Utilization (%)"] = (
        route_summary["Passengers"]
        / route_summary["Capacity"] * 100
    )

    route_chart = px.bar(
        route_summary,
        x="Route",
        y="Utilization (%)",
        title="Capacity Utilization by Route",
        text_auto=".1f"
    )

    st.plotly_chart(
        route_chart,
        use_container_width=True
    )

    st.subheader("Operational Recommendations")

    utilization = kpis["Capacity Utilization Ratio (%)"]
    idle = kpis["Idle Capacity Percentage (%)"]
    variability = kpis["Operational Variability Score"]

    if utilization >= threshold:
        st.write(
            "- Review peak-period schedules and available vessel capacity."
        )

    if idle > 45:
        st.write(
            "- Review low-demand periods for possible schedule adjustments."
        )

    if variability > 18:
        st.write(
            "- Investigate differences across routes, hours, and seasons."
        )

    if utilization < threshold and idle <= 45 and variability <= 18:
        st.write(
            "- Continue monitoring demand and compare route performance."
        )

    st.write(
        "- Validate recommendations using real operational records."
    )

# ---------------- UTILIZATION HEATMAP ----------------

with heatmap_tab:
    st.subheader("Route and Hour Utilization Heatmap")

    matrix = filtered_data.pivot_table(
        index="Route",
        columns="Hour",
        values="Utilization_Pct",
        aggfunc="mean"
    )

    heatmap_chart = px.imshow(
        matrix,
        aspect="auto",
        title="Average Utilization by Route and Hour",
        labels={
            "x": "Hour of Day",
            "y": "Route",
            "color": "Utilization (%)"
        }
    )

    st.plotly_chart(
        heatmap_chart,
        use_container_width=True
    )

    st.subheader("Weekday and Weekend Comparison")

    day_summary = filtered_data.groupby(
        "Day_Type", as_index=False
    ).agg(
        Utilization=("Utilization_Pct", "mean")
    )

    day_chart = px.bar(
        day_summary,
        x="Day_Type",
        y="Utilization",
        title="Average Utilization by Day Type"
    )

    st.plotly_chart(
        day_chart,
        use_container_width=True
    )

# ---------------- SEASONAL ANALYSIS ----------------

with seasonal_tab:
    st.subheader("Seasonal Capacity Utilization")

    season_summary = filtered_data.groupby(
        "Season", as_index=False
    ).agg(
        Passengers=("Passengers", "sum"),
        Capacity=("Capacity", "sum")
    )

    season_summary["Utilization (%)"] = (
        season_summary["Passengers"]
        / season_summary["Capacity"] * 100
    )

    season_chart = px.bar(
        season_summary,
        x="Season",
        y="Utilization (%)",
        title="Capacity Utilization Across Seasons",
        text_auto=".1f"
    )

    st.plotly_chart(
        season_chart,
        use_container_width=True
    )

    st.subheader("Hourly Demand Pattern")

    hourly_summary = filtered_data.groupby(
        ["Hour", "Day_Type"], as_index=False
    ).agg(
        Utilization=("Utilization_Pct", "mean")
    )

    hourly_chart = px.line(
        hourly_summary,
        x="Hour",
        y="Utilization",
        color="Day_Type",
        markers=True,
        title="Hourly Utilization: Weekdays vs Weekends"
    )

    st.plotly_chart(
        hourly_chart,
        use_container_width=True
    )

# ---------------- DATA AND EXPORT ----------------

with data_tab:
    st.subheader("Filtered Ferry Records")

    st.dataframe(
        filtered_data,
        use_container_width=True
    )

    csv_data = filtered_data.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name="ferry_filtered_data.csv",
        mime="text/csv"
    )

    st.write(
        f"Number of filtered records: {len(filtered_data):,}"
    )

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "Research limitation: Generated records are simulated, not verified "
    "real-world ferry data. The Peak Strain Records KPI counts records "
    "at or above the selected threshold; it does not measure elapsed time. "
    "The congestion index is a project-defined indicator, not an official "
    "transport standard."
)
