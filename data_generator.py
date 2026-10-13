import pandas as pd
import numpy as np

def generate_data():
    rng = np.random.default_rng(42)
    rows = []

    for day in pd.date_range("2015-01-01", "2025-12-31"):
        for route, capacity in [
            ("Route A", 180),
            ("Route B", 140),
            ("Route C", 110)
        ]:
            for hour in [6, 9, 12, 15, 18, 21]:

                if day.month in [3, 4, 5, 6]:
                    season = "Summer"
                elif day.month in [7, 8, 9]:
                    season = "Monsoon"
                elif day.month in [12, 1, 2]:
                    season = "Winter"
                else:
                    season = "Post-monsoon"

                load = 0.4 + rng.normal(0, 0.12)

                if hour in [9, 18]:
                    load += 0.25

                if day.dayofweek >= 5:
                    load += 0.05

                if season == "Monsoon":
                    load -= 0.08

                passengers = int(round(
                    capacity * np.clip(load, 0.05, 1)
                ))

                delay = max(
                    0,
                    round(
                        (passengers / capacity - 0.7) * 35
                        + rng.normal(4, 3),
                        1
                    )
                )

                rows.append({
                    "Date": day,
                    "Route": route,
                    "Hour": hour,
                    "Season": season,
                    "Day_Type": (
                        "Weekend" if day.dayofweek >= 5
                        else "Weekday"
                    ),
                    "Capacity": capacity,
                    "Passengers": passengers,
                    "Utilization_Pct": round(
                        passengers / capacity * 100, 2
                    ),
                    "Estimated_Delay_Min": delay
                })

    df = pd.DataFrame(rows)
    df.to_csv("sample_data.csv", index=False)
    df.to_excel("sample_data.xlsx", index=False)

    return df

if __name__ == "__main__":
    generate_data()
    print("Sample CSV and Excel datasets created successfully!")
