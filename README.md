# AquaSmart SEWA - Production-Level Demo

A Streamlit demo showing how synthetic SCADA-style data can support smart water monitoring, leak detection, GIS-style zone visibility, SCADA-like alarms, and business value analysis.

## What is included

- `app.py` - main Streamlit dashboard
- `data_generator.py` - synthetic SCADA data generator
- `sample_scada_data.csv` - generated demo dataset
- `sewa_logo.png` - SEWA logo used in the dashboard
- `AquaSmart_SEWA_Executive_Pitch.pptx` - executive presentation
- `requirements.txt` - Python packages
- `run_app.bat` - Windows one-click launcher

## Main demo features

- Dark SEWA-style control room dashboard
- Real-time trend simulation for flow, pressure and consumption
- SCADA-style blinking alarm cards
- Interactive GIS-style Khorfakkan map
- Local zones: Zubara, Mussala, Hayawa, Al Luluyah and Al Wurrayah
- Mobile field-team view
- KPI cards: NRW, alerts, response time, efficiency and cost savings
- Before vs after business improvement simulation
- CSV and PowerPoint export options

## Run locally

Open the folder in Command Prompt or PowerShell, then run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Or on Windows, double-click:

```text
run_app.bat
```

## Important note

This prototype uses synthetic data only. It is not connected to live SEWA systems. The purpose is to demonstrate the product concept, dashboard design, analytics logic and operational workflow.

## Latest upgrade
This version adds:
- Daytime Khorfakkan GIS-style map
- White real-time trend chart labels for better readability
- Zone detail page from the sidebar
- Suggested supply pressure and flow ranges
- Recommended action panel
- Asset information by zone
- Leak history with operational status
- Financial impact estimate in m3/day and AED/day
- Team response workflow
- Executive summary panel
- Export selected zone daily summary report
