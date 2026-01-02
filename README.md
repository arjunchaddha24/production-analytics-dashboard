# Production Analytics Dashboard

A comprehensive Streamlit-based web application for analyzing production data with interactive visualizations.

## Features

- **📊 Daily Actual Production Tracking** - Bar chart showing actual production by process
- **📈 Cumulative Planned vs Actual** - Line/Bar charts comparing cumulative targets vs reality (Daily/Monthly views)
- **📉 Daily Planned vs Actual** - Line charts for day-to-day comparison
- **🎯 Production Completion Percentage** - Table showing completion percentage for each process
- **📅 Production Days Analysis** - Track production days vs non-production days per month (excluding Sundays)

## How to Use

1. Upload your production report Excel file
2. Select an analytics view from the sidebar
3. Apply filters as needed
4. Interact with the visualizations

## Local Development

To run this app locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

This app is designed to be deployed on Streamlit Cloud for 24/7 access.

## Data Format

The app expects an Excel file with the following structure:
- Multiple sheets (one per style)
- Columns including: Date, PO, Colour, Planned/Actual values for each process (Cutting, Sewing, Washing, Finishing, Packing)
- Date format: DD/MMM/YY (e.g., 15/Sep/25)
