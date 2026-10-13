# Ferry Capacity Utilization & Operational Efficiency Analytics

## Project Overview
This project analyzes ferry passenger demand, vessel capacity,
congestion patterns, idle capacity, and operational efficiency.

The dashboard is developed using Python, Pandas, NumPy,
Plotly, and Streamlit.

## Features
- Five Key Performance Indicators (KPIs)
- Capacity utilization analysis
- Congestion pressure index
- Idle capacity percentage
- Peak-strain record identification
- Operational variability score
- Route-wise comparison
- Congestion and idle-capacity heatmaps
- Seasonal efficiency comparison
- Weekday versus weekend analysis
- Interactive filters and alerts
- CSV data download

## Dataset
The project uses simulated sample ferry data covering
2015–2025. It is intended for educational demonstration
and does not represent actual ferry operating statistics.

## Installation on Ubuntu 22

Install the required system packages:

    sudo apt update
    sudo apt install python3-venv python3-pip -y

Navigate to the project directory:

    cd ~/Documents/FerryAnalytics

Create a virtual environment:

    python3 -m venv .venv

Activate it:

    source .venv/bin/activate

Install Python libraries:

    python3 -m pip install -r requirements.txt

## Run the Application

    streamlit run app.py

Open the local URL displayed in the terminal.
Usually, it is http://localhost:8501.

## KPI Definitions
1. Capacity Utilization Ratio:
   Passengers divided by available capacity, multiplied by 100.

2. Congestion Pressure Index:
   A project-defined indicator of high utilization.

3. Idle Capacity Percentage:
   100 minus the capacity utilization percentage.

4. Peak Strain:
   Number of records meeting the selected utilization threshold.

5. Operational Variability Score:
   Standard deviation of utilization percentages.

## Limitations
All generated results are based on simulated data.
Validate findings against real operational records before
using them for government or operational decisions.

## Future Enhancements
- Integration of verified ferry operational data
- Improved congestion forecasting
- More detailed peak-strain duration calculations
- Exportable stakeholder reports
-
