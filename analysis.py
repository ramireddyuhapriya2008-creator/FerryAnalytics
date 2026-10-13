def calculate_kpis(df, threshold=80):
    capacity = df["Capacity"].sum()
    passengers = df["Passengers"].sum()

    utilization = (
        passengers / capacity * 100 if capacity else 0
    )

    congestion = max(
        0, min(100, (utilization - 70) / 30 * 100)
    )

    idle_capacity = 100 - utilization

    peak_strain = int(
        (df["Utilization_Pct"] >= threshold).sum()
    )

    variability = df["Utilization_Pct"].std()

    return {
        "Capacity Utilization Ratio (%)":
            round(utilization, 2),

        "Congestion Pressure Index":
            round(congestion, 2),

        "Idle Capacity Percentage (%)":
            round(idle_capacity, 2),

        "Peak Strain Records":
            peak_strain,

        "Operational Variability Score":
            round(variability, 2)
    }
