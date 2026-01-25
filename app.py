import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar
import os
import json
import shutil

# Page configuration
st.set_page_config(
    page_title="Production Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# ========================================
# FILE PERSISTENCE SETUP
# ========================================

# Define persistent storage directory
STORAGE_DIR = "/tmp/production_analytics_storage"
SAVED_FILE_PATH = os.path.join(STORAGE_DIR, "last_uploaded_file.xlsx")
METADATA_PATH = os.path.join(STORAGE_DIR, "file_metadata.json")

# Create storage directory if it doesn't exist
os.makedirs(STORAGE_DIR, exist_ok=True)

def save_uploaded_file(uploaded_file):
    """
    Save the uploaded file to persistent storage and update metadata.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        # Save the file
        with open(SAVED_FILE_PATH, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Save metadata
        metadata = {
            "filename": uploaded_file.name,
            "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_size": uploaded_file.size
        }
        
        with open(METADATA_PATH, "w") as f:
            json.dump(metadata, f)
        
        return True
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return False

def load_saved_file():
    """
    Load the previously saved file from persistent storage.
    
    Returns:
        tuple: (file_path, metadata_dict) if file exists, (None, None) otherwise
    """
    try:
        # Check if saved file exists
        if not os.path.exists(SAVED_FILE_PATH):
            return None, None
        
        # Check if metadata exists
        if not os.path.exists(METADATA_PATH):
            return None, None
        
        # Load metadata
        with open(METADATA_PATH, "r") as f:
            metadata = json.load(f)
        
        return SAVED_FILE_PATH, metadata
    except Exception as e:
        return None, None

def clear_saved_file():
    """
    Clear the saved file and metadata from persistent storage.
    """
    try:
        if os.path.exists(SAVED_FILE_PATH):
            os.remove(SAVED_FILE_PATH)
        if os.path.exists(METADATA_PATH):
            os.remove(METADATA_PATH)
        return True
    except Exception as e:
        st.error(f"Error clearing saved file: {str(e)}")
        return False

# ========================================
# HTML REPORT GENERATION
# ========================================

def generate_html_report(data):
    """
    Generate a self-contained HTML report with embedded data and interactive filters.
    
    Args:
        data: pandas DataFrame with production data
    
    Returns:
        str: HTML content as a string
    """
    
    # Convert data to JSON for embedding
    data_json = data.to_json(orient='records', date_format='iso')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Production Analytics Report</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; padding: 20px; }}
        #app {{ max-width: 1400px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1f77b4; text-align: center; margin-bottom: 10px; font-size: 2.5rem; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; font-size: 1.1rem; }}
        .filters-container {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; border: 1px solid #dee2e6; }}
        .filter-row {{ display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap; align-items: center; }}
        .filter-group {{ flex: 1; min-width: 200px; }}
        .filter-label {{ display: block; font-weight: 600; margin-bottom: 5px; color: #333; font-size: 0.9rem; }}
        select, input[type="date"] {{ width: 100%; padding: 10px; border: 1px solid #ced4da; border-radius: 5px; font-size: 14px; background-color: white; }}
        select:focus, input[type="date"]:focus {{ outline: none; border-color: #1f77b4; box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.1); }}
        select[multiple] {{ height: 80px; }}
        .chart-container {{ margin-bottom: 40px; background-color: #fafafa; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; }}
        .info-message {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; border-left: 4px solid #1f77b4; margin-bottom: 20px; }}
        .warning-message {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin-bottom: 20px; }}
        .button-group {{ display: flex; gap: 10px; margin-top: 15px; }}
        button {{ padding: 10px 20px; border: none; border-radius: 5px; font-size: 14px; cursor: pointer; transition: background-color 0.2s; }}
        button.primary {{ background-color: #1f77b4; color: white; }}
        button.primary:hover {{ background-color: #155a8a; }}
        button.secondary {{ background-color: #6c757d; color: white; }}
        button.secondary:hover {{ background-color: #545b62; }}
    </style>
</head>
<body>
    <div id="app">
        <h1>📊 Production Analytics Report</h1>
        <div class="subtitle">Interactive Offline Analytics Dashboard</div>
        <div class="info-message"><strong>ℹ️ How to use:</strong> Select filters below to view analytics. All data is embedded - no internet required!</div>
        <div class="filters-container">
            <div class="filter-row">
                <div class="filter-group"><label class="filter-label">Style</label><select id="styleFilter"><option value="">Select Style...</option></select></div>
                <div class="filter-group"><label class="filter-label">PO (Ctrl/Cmd for multiple)</label><select id="poFilter" multiple></select></div>
                <div class="filter-group"><label class="filter-label">Colour (Ctrl/Cmd for multiple)</label><select id="colourFilter" multiple></select></div>
            </div>
            <div class="filter-row">
                <div class="filter-group"><label class="filter-label">Start Date</label><input type="date" id="startDate"></div>
                <div class="filter-group"><label class="filter-label">End Date</label><input type="date" id="endDate"></div>
                <div class="filter-group"><label class="filter-label">View Mode</label><select id="viewMode"><option value="Daily">Daily</option><option value="Weekly">Weekly</option><option value="Monthly">Monthly</option></select></div>
            </div>
            <div class="button-group"><button class="primary" onclick="updateCharts()">🔄 Update Charts</button><button class="secondary" onclick="resetFilters()">↺ Reset Filters</button></div>
        </div>
        <div id="message"></div><div id="charts"></div>
    </div>
    <script>
        const rawData = {data_json};
        rawData.forEach(row => {{ row.Date = new Date(row.Date); }});
        const processes = ['Cutting', 'Sewing', 'Washing', 'Finishing', 'Packing'];
        
        function populateFilters() {{
            const styles = [...new Set(rawData.map(r => r['Style No']))].sort();
            const styleFilter = document.getElementById('styleFilter');
            styles.forEach(style => {{ const option = document.createElement('option'); option.value = style; option.textContent = style; styleFilter.appendChild(option); }});
            if (styles.length > 0) {{ styleFilter.value = styles[0]; updatePOAndColourFilters(); }}
            const dates = rawData.map(r => r.Date);
            const minDate = new Date(Math.min(...dates)); const maxDate = new Date(Math.max(...dates));
            document.getElementById('startDate').value = minDate.toISOString().split('T')[0];
            document.getElementById('endDate').value = maxDate.toISOString().split('T')[0];
        }}
        
        function updatePOAndColourFilters() {{
            const selectedStyle = document.getElementById('styleFilter').value;
            const styleData = rawData.filter(r => r['Style No'] === selectedStyle);
            const pos = [...new Set(styleData.map(r => String(r.PO)))].sort();
            const colours = [...new Set(styleData.map(r => String(r.Colour)))].sort();
            const poFilter = document.getElementById('poFilter'); const colourFilter = document.getElementById('colourFilter');
            poFilter.innerHTML = ''; colourFilter.innerHTML = '';
            pos.forEach(po => {{ const option = document.createElement('option'); option.value = po; option.textContent = po; option.selected = true; poFilter.appendChild(option); }});
            colours.forEach(colour => {{ const option = document.createElement('option'); option.value = colour; option.textContent = colour; option.selected = true; colourFilter.appendChild(option); }});
        }}
        
        document.getElementById('styleFilter').addEventListener('change', () => {{ updatePOAndColourFilters(); updateCharts(); }});
        
        function resetFilters() {{
            const styleFilter = document.getElementById('styleFilter');
            if (styleFilter.options.length > 1) {{ styleFilter.selectedIndex = 1; }}
            updatePOAndColourFilters();
            const dates = rawData.map(r => r.Date); const minDate = new Date(Math.min(...dates)); const maxDate = new Date(Math.max(...dates));
            document.getElementById('startDate').value = minDate.toISOString().split('T')[0];
            document.getElementById('endDate').value = maxDate.toISOString().split('T')[0];
            document.getElementById('viewMode').value = 'Daily'; updateCharts();
        }}
        
        function updateCharts() {{
            const selectedStyle = document.getElementById('styleFilter').value;
            if (!selectedStyle) {{ document.getElementById('message').innerHTML = '<div class="warning-message">⚠️ Please select a style.</div>'; document.getElementById('charts').innerHTML = ''; return; }}
            const selectedPOs = Array.from(document.getElementById('poFilter').selectedOptions).map(o => o.value);
            const selectedColours = Array.from(document.getElementById('colourFilter').selectedOptions).map(o => o.value);
            const startDate = new Date(document.getElementById('startDate').value); const endDate = new Date(document.getElementById('endDate').value);
            const viewMode = document.getElementById('viewMode').value;
            if (selectedPOs.length === 0 || selectedColours.length === 0) {{ document.getElementById('message').innerHTML = '<div class="warning-message">⚠️ Select at least one PO and Colour.</div>'; document.getElementById('charts').innerHTML = ''; return; }}
            document.getElementById('message').innerHTML = '';
            const filteredData = rawData.filter(row => {{ return row['Style No'] === selectedStyle && selectedPOs.includes(String(row.PO)) && selectedColours.includes(String(row.Colour)) && row.Date >= startDate && row.Date <= endDate; }});
            if (filteredData.length === 0) {{ document.getElementById('message').innerHTML = '<div class="warning-message">⚠️ No data matches filters.</div>'; document.getElementById('charts').innerHTML = ''; return; }}
            generateDailyCharts(filteredData);
        }}
        
        function generateDailyCharts(filteredData) {{
            const combinations = [...new Set(filteredData.map(r => `${{r['Style No']}}_${{r.PO}}_${{r.Colour}}`))]; const allDates = [];
            const minDate = new Date(Math.min(...filteredData.map(r => r.Date))); const maxDate = new Date(Math.max(...filteredData.map(r => r.Date)));
            for (let d = new Date(minDate); d <= maxDate; d.setDate(d.getDate() + 1)) {{ allDates.push(new Date(d)); }}
            const aggregatedData = allDates.map(currentDate => {{
                const result = {{ Date: currentDate }}; processes.forEach(process => {{ result[`Cumulative Planned ${{process}}`] = 0; result[`Cumulative Actual ${{process}}`] = 0; }});
                combinations.forEach(combo => {{
                    const [style, po, colour] = combo.split('_');
                    const comboData = filteredData.filter(r => r['Style No'] === style && String(r.PO) === po && String(r.Colour) === colour && r.Date <= currentDate).sort((a, b) => a.Date - b.Date);
                    if (comboData.length > 0) {{ const lastRow = comboData[comboData.length - 1]; processes.forEach(process => {{ result[`Cumulative Planned ${{process}}`] += lastRow[`Cumulative Planned ${{process}}`] || 0; result[`Cumulative Actual ${{process}}`] += lastRow[`Cumulative Actual ${{process}}`] || 0; }}); }}
                }}); return result;
            }});
            const chartsDiv = document.getElementById('charts'); chartsDiv.innerHTML = '';
            processes.forEach(process => {{
                const chartDiv = document.createElement('div'); chartDiv.className = 'chart-container'; chartDiv.id = `chart-${{process}}`; chartsDiv.appendChild(chartDiv);
                const dates = aggregatedData.map(d => d.Date); const plannedValues = aggregatedData.map(d => d[`Cumulative Planned ${{process}}`]); const actualValues = aggregatedData.map(d => d[`Cumulative Actual ${{process}}`]);
                const trace1 = {{ x: dates, y: plannedValues, type: 'scatter', mode: 'lines+markers', name: 'Planned', line: {{ dash: 'dash', width: 3, color: '#FF6B6B' }}, marker: {{ size: 6 }} }};
                const trace2 = {{ x: dates, y: actualValues, type: 'scatter', mode: 'lines+markers', name: 'Actual', line: {{ width: 3, color: '#4ECDC4' }}, marker: {{ size: 6 }} }};
                const layout = {{ title: `${{process}} - Cumulative Planned vs Actual (Daily)`, xaxis: {{ title: 'Date' }}, yaxis: {{ title: 'Cumulative Quantity' }}, height: 450, hovermode: 'x unified' }};
                Plotly.newPlot(`chart-${{process}}`, [trace1, trace2], layout);
            }});
        }}
        
        populateFilters(); updateCharts();
    </script>
</body>
</html>"""
    
    return html_content

# ========================================
# CUSTOM CSS
# ========================================

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ========================================
# HEADER
# ========================================

st.markdown('<div class="main-header">📊 Production Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your production report to view interactive analytics</div>', unsafe_allow_html=True)

# ========================================
# LOAD SAVED FILE (IF EXISTS)
# ========================================

saved_file_path, saved_metadata = load_saved_file()

# Display info about currently loaded file
if saved_metadata is not None:
    st.markdown(f"""
    <div class="info-box">
        <strong>📂 Currently Loaded File:</strong> {saved_metadata['filename']}<br>
        <strong>📅 Uploaded:</strong> {saved_metadata['upload_time']}<br>
        <strong>💾 Size:</strong> {saved_metadata['file_size'] / 1024:.1f} KB<br>
        <em>This file is automatically loaded for all users. Upload a new file to update.</em>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ========================================
# FILE UPLOAD SECTION
# ========================================

st.markdown("### 📁 Upload Production Report")

col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choose your production report Excel file (or use the currently loaded file above)",
        type=['xlsx'],
        help="Upload a new Excel file to update the analytics for all users"
    )

with col2:
    if saved_metadata is not None:
        if st.button("🗑️ Clear Saved File", help="Remove the currently saved file and start fresh"):
            if clear_saved_file():
                st.success("✅ Saved file cleared!")
                st.rerun()

# ========================================
# DETERMINE WHICH FILE TO USE
# ========================================

file_to_use = None
file_source = None

if uploaded_file is not None:
    # User uploaded a new file
    file_to_use = uploaded_file
    file_source = "newly_uploaded"
    
    # Save the new file
    if save_uploaded_file(uploaded_file):
        st.success(f"✅ File saved! This file will now be loaded automatically for all users.")
elif saved_file_path is not None:
    # Use the previously saved file
    file_to_use = saved_file_path
    file_source = "previously_saved"

# ========================================
# PROCESS THE FILE
# ========================================

data = None
analytics_option = None

if file_to_use is not None:
    try:
        # Read the Excel file
        if file_source == "newly_uploaded":
            excel_file = pd.ExcelFile(file_to_use)
        else:
            excel_file = pd.ExcelFile(file_to_use)
        
        # Get all sheet names (these are the style numbers)
        sheet_names = excel_file.sheet_names
        
        if file_source == "newly_uploaded":
            st.success(f"✅ New file loaded successfully! Found {len(sheet_names)} style(s)")
        else:
            st.info(f"📂 Loaded previously saved file. Found {len(sheet_names)} style(s)")
        
        # Read all sheets into a combined dataframe
        all_data = []
        for sheet in sheet_names:
            if file_source == "newly_uploaded":
                df = pd.read_excel(file_to_use, sheet_name=sheet)
            else:
                df = pd.read_excel(file_to_use, sheet_name=sheet)
            df['Style'] = sheet  # Add style column
            all_data.append(df)
        
        # Combine all data
        data = pd.concat(all_data, ignore_index=True)
        
        # Convert Date column to datetime
        data['Date'] = pd.to_datetime(data['Date'], format='%d/%b/%y', errors='coerce')
        
        # Remove rows with invalid dates
        data = data.dropna(subset=['Date'])
        
        # Sort by date
        data = data.sort_values('Date')
        
        st.markdown("---")
        
        # Sidebar for navigation
        st.sidebar.title("📊 Navigation")
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Select Analytics View")
        analytics_option = st.sidebar.radio(
            "Choose visualization:",
            [
                "📊 Daily Actual Production Tracking",
                "📈 Cumulative Planned vs Actual",
                "📉 Daily Planned vs Actual",
                "🎯 Production Completion Percentage",
                "📅 Production Days Analysis"
            ],
            label_visibility="collapsed"
        )
        
        # Download button
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📥 Download Report")
        if st.sidebar.button("💾 Generate Offline HTML Report", use_container_width=True):
            with st.spinner("🔄 Generating report..."):
                html_content = generate_html_report(data)
                st.sidebar.download_button(
                    label="📥 Download HTML File",
                    data=html_content,
                    file_name=f"Production_Analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True
                )
                st.sidebar.success("✅ Report ready! Click above to download.")
        st.sidebar.markdown("<small>💡 The HTML report works offline with interactive filters!</small>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        st.error("The saved file may be corrupted. Please upload a new file or clear the saved file.")
        data = None

# ========================================
# MAIN ANALYTICS CONTENT
# ========================================

if data is not None and analytics_option is not None:
    
    # Define process names and colors
    processes = ['Cutting', 'Sewing', 'Washing', 'Finishing', 'Packing']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # ========================================
    # OPTION 1: Daily Actual Production Tracking
    # ========================================
    if analytics_option == "📊 Daily Actual Production Tracking":
        st.markdown('<div class="main-header">📊 Daily Actual Production Tracking</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Track actual production quantities across all processes</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Filters
        st.markdown("### Filters")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            selected_styles = st.multiselect(
                "Style",
                options=sorted(data['Style'].unique()),
                default=sorted(data['Style'].unique())
            )
        
        with col2:
            selected_pos = st.multiselect(
                "PO",
                options=sorted(data['PO'].unique()),
                default=sorted(data['PO'].unique())
            )
        
        with col3:
            selected_colours = st.multiselect(
                "Colour",
                options=sorted(data['Colour'].unique()),
                default=sorted(data['Colour'].unique())
            )
        
        with col4:
            date_range = st.date_input(
                "Date Range",
                value=(data['Date'].min(), data['Date'].max())
            )
        
        st.markdown("---")
        
        # Filter data
        filtered_data = data[
            (data['Style'].isin(selected_styles)) &
            (data['PO'].isin(selected_pos)) &
            (data['Colour'].isin(selected_colours)) &
            (data['Date'] >= pd.to_datetime(date_range[0])) &
            (data['Date'] <= pd.to_datetime(date_range[1]))
        ]
        
        if len(filtered_data) == 0:
            st.warning("⚠️ No data matches the selected filters")
        else:
            # Group by date and sum actual quantities
            daily_production = filtered_data.groupby('Date').agg({
                'Actual Cutting': 'sum',
                'Actual Sewing': 'sum',
                'Actual Washing': 'sum',
                'Actual Finishing': 'sum',
                'Actual Packing': 'sum'
            }).reset_index()
            
            # Create bar chart
            fig = go.Figure()
            
            for i, process in enumerate(processes):
                fig.add_trace(go.Bar(
                    x=daily_production['Date'],
                    y=daily_production[f'Actual {process}'],
                    name=process,
                    marker_color=colors[i]
                ))
            
            fig.update_layout(
                title="Daily Actual Production by Process",
                xaxis_title="Date",
                yaxis_title="Quantity",
                barmode='group',
                height=600,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # ========================================
    # OPTION 2: Cumulative Planned vs Actual
    # ========================================
    elif analytics_option == "📈 Cumulative Planned vs Actual":
        st.markdown('<div class="main-header">📈 Cumulative Planned vs Actual Production</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Compare cumulative planned and actual production over time (Style/PO/Colour level)</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Filters
        st.markdown("### Filters")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            selected_style = st.selectbox(
                "Select Style",
                options=sorted(data['Style'].unique()),
                key="cumulative_style"
            )
        
        # Get POs and Colours for selected style
        style_data = data[data['Style'] == selected_style]
        
        with col2:
            selected_pos_cumulative = st.multiselect(
                "PO",
                options=sorted(style_data['PO'].unique()),
                default=sorted(style_data['PO'].unique()),
                key="cumulative_po"
            )
        
        with col3:
            selected_colours_cumulative = st.multiselect(
                "Colour",
                options=sorted(style_data['Colour'].unique()),
                default=sorted(style_data['Colour'].unique()),
                key="cumulative_colour"
            )
        
        with col4:
            date_range = st.date_input(
                "Date Range",
                value=(data['Date'].min(), data['Date'].max()),
                key="cumulative_date"
            )
        
        with col5:
            view_mode = st.radio(
                "View Mode",
                options=["Daily", "Weekly", "Monthly"],
                horizontal=True
            )
        
        st.markdown("---")
        
        # Filter data
        filtered_data = data[
            (data['Style'] == selected_style) &
            (data['PO'].isin(selected_pos_cumulative)) &
            (data['Colour'].isin(selected_colours_cumulative)) &
            (data['Date'] >= pd.to_datetime(date_range[0])) &
            (data['Date'] <= pd.to_datetime(date_range[1]))
        ]
        
        if len(filtered_data) == 0:
            st.warning("⚠️ No data matches the selected filters")
        else:
            if view_mode == "Daily":
                # Get all unique Style/PO/Colour combinations
                combinations = filtered_data[['Style', 'PO', 'Colour']].drop_duplicates()
                
                # Get all unique dates in the filtered range (sorted)
                all_dates = pd.date_range(
                    start=filtered_data['Date'].min(),
                    end=filtered_data['Date'].max(),
                    freq='D'
                )
                
                # Initialize result list
                result_data = []
                
                # For each date
                for current_date in all_dates:
                    date_totals = {
                        'Date': current_date,
                        'Cumulative Planned Cutting': 0,
                        'Cumulative Actual Cutting': 0,
                        'Cumulative Planned Sewing': 0,
                        'Cumulative Actual Sewing': 0,
                        'Cumulative Planned Washing': 0,
                        'Cumulative Actual Washing': 0,
                        'Cumulative Planned Finishing': 0,
                        'Cumulative Actual Finishing': 0,
                        'Cumulative Planned Packing': 0,
                        'Cumulative Actual Packing': 0
                    }
                    
                    # For each combination
                    for _, combo in combinations.iterrows():
                        style = combo['Style']
                        po = combo['PO']
                        colour = combo['Colour']
                        
                        # Get data for this combination up to current_date
                        combo_data = filtered_data[
                            (filtered_data['Style'] == style) &
                            (filtered_data['PO'] == po) &
                            (filtered_data['Colour'] == colour) &
                            (filtered_data['Date'] <= current_date)
                        ]
                        
                        # If data exists, get the last row (most recent date <= current_date)
                        if len(combo_data) > 0:
                            last_row = combo_data.sort_values('Date').iloc[-1]
                            
                            # Add cumulative values to totals
                            for process in processes:
                                date_totals[f'Cumulative Planned {process}'] += last_row[f'Cumulative Planned {process}']
                                date_totals[f'Cumulative Actual {process}'] += last_row[f'Cumulative Actual {process}']
                    
                    result_data.append(date_totals)
                
                # Convert to dataframe
                cumulative_data = pd.DataFrame(result_data)
                
                # Create line charts for each process
                for process in processes:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=cumulative_data['Date'],
                        y=cumulative_data[f'Cumulative Planned {process}'],
                        mode='lines+markers',
                        name=f'Planned',
                        line=dict(dash='dash', width=3, color='#FF6B6B'),
                        marker=dict(size=6)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=cumulative_data['Date'],
                        y=cumulative_data[f'Cumulative Actual {process}'],
                        mode='lines+markers',
                        name=f'Actual',
                        line=dict(width=3, color='#4ECDC4'),
                        marker=dict(size=6)
                    ))
                    
                    fig.update_layout(
                        title=f"{process} - Cumulative Planned vs Actual (Daily)",
                        xaxis_title="Date",
                        yaxis_title="Cumulative Quantity",
                        height=450,
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            elif view_mode == "Weekly":
                # Get all unique Style/PO/Colour combinations
                combinations = filtered_data[['Style', 'PO', 'Colour']].drop_duplicates()
                
                # Add week column to filtered data
                filtered_data_with_week = filtered_data.copy()
                filtered_data_with_week['Week'] = filtered_data_with_week['Date'].dt.to_period('W')
                
                # Get all unique weeks
                all_weeks = sorted(filtered_data_with_week['Week'].unique())
                
                # Initialize result list
                result_data = []
                
                # For each week
                for current_week in all_weeks:
                    # Get the last date of this week from the data
                    week_dates = filtered_data_with_week[filtered_data_with_week['Week'] == current_week]['Date']
                    if len(week_dates) > 0:
                        last_date_in_week = week_dates.max()
                    else:
                        continue
                    
                    week_totals = {
                        'Week': str(current_week),
                        'Cumulative Planned Cutting': 0,
                        'Cumulative Actual Cutting': 0,
                        'Cumulative Planned Sewing': 0,
                        'Cumulative Actual Sewing': 0,
                        'Cumulative Planned Washing': 0,
                        'Cumulative Actual Washing': 0,
                        'Cumulative Planned Finishing': 0,
                        'Cumulative Actual Finishing': 0,
                        'Cumulative Planned Packing': 0,
                        'Cumulative Actual Packing': 0
                    }
                    
                    # For each combination
                    for _, combo in combinations.iterrows():
                        style = combo['Style']
                        po = combo['PO']
                        colour = combo['Colour']
                        
                        # Get data for this combination up to last date of current week
                        combo_data = filtered_data[
                            (filtered_data['Style'] == style) &
                            (filtered_data['PO'] == po) &
                            (filtered_data['Colour'] == colour) &
                            (filtered_data['Date'] <= last_date_in_week)
                        ]
                        
                        # If data exists, get the last row
                        if len(combo_data) > 0:
                            last_row = combo_data.sort_values('Date').iloc[-1]
                            
                            # Add cumulative values to totals
                            for process in processes:
                                week_totals[f'Cumulative Planned {process}'] += last_row[f'Cumulative Planned {process}']
                                week_totals[f'Cumulative Actual {process}'] += last_row[f'Cumulative Actual {process}']
                    
                    result_data.append(week_totals)
                
                # Convert to dataframe
                weekly_data = pd.DataFrame(result_data)
                
                # Create bar charts for each process
                for process in processes:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=weekly_data['Week'],
                        y=weekly_data[f'Cumulative Planned {process}'],
                        name='Planned',
                        marker_color='#FF6B6B'
                    ))
                    
                    fig.add_trace(go.Bar(
                        x=weekly_data['Week'],
                        y=weekly_data[f'Cumulative Actual {process}'],
                        name='Actual',
                        marker_color='#4ECDC4'
                    ))
                    
                    fig.update_layout(
                        title=f"{process} - Cumulative Planned vs Actual (Weekly)",
                        xaxis_title="Week",
                        yaxis_title="Cumulative Quantity",
                        height=450,
                        barmode='group',
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            else:  # Monthly view
                # Get all unique Style/PO/Colour combinations
                combinations = filtered_data[['Style', 'PO', 'Colour']].drop_duplicates()
                
                # Add month column to filtered data
                filtered_data_with_month = filtered_data.copy()
                filtered_data_with_month['Month'] = filtered_data_with_month['Date'].dt.to_period('M')
                
                # Get all unique months
                all_months = sorted(filtered_data_with_month['Month'].unique())
                
                # Initialize result list
                result_data = []
                
                # For each month
                for current_month in all_months:
                    # Get the last date of this month from the data
                    month_dates = filtered_data_with_month[filtered_data_with_month['Month'] == current_month]['Date']
                    if len(month_dates) > 0:
                        last_date_in_month = month_dates.max()
                    else:
                        continue
                    
                    month_totals = {
                        'Month': str(current_month),
                        'Cumulative Planned Cutting': 0,
                        'Cumulative Actual Cutting': 0,
                        'Cumulative Planned Sewing': 0,
                        'Cumulative Actual Sewing': 0,
                        'Cumulative Planned Washing': 0,
                        'Cumulative Actual Washing': 0,
                        'Cumulative Planned Finishing': 0,
                        'Cumulative Actual Finishing': 0,
                        'Cumulative Planned Packing': 0,
                        'Cumulative Actual Packing': 0
                    }
                    
                    # For each combination
                    for _, combo in combinations.iterrows():
                        style = combo['Style']
                        po = combo['PO']
                        colour = combo['Colour']
                        
                        # Get data for this combination up to last date of current month
                        combo_data = filtered_data[
                            (filtered_data['Style'] == style) &
                            (filtered_data['PO'] == po) &
                            (filtered_data['Colour'] == colour) &
                            (filtered_data['Date'] <= last_date_in_month)
                        ]
                        
                        # If data exists, get the last row
                        if len(combo_data) > 0:
                            last_row = combo_data.sort_values('Date').iloc[-1]
                            
                            # Add cumulative values to totals
                            for process in processes:
                                month_totals[f'Cumulative Planned {process}'] += last_row[f'Cumulative Planned {process}']
                                month_totals[f'Cumulative Actual {process}'] += last_row[f'Cumulative Actual {process}']
                    
                    result_data.append(month_totals)
                
                # Convert to dataframe
                monthly_data = pd.DataFrame(result_data)
                
                # Create bar charts for each process
                for process in processes:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=monthly_data['Month'],
                        y=monthly_data[f'Cumulative Planned {process}'],
                        name='Planned',
                        marker_color='#FF6B6B'
                    ))
                    
                    fig.add_trace(go.Bar(
                        x=monthly_data['Month'],
                        y=monthly_data[f'Cumulative Actual {process}'],
                        name='Actual',
                        marker_color='#4ECDC4'
                    ))
                    
                    fig.update_layout(
                        title=f"{process} - Cumulative Planned vs Actual (Monthly)",
                        xaxis_title="Month",
                        yaxis_title="Cumulative Quantity",
                        height=450,
                        barmode='group',
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    # ========================================
    # OPTION 3: Daily Planned vs Actual
    # ========================================
    elif analytics_option == "📉 Daily Planned vs Actual":
        st.markdown('<div class="main-header">📉 Daily Planned vs Actual Production</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Compare daily planned and actual production quantities</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Filters
        st.markdown("### Filters")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            selected_styles = st.multiselect(
                "Style",
                options=sorted(data['Style'].unique()),
                default=sorted(data['Style'].unique()),
                key="daily_style"
            )
        
        with col2:
            selected_pos = st.multiselect(
                "PO",
                options=sorted(data['PO'].unique()),
                default=sorted(data['PO'].unique()),
                key="daily_po"
            )
        
        with col3:
            selected_colours = st.multiselect(
                "Colour",
                options=sorted(data['Colour'].unique()),
                default=sorted(data['Colour'].unique()),
                key="daily_colour"
            )
        
        with col4:
            date_range = st.date_input(
                "Date Range",
                value=(data['Date'].min(), data['Date'].max()),
                key="daily_date"
            )
        
        with col5:
            view_mode_daily = st.radio(
                "View Mode",
                options=["Daily", "Weekly", "Monthly"],
                horizontal=True,
                key="daily_view_mode"
            )
        
        st.markdown("---")
        
        # Filter data
        filtered_data = data[
            (data['Style'].isin(selected_styles)) &
            (data['PO'].isin(selected_pos)) &
            (data['Colour'].isin(selected_colours)) &
            (data['Date'] >= pd.to_datetime(date_range[0])) &
            (data['Date'] <= pd.to_datetime(date_range[1]))
        ]
        
        if len(filtered_data) == 0:
            st.warning("⚠️ No data matches the selected filters")
        else:
            if view_mode_daily == "Daily":
                # Group by date and sum quantities
                daily_comparison = filtered_data.groupby('Date').agg({
                    'Planned Cutting': 'sum',
                    'Actual Cutting': 'sum',
                    'Planned Sewing': 'sum',
                    'Actual Sewing': 'sum',
                    'Planned Washing': 'sum',
                    'Actual Washing': 'sum',
                    'Planned Finishing': 'sum',
                    'Actual Finishing': 'sum',
                    'Planned Packing': 'sum',
                    'Actual Packing': 'sum'
                }).reset_index()
                
                # Create line charts for each process
                for process in processes:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=daily_comparison['Date'],
                        y=daily_comparison[f'Planned {process}'],
                        mode='lines+markers',
                        name='Planned',
                        line=dict(dash='dash', width=2, color='#FF6B6B'),
                        marker=dict(size=6)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=daily_comparison['Date'],
                        y=daily_comparison[f'Actual {process}'],
                        mode='lines+markers',
                        name='Actual',
                        line=dict(width=2, color='#4ECDC4'),
                        marker=dict(size=6)
                    ))
                    
                    fig.update_layout(
                        title=f"{process} - Daily Planned vs Actual",
                        xaxis_title="Date",
                        yaxis_title="Quantity",
                        height=450,
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            elif view_mode_daily == "Weekly":
                # Add week column
                filtered_data_copy = filtered_data.copy()
                filtered_data_copy['Week'] = filtered_data_copy['Date'].dt.to_period('W')
                
                # Group by week and sum quantities
                weekly_comparison = filtered_data_copy.groupby('Week').agg({
                    'Planned Cutting': 'sum',
                    'Actual Cutting': 'sum',
                    'Planned Sewing': 'sum',
                    'Actual Sewing': 'sum',
                    'Planned Washing': 'sum',
                    'Actual Washing': 'sum',
                    'Planned Finishing': 'sum',
                    'Actual Finishing': 'sum',
                    'Planned Packing': 'sum',
                    'Actual Packing': 'sum'
                }).reset_index()
                
                # Convert period to string for display
                weekly_comparison['Week'] = weekly_comparison['Week'].astype(str)
                
                # Create grouped bar charts for each process
                for process in processes:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=weekly_comparison['Week'],
                        y=weekly_comparison[f'Planned {process}'],
                        name='Planned',
                        marker_color='#FF6B6B'
                    ))
                    
                    fig.add_trace(go.Bar(
                        x=weekly_comparison['Week'],
                        y=weekly_comparison[f'Actual {process}'],
                        name='Actual',
                        marker_color='#4ECDC4'
                    ))
                    
                    fig.update_layout(
                        title=f"{process} - Weekly Planned vs Actual",
                        xaxis_title="Week",
                        yaxis_title="Quantity",
                        height=450,
                        barmode='group',
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            else:  # Monthly view
                # Add month column
                filtered_data_copy = filtered_data.copy()
                filtered_data_copy['Month'] = filtered_data_copy['Date'].dt.to_period('M')
                
                # Group by month and sum quantities
                monthly_comparison = filtered_data_copy.groupby('Month').agg({
                    'Planned Cutting': 'sum',
                    'Actual Cutting': 'sum',
                    'Planned Sewing': 'sum',
                    'Actual Sewing': 'sum',
                    'Planned Washing': 'sum',
                    'Actual Washing': 'sum',
                    'Planned Finishing': 'sum',
                    'Actual Finishing': 'sum',
                    'Planned Packing': 'sum',
                    'Actual Packing': 'sum'
                }).reset_index()
                
                # Convert period to string for display
                monthly_comparison['Month'] = monthly_comparison['Month'].astype(str)
                
                # Create grouped bar charts for each process
                for process in processes:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=monthly_comparison['Month'],
                        y=monthly_comparison[f'Planned {process}'],
                        name='Planned',
                        marker_color='#FF6B6B'
                    ))
                    
                    fig.add_trace(go.Bar(
                        x=monthly_comparison['Month'],
                        y=monthly_comparison[f'Actual {process}'],
                        name='Actual',
                        marker_color='#4ECDC4'
                    ))
                    
                    fig.update_layout(
                        title=f"{process} - Monthly Planned vs Actual",
                        xaxis_title="Month",
                        yaxis_title="Quantity",
                        height=450,
                        barmode='group',
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    # ========================================
    # OPTION 4: Production Completion Percentage
    # ========================================
    elif analytics_option == "🎯 Production Completion Percentage":
        st.markdown('<div class="main-header">🎯 Production Completion Percentage</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Track completion percentage for each production process (Style/PO/Colour level)</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Filters
        st.markdown("### Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_style = st.selectbox(
                "Select Style",
                options=sorted(data['Style'].unique()),
                key="completion_style"
            )
        
        # Get POs and Colours for selected style
        style_data_for_filters = data[data['Style'] == selected_style]
        
        with col2:
            selected_pos_completion = st.multiselect(
                "PO",
                options=sorted(style_data_for_filters['PO'].unique()),
                default=sorted(style_data_for_filters['PO'].unique()),
                key="completion_po"
            )
        
        with col3:
            selected_colours_completion = st.multiselect(
                "Colour",
                options=sorted(style_data_for_filters['Colour'].unique()),
                default=sorted(style_data_for_filters['Colour'].unique()),
                key="completion_colour"
            )
        
        st.markdown("---")
        
        # Check if any filters are selected
        if len(selected_pos_completion) == 0 or len(selected_colours_completion) == 0:
            st.warning("⚠️ Please select at least one PO and one Colour")
        else:
            # Initialize accumulators for totals
            total_planned = {process: 0 for process in processes}
            total_actual = {process: 0 for process in processes}
            latest_date = None
            combinations_found = 0
            
            # Process each Style/PO/Colour combination
            for po in selected_pos_completion:
                for colour in selected_colours_completion:
                    # Filter for this specific combination
                    combo_data = data[
                        (data['Style'] == selected_style) &
                        (data['PO'] == po) &
                        (data['Colour'] == colour)
                    ]
                    
                    # Check if this combination has data
                    if len(combo_data) > 0:
                        combinations_found += 1
                        
                        # Get the last row (most recent date) for this combination
                        last_row = combo_data.sort_values('Date').iloc[-1]
                        
                        # Track the latest date across all combinations
                        if latest_date is None or last_row['Date'] > latest_date:
                            latest_date = last_row['Date']
                        
                        # Add cumulative values from this combination to totals
                        for process in processes:
                            total_planned[process] += last_row[f'Cumulative Planned {process}']
                            total_actual[process] += last_row[f'Cumulative Actual {process}']
            
            # Check if any combinations were found
            if combinations_found == 0:
                st.warning("⚠️ No data found for the selected Style/PO/Colour combinations")
            else:
                # Calculate completion percentages from totals
                progress_data = []
                for process in processes:
                    planned = total_planned[process]
                    actual = total_actual[process]
                    
                    if planned > 0:
                        percentage = (actual / planned) * 100
                    else:
                        percentage = 0
                    
                    remaining = planned - actual
                    
                    progress_data.append({
                        'Process': process,
                        'Planned': int(planned),
                        'Actual': int(actual),
                        'Remaining': int(remaining),
                        'Percentage': round(percentage, 1)
                    })
                
                progress_df = pd.DataFrame(progress_data)
                
                # Display as a styled table
                st.markdown(f"### Progress Summary for Style: **{selected_style}**")
                if len(selected_pos_completion) == 1 and len(selected_colours_completion) == 1:
                    st.markdown(f"**PO:** {selected_pos_completion[0]} | **Colour:** {selected_colours_completion[0]}")
                else:
                    pos_list = ', '.join(str(x) for x in selected_pos_completion)
                    colour_list = ', '.join(str(x) for x in selected_colours_completion)
                    st.markdown(f"**POs:** {pos_list} | **Colours:** {colour_list}")
                st.markdown(f"*As of {latest_date.strftime('%d %B %Y')}*")
                st.markdown("")
                
                # Create a more detailed table with styling
                styled_df = progress_df[['Process', 'Actual', 'Planned', 'Remaining', 'Percentage']].copy()
                styled_df['Percentage'] = styled_df['Percentage'].apply(lambda x: f"{x}%")
                
                # Display the table with custom styling
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Process": st.column_config.TextColumn("Process", width="medium"),
                        "Actual": st.column_config.NumberColumn("Actual", width="small", format="%d"),
                        "Planned": st.column_config.NumberColumn("Planned", width="small", format="%d"),
                        "Remaining": st.column_config.NumberColumn("Remaining", width="small", format="%d"),
                        "Percentage": st.column_config.TextColumn("Completion %", width="small")
                    }
                )
    
    # ========================================
    # OPTION 5: Production Days Analysis
    # ========================================
    elif analytics_option == "📅 Production Days Analysis":
        st.markdown('<div class="main-header">📅 Production Days Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Track production days vs non-production days per month (excluding Sundays)</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Get the date range from the data
        min_date = data['Date'].min()
        max_date = data['Date'].max()
        
        # Get all unique dates where production happened
        production_dates = set(data['Date'].dt.date)
        
        # Create a complete date range
        all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
        
        # Analyze by month
        monthly_analysis = []
        
        for year_month in pd.period_range(start=min_date, end=max_date, freq='M'):
            # Get all dates in this month
            month_start = year_month.to_timestamp()
            month_end = (year_month + 1).to_timestamp() - pd.Timedelta(days=1)
            
            # Get all dates in the month
            month_dates = pd.date_range(start=month_start, end=month_end, freq='D')
            
            # Count working days (exclude Sundays)
            working_days = [d for d in month_dates if d.dayofweek != 6]  # 6 = Sunday
            total_working_days = len(working_days)
            
            # Count production days (exclude Sundays)
            production_days_count = sum(1 for d in working_days if d.date() in production_dates)
            
            # Count non-production days
            non_production_days_count = total_working_days - production_days_count
            
            monthly_analysis.append({
                'Month': year_month.strftime('%b %Y'),
                'Total Working Days': total_working_days,
                'Production Days': production_days_count,
                'Non-Production Days': non_production_days_count,
                'Production Rate': f"{(production_days_count / total_working_days * 100):.1f}%" if total_working_days > 0 else "0%"
            })
        
        # Create dataframe
        analysis_df = pd.DataFrame(monthly_analysis)
        
        # Display summary table
        st.markdown("### Monthly Production Days Summary")
        st.markdown("*Sundays are excluded from the analysis*")
        st.markdown("")
        
        st.dataframe(
            analysis_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Month": st.column_config.TextColumn("Month", width="medium"),
                "Total Working Days": st.column_config.NumberColumn("Total Working Days", width="small", format="%d"),
                "Production Days": st.column_config.NumberColumn("Production Days", width="small", format="%d"),
                "Non-Production Days": st.column_config.NumberColumn("Non-Production Days", width="small", format="%d"),
                "Production Rate": st.column_config.TextColumn("Production Rate", width="small")
            }
        )
        
        st.markdown("---")
        
        # Create bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=analysis_df['Month'],
            y=analysis_df['Production Days'],
            name='Production Days',
            marker_color='#4ECDC4',
            text=analysis_df['Production Days'],
            textposition='inside'
        ))
        
        fig.add_trace(go.Bar(
            x=analysis_df['Month'],
            y=analysis_df['Non-Production Days'],
            name='Non-Production Days',
            marker_color='#FF6B6B',
            text=analysis_df['Non-Production Days'],
            textposition='inside'
        ))
        
        fig.update_layout(
            title="Production Days vs Non-Production Days by Month",
            xaxis_title="Month",
            yaxis_title="Number of Days",
            barmode='stack',
            height=500,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Create production rate line chart
        fig2 = go.Figure()
        
        # Extract numeric production rate
        production_rate_numeric = [float(rate.strip('%')) for rate in analysis_df['Production Rate']]
        
        fig2.add_trace(go.Scatter(
            x=analysis_df['Month'],
            y=production_rate_numeric,
            mode='lines+markers',
            name='Production Rate',
            line=dict(width=3, color='#2ca02c'),
            marker=dict(size=10),
            text=[f"{rate}%" for rate in production_rate_numeric],
            textposition='top center'
        ))
        
        fig2.update_layout(
            title="Production Rate Trend by Month",
            xaxis_title="Month",
            yaxis_title="Production Rate (%)",
            height=400,
            hovermode='x unified',
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig2, use_container_width=True)

else:
    # Show message when no file is available
    if saved_metadata is None:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ No file loaded</strong><br>
            Please upload a production report Excel file to view analytics.<br>
            Once uploaded, the file will be automatically loaded for all users.
        </div>
        """, unsafe_allow_html=True)
    
    # Show available analytics
    st.markdown("### Available Analytics:")
    st.markdown("""
    - **📊 Daily Actual Production Tracking** - Bar chart showing actual production by process
    - **📈 Cumulative Planned vs Actual** - Line/Bar charts comparing cumulative targets vs reality (Daily/Monthly views)
    - **📉 Daily Planned vs Actual** - Line charts for day-to-day comparison
    - **🎯 Production Completion Percentage** - Table showing completion percentage for each process
    - **📅 Production Days Analysis** - Track production days vs non-production days per month
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>Production Analytics Dashboard v2.2 (with File Persistence)</p>
</div>
""", unsafe_allow_html=True)
