import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import io
from reportlab.lib import colors as rl_colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import tempfile
import os
import time
import requests
from urllib.parse import urlparse

# Page configuration
st.set_page_config(
    page_title="Grade Management System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for splash screen and recent files
if 'splash_shown' not in st.session_state:
    st.session_state.splash_shown = False

if 'recent_files' not in st.session_state:
    st.session_state.recent_files = []

# Function to add file to recent list
def add_to_recent(file_name, sheet_name, rows, cols):
    """Add file to recent files list"""
    from datetime import datetime
    
    # Create file info
    file_info = {
        'name': file_name,
        'sheet': sheet_name,
        'rows': rows,
        'cols': cols,
        'time': datetime.now().strftime('%H:%M:%S'),
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Remove if already exists (to avoid duplicates)
    st.session_state.recent_files = [f for f in st.session_state.recent_files if f['name'] != file_name]
    
    # Add to beginning of list
    st.session_state.recent_files.insert(0, file_info)
    
    # Keep only last 10 files
    if len(st.session_state.recent_files) > 10:
        st.session_state.recent_files = st.session_state.recent_files[:10]

# Custom CSS for animations and recent files
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&family=Playfair+Display:wght@400;700&family=Poppins:wght@300;400;500;600&display=swap');
    
    @keyframes fadeInScale {
        0% { opacity: 0; transform: scale(0.8); }
        50% { opacity: 0.8; transform: scale(1.05); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes slideInLeft {
        0% { opacity: 0; transform: translateX(-50px); }
        100% { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInRight {
        0% { opacity: 0; transform: translateX(50px); }
        100% { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-title h1 { font-size: 32px; }
        .splash-title { font-size: 42px; }
        .splash-subtitle { font-size: 18px; }
        .stat-card h3 { font-size: 24px; }
    }
    
    .splash-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientFlow 5s ease infinite;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        font-family: 'Playfair Display', serif;
    }
    
    .splash-content {
        text-align: center;
        color: white;
        animation: fadeInScale 2s ease-out;
        padding: 20px;
    }
    
    .splash-title {
        font-size: 72px;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        letter-spacing: 2px;
        font-family: 'Playfair Display', serif;
    }
    
    .splash-subtitle {
        font-size: 24px;
        font-weight: 300;
        margin: 10px 0 0 0;
        opacity: 0.9;
        font-family: 'Montserrat', sans-serif;
        letter-spacing: 1px;
    }
    
    .splash-loader {
        margin-top: 40px;
        font-size: 18px;
        font-family: 'Montserrat', sans-serif;
        animation: pulse 1.5s ease infinite;
    }
    
    .main-title {
        text-align: center;
        padding: 20px 0;
        margin-bottom: 30px;
        border-bottom: 2px solid #2c3e50;
        animation: slideInLeft 1s ease-out;
    }
    
    .main-title h1 {
        font-family: 'Playfair Display', serif;
        font-size: 48px;
        font-weight: 700;
        color: #2c3e50;
        margin: 0;
        letter-spacing: 1px;
        background: linear-gradient(45deg, #2c3e50, #3498db, #9b59b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% 200%;
        animation: gradientFlow 5s ease infinite;
    }
    
    .main-title p {
        font-family: 'Poppins', sans-serif;
        font-size: 16px;
        font-weight: 300;
        color: #7f8c8d;
        margin: 5px 0 0 0;
    }
    
    .upload-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: slideInRight 1s ease-out;
    }
    
    .upload-section h3 {
        font-family: 'Montserrat', sans-serif;
        font-size: 20px;
        font-weight: 500;
        margin: 0 0 10px 0;
    }
    
    .upload-section p {
        font-family: 'Poppins', sans-serif;
        font-size: 14px;
        margin: 5px 0;
        opacity: 0.9;
    }
    
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 600;
        color: #2c3e50;
        padding: 15px 0;
        margin: 30px 0 20px 0;
        position: relative;
        animation: slideInLeft 1s ease-out;
    }
    
    .section-header:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100px;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 3px;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: slideInRight 1s ease-out;
        margin: 10px 0;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4);
    }
    
    .stat-card h4 {
        font-family: 'Montserrat', sans-serif;
        font-size: 14px;
        font-weight: 400;
        margin: 0 0 10px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.9;
    }
    
    .stat-card h3 {
        font-family: 'Playfair Display', serif;
        font-size: 32px;
        font-weight: 700;
        margin: 0;
    }
    
    .col-name-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 12px 15px;
        font-family: 'Poppins', sans-serif;
        font-size: 13px;
        font-weight: 500;
        color: white;
        margin: 5px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        transition: transform 0.3s ease;
        animation: slideInLeft 1s ease-out;
    }
    
    .col-name-box:hover {
        transform: scale(1.05);
    }
    
    .graph-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 20px 0;
        animation: slideInRight 1s ease-out;
        overflow-x: auto;
    }
    
    /* Small + button styling */
    div[data-testid="column"]:nth-child(1) button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 2px 8px;
        font-size: 20px;
        border-radius: 4px;
        cursor: pointer;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    div[data-testid="column"]:nth-child(1) button:hover {
        background-color: #218838;
        transform: scale(1.1);
    }
    
    div[data-testid="column"]:nth-child(2) button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 2px 8px;
        font-size: 20px;
        border-radius: 4px;
        cursor: pointer;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    div[data-testid="column"]:nth-child(2) button:hover {
        background-color: #0069d9;
        transform: scale(1.1);
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 80px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -40px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
        white-space: nowrap;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-family: 'Montserrat', sans-serif;
        font-size: 14px;
        font-weight: 500;
        padding: 10px 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-family: 'Montserrat', sans-serif;
        font-size: 16px;
        font-weight: 600;
        padding: 15px 30px;
        width: 100%;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    .footer {
        text-align: center;
        font-family: 'Poppins', sans-serif;
        font-size: 12px;
        color: #95a5a6;
        padding: 20px;
        animation: slideInLeft 1s ease-out;
    }
    
    /* Google Drive link input */
    .drive-input {
        margin: 20px 0;
    }
    
    /* Preview box */
    .preview-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 15px 0;
        border-radius: 5px;
    }
    
    /* Recent files card */
    .recent-file-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
        border-radius: 10px;
        padding: 12px;
        margin: 5px;
        border-left: 4px solid #667eea;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    
    .recent-file-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Function to extract Google Drive file ID
def get_gdrive_file_id(url):
    """Extract file ID from Google Drive link"""
    if 'drive.google.com' in url:
        if '/d/' in url:
            return url.split('/d/')[1].split('/')[0]
        elif 'id=' in url:
            return url.split('id=')[1].split('&')[0]
    return None

# Function to download from Google Drive
def download_from_gdrive(file_id):
    """Download file from Google Drive using file ID"""
    try:
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(download_url)
        if response.status_code == 200:
            return io.BytesIO(response.content)
    except:
        pass
    return None

# Function to find the actual data table in Excel with merged cells
def find_data_table(df_raw):
    """
    Find where the actual student data starts in a messy Excel file
    Returns (header_row, data_start_row, column_names)
    """
    expected_columns = ['S/NO', 'REG', 'NAME', 'TEST', 'PRAC', 'ASSN', 'QUIZ', 'PROJECT', 'CA']
    
    for row in range(min(30, len(df_raw))):  # Check first 30 rows
        row_values = df_raw.iloc[row].astype(str).str.upper()
        row_text = ' '.join(row_values)
        
        # Look for row that contains typical column headers
        if any(keyword in row_text for keyword in ['S/NO', 'REG.NO', 'REG NUMBER', 'FULL NAME', 'TEST', 'PRAC', 'ASSN', 'QUIZ']):
            # This is likely the header row
            header_row = row
            
            # Extract column names from this row
            col_names = []
            for col in range(len(df_raw.columns)):
                cell_value = str(df_raw.iloc[header_row, col]).strip()
                if cell_value and cell_value != 'nan' and cell_value != 'None':
                    # Clean up the column name
                    if 'S/NO' in cell_value.upper():
                        col_names.append('S/NO')
                    elif 'REG' in cell_value.upper() and 'NUMBER' in cell_value.upper():
                        col_names.append('REG. NUMBER')
                    elif 'FULL NAME' in cell_value.upper() or 'NAME' in cell_value.upper():
                        col_names.append('FULL NAME')
                    elif 'TEST 1' in cell_value.upper() or 'TEST1' in cell_value.upper():
                        col_names.append('TEST 1')
                    elif 'TEST 2' in cell_value.upper() or 'TEST2' in cell_value.upper():
                        col_names.append('TEST 2')
                    elif 'PRAC 1' in cell_value.upper() or 'PRAC1' in cell_value.upper():
                        col_names.append('PRAC 1')
                    elif 'PRAC 2' in cell_value.upper() or 'PRAC2' in cell_value.upper():
                        col_names.append('PRAC 2')
                    elif 'ASSN 1' in cell_value.upper() or 'ASSIGNMENT 1' in cell_value.upper():
                        col_names.append('ASSN 1')
                    elif 'ASSN 2' in cell_value.upper() or 'ASSIGNMENT 2' in cell_value.upper():
                        col_names.append('ASSN 2')
                    elif 'QUIZ 1' in cell_value.upper() or 'QUIZ1' in cell_value.upper():
                        col_names.append('QUIZ 1')
                    elif 'QUIZ 2' in cell_value.upper() or 'QUIZ2' in cell_value.upper():
                        col_names.append('QUIZ 2')
                    elif 'MIN PRJT' in cell_value.upper() or 'MINI PROJECT' in cell_value.upper():
                        col_names.append('MIN PRJT')
                    elif 'CA' in cell_value.upper() and len(cell_value) < 10:
                        col_names.append('CA')
                    else:
                        col_names.append(cell_value)
                else:
                    col_names.append(f'Column_{len(col_names)+1}')
            
            return header_row, header_row + 1, col_names
    
    # If no header found, return default
    return 0, 1, ['S/NO', 'REG. NUMBER', 'FULL NAME', 'TEST 1', 'TEST 2', 'PRAC 1', 'PRAC 2', 'ASSN 1', 'ASSN 2', 'QUIZ 1', 'QUIZ 2', 'MIN PRJT', 'CA']

# Function to read Excel and extract student data
def read_student_data(file):
    """
    Read Excel file and extract only student data, ignoring header rows
    """
    try:
        if isinstance(file, io.BytesIO):
            # For Google Drive files
            df_raw = pd.read_excel(file, header=None)
        else:
            # For uploaded files
            df_raw = pd.read_excel(file, header=None)
        
        # Find where the actual data starts
        header_row, data_start_row, column_names = find_data_table(df_raw)
        
        # Read from the data start row
        df = pd.read_excel(file, header=None, skiprows=data_start_row)
        
        # Keep only columns that have data
        df = df.dropna(axis=1, how='all')
        
        # Keep only rows that have at least some data
        df = df.dropna(how='all')
        
        # Limit to the number of columns we identified
        num_cols = min(len(column_names), len(df.columns))
        df = df.iloc[:, :num_cols]
        
        # Assign column names
        df.columns = column_names[:num_cols]
        
        # Remove rows where S/NO is empty or not a number
        if 'S/NO' in df.columns:
            df = df[df['S/NO'].notna()]
            # Try to convert S/NO to numeric, keep if it's a number
            try:
                df['S/NO'] = pd.to_numeric(df['S/NO'], errors='coerce')
                df = df[df['S/NO'].notna()]
            except:
                pass
        
        # Replace NaN with "-" for better display
        df = df.fillna("-")
        
        return df, "Student Data"
        
    except Exception as e:
        st.error(f"Error reading Excel: {e}")
        return pd.DataFrame(), "Error"

# Function to create PDF report with institution name
def create_pdf_report(df, graph_data, stats, graph_type, settings, graph_path):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Institution name at the top
    inst_style = ParagraphStyle(
        'Institution',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=rl_colors.Color(0.2, 0.2, 0.4),
        alignment=1,
        spaceAfter=5,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("DAR ES SALAAM INSTITUTE OF TECHNOLOGY", inst_style))
    
    # Department
    dept_style = ParagraphStyle(
        'Department',
        parent=styles['Normal'],
        fontSize=12,
        textColor=rl_colors.Color(0.4, 0.4, 0.4),
        alignment=1,
        spaceAfter=15
    )
    
    story.append(Paragraph("Department of Computer Science", dept_style))
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=rl_colors.Color(0.4, 0.4, 0.8),
        alignment=1,
        spaceAfter=10
    )
    
    story.append(Paragraph("GRADE ANALYSIS REPORT", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # File Information
    story.append(Paragraph("FILE INFORMATION", styles['Heading2']))
    file_data = [
        ["Total Students", str(len(df))],
        ["Total Columns", str(len(df.columns))],
        ["Analysis Column", stats['column']]
    ]
    
    file_table = Table(file_data, colWidths=[150, 300])
    file_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), rl_colors.Color(0.9, 0.9, 0.9)),
        ('TEXTCOLOR', (0, 0), (-1, -1), rl_colors.Color(0, 0, 0)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, rl_colors.Color(0.8, 0.8, 0.8))
    ]))
    story.append(file_table)
    story.append(Spacer(1, 20))
    
    # Graph Settings
    story.append(Paragraph("GRAPH SETTINGS", styles['Heading2']))
    settings_data = [
        ["Graph Type", graph_type],
        ["Grade Range", f"{settings['min_grade']} - {settings['max_grade']}"],
        ["Interval Size", str(settings['interval'])],
        ["Intervals", settings['bins']],
        ["Color Theme", settings['color_theme']]
    ]
    
    if graph_type == "Pie Chart" and 'pie_display' in settings:
        settings_data.append(["Pie Display", settings['pie_display']])
    
    settings_table = Table(settings_data, colWidths=[150, 300])
    settings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), rl_colors.Color(0.9, 0.9, 0.9)),
        ('TEXTCOLOR', (0, 0), (-1, -1), rl_colors.Color(0, 0, 0)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, rl_colors.Color(0.8, 0.8, 0.8))
    ]))
    story.append(settings_table)
    story.append(Spacer(1, 20))
    
    # Statistics
    story.append(Paragraph("STATISTICAL SUMMARY", styles['Heading2']))
    stats_data = [
        ["Metric", "Value"],
        ["Total Students", str(stats['total'])],
        ["Mean", f"{stats['mean']:.2f}"],
        ["Median", f"{stats['median']:.2f}"],
        ["Standard Deviation", f"{stats['std']:.2f}"],
        ["Minimum", f"{stats['min']:.2f}"],
        ["Maximum", f"{stats['max']:.2f}"]
    ]
    
    stats_table = Table(stats_data, colWidths=[150, 300])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), rl_colors.Color(0.4, 0.4, 0.8)),
        ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.Color(1, 1, 1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), rl_colors.Color(0.95, 0.95, 0.95)),
        ('GRID', (0, 0), (-1, -1), 1, rl_colors.Color(0.8, 0.8, 0.8))
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # Graph
    story.append(Paragraph(f"{graph_type} OF {stats['column']}", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    img = Image(graph_path, width=450, height=250)
    story.append(img)
    story.append(Spacer(1, 20))
    
    # Data Preview - ALL ROWS with original column names
    story.append(Paragraph("COMPLETE DATA (ALL ROWS)", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    all_data = [df.columns.tolist()]
    for index, row in df.iterrows():
        # Convert all values to string and replace NaN with "-"
        row_data = [str(val) if val != "-" else "-" for val in row.tolist()]
        all_data.append(row_data)
    
    all_table = Table(all_data)
    all_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), rl_colors.Color(0.4, 0.4, 0.8)),
        ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.Color(1, 1, 1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, rl_colors.Color(0.8, 0.8, 0.8))
    ]))
    story.append(all_table)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Total Rows: {len(df)}", styles['Normal']))
    
    # Footer with institution info
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=rl_colors.Color(0.5, 0.5, 0.5),
        alignment=1
    )
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("DAR ES SALAAM INSTITUTE OF TECHNOLOGY - Academic Records", footer_style))
    story.append(Paragraph(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Function to get color palette
def get_colors(n, theme):
    if theme == "Rainbow":
        return [plt.cm.rainbow(i/n) for i in range(n)]
    elif theme == "Blue":
        return plt.cm.Blues(np.linspace(0.4, 0.9, n))
    elif theme == "Green":
        return plt.cm.Greens(np.linspace(0.4, 0.9, n))
    elif theme == "Red":
        return plt.cm.Reds(np.linspace(0.4, 0.9, n))
    elif theme == "Purple":
        return plt.cm.Purples(np.linspace(0.4, 0.9, n))
    elif theme == "Orange":
        return plt.cm.Oranges(np.linspace(0.4, 0.9, n))

# Splash screen - shows only once
if not st.session_state.splash_shown:
    splash_placeholder = st.empty()
    
    with splash_placeholder.container():
        st.markdown("""
            <div class='splash-container'>
                <div class='splash-content'>
                    <h1 class='splash-title'>GRADE MANAGEMENT SYSTEM</h1>
                    <p class='splash-subtitle'>Advanced Analytics Dashboard</p>
                    <div class='splash-loader'>Loading amazing features...</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(5)
        splash_placeholder.empty()
        st.session_state.splash_shown = True

# Main title
st.markdown("""
    <div class='main-title'>
        <h1>GRADE MANAGEMENT SYSTEM</h1>
        <p>Advanced Analytics Dashboard</p>
    </div>
""", unsafe_allow_html=True)

# Upload section
st.markdown("""
    <div class='upload-section'>
        <h3>UPLOAD EXCEL FILE</h3>
        <p>Choose from your device or Google Drive</p>
        <p style='font-size: 12px; opacity: 0.8;'>Limit 200MB per file - XLSX, XLS</p>
    </div>
""", unsafe_allow_html=True)

# Create tabs for different upload methods
upload_tab1, upload_tab2 = st.tabs(["📁 Upload from Device", "🌐 Google Drive Link"])

uploaded_file = None

with upload_tab1:
    uploaded_file = st.file_uploader("", type=["xlsx", "xls"], label_visibility="collapsed")

with upload_tab2:
    st.markdown('<div class="drive-input">', unsafe_allow_html=True)
    drive_link = st.text_input("Paste Google Drive link here:", placeholder="https://drive.google.com/file/d/...")
    
    if drive_link:
        file_id = get_gdrive_file_id(drive_link)
        if file_id:
            with st.spinner("Downloading from Google Drive..."):
                file_content = download_from_gdrive(file_id)
                if file_content:
                    uploaded_file = file_content
                    st.success("File downloaded successfully!")
                else:
                    st.error("Failed to download file. Make sure the link is public.")
        else:
            st.error("Invalid Google Drive link")

# Recent Files Section
if st.session_state.recent_files:
    st.markdown("<div class='section-header'>RECENT FILES</div>", unsafe_allow_html=True)
    
    # Create columns for recent files display
    recent_cols = st.columns(5)
    
    for i, file_info in enumerate(st.session_state.recent_files[:5]):
        with recent_cols[i]:
            # Create a card for each recent file
            st.markdown(f"""
                <div class='recent-file-card'>
                    <div style='font-family: Montserrat; font-size: 12px; color: #2c3e50; font-weight: 600;'>
                        📁 {file_info['name'][:15]}...
                    </div>
                    <div style='font-family: Poppins; font-size: 10px; color: #7f8c8d; margin-top: 5px;'>
                        {file_info['rows']} rows • {file_info['cols']} cols
                    </div>
                    <div style='font-family: Poppins; font-size: 9px; color: #95a5a6; margin-top: 3px;'>
                        {file_info['date']} at {file_info['time']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Main program logic
if uploaded_file is not None:
    try:
        # Read Excel file and extract only student data
        df, sheet_name = read_student_data(uploaded_file)
        
        if df.empty:
            st.error("Could not find student data in the Excel file. Please check the file format.")
        else:
            # Add to recent files
            file_display_name = uploaded_file.name if hasattr(uploaded_file, 'name') else "Google Drive File"
            add_to_recent(file_display_name, sheet_name, len(df), len(df.columns))
            
            # Show success message
            st.success(f"✅ Successfully loaded {len(df)} students and {len(df.columns)} columns")
            
            # Preview data
            with st.expander("🔍 Preview Student Data"):
                st.markdown('<div class="preview-box">', unsafe_allow_html=True)
                st.write("**First 5 students:**")
                st.dataframe(df.head(), use_container_width=True)
                st.write("**Column names:**")
                st.write(list(df.columns))
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Show file info
            st.markdown("<div class='section-header'>FILE INFORMATION</div>", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                file_name = uploaded_file.name if hasattr(uploaded_file, 'name') else "Google Drive File"
                st.markdown(f"""
                    <div class='stat-card'>
                        <h4>FILE NAME</h4>
                        <h3>{file_name[:20]}...</h3>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class='stat-card'>
                        <h4>SHEET</h4>
                        <h3>{sheet_name}</h3>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class='stat-card'>
                        <h4>TOTAL STUDENTS</h4>
                        <h3>{len(df)}</h3>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                    <div class='stat-card'>
                        <h4>COLUMNS</h4>
                        <h3>{len(df.columns)}</h3>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div class='section-header'>GRAPH SETTINGS</div>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                graph_type = st.selectbox(
                    "Select Graph Type",
                    ["Histogram", "Bar Graph", "Line Graph", "Cumulative Frequency Curve", "Pie Chart"]
                )
                
                color_theme = st.selectbox(
                    "Color Theme",
                    ["Rainbow", "Blue", "Green", "Red", "Purple", "Orange"]
                )
            
            with col2:
                min_grade = st.number_input("Min Grade", value=0, step=1)
                max_grade = st.number_input("Max Grade", value=100, step=1)
                interval_size = st.slider("Interval Size", 2, 20, 10)
            
            with col3:
                bins_input = st.text_input(
                    "Custom Intervals",
                    placeholder="e.g., 0,50,60,70,80,90,100",
                    value="0,50,60,70,80,90,100"
                )
                
                if graph_type == "Pie Chart":
                    pie_display = st.radio(
                        "Pie Chart Options",
                        ["Percentages (%)", "360 Degrees", "Both"],
                        horizontal=True
                    )
            
            # COLUMN NAMES - Show original column names
            st.markdown("<div class='section-header'>COLUMN NAMES</div>", unsafe_allow_html=True)
            
            # Use original column names from dataframe
            original_columns = df.columns.tolist()
            
            # Display in grid of 5 columns
            cols = st.columns(5)
            for i, col_name in enumerate(original_columns):
                with cols[i % 5]:
                    st.markdown(f"<div class='col-name-box'>{col_name}</div>", unsafe_allow_html=True)
            
            # DATA EDITOR - With + buttons and tooltips
            st.markdown("<div class='section-header'>DATA EDITOR</div>", unsafe_allow_html=True)
            
            # Row and Column buttons with hover tooltips
            col1, col2, _ = st.columns([0.5, 0.5, 10])
            
            with col1:
                st.markdown("""
                <div class="tooltip">
                    <button onclick="alert('Add Row')" style="background-color:#28a745; color:white; border:none; padding:2px 8px; font-size:20px; border-radius:4px; cursor:pointer; width:30px; height:30px;">+</button>
                    <span class="tooltiptext">add row</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("➕", key="add_row_btn", help="add row"):
                    # Create a new empty row at the end
                    new_row = pd.DataFrame({col: ["-"] for col in df.columns}, index=[0])
                    df = pd.concat([df, new_row], ignore_index=True)
                    st.rerun()
            
            with col2:
                st.markdown("""
                <div class="tooltip">
                    <button onclick="alert('Add Column')" style="background-color:#007bff; color:white; border:none; padding:2px 8px; font-size:20px; border-radius:4px; cursor:pointer; width:30px; height:30px;">+</button>
                    <span class="tooltiptext">add column</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("➕", key="add_col_btn", help="add column"):
                    # Add new column at the end
                    new_col_name = f"Column_{len(df.columns)+1}"
                    df[new_col_name] = "-"
                    st.rerun()
            
            st.caption("Hover over + buttons to see options")
            
            # Data editor with original column names
            edited_df = st.data_editor(df, use_container_width=True, height=400)
            
            st.markdown("<div class='section-header'>SELECT DATA FOR ANALYSIS</div>", unsafe_allow_html=True)
            
            # Find numeric columns
            numeric_cols = []
            for col in edited_df.columns:
                try:
                    # Replace "-" with NaN for conversion
                    temp_series = edited_df[col].replace("-", np.nan)
                    numeric_data = pd.to_numeric(temp_series, errors='coerce')
                    if numeric_data.notna().sum() > 0:
                        numeric_cols.append(col)
                except:
                    pass
            
            if numeric_cols:
                selected_col = st.selectbox("Choose column for analysis:", numeric_cols)
                
                # Clean data for analysis (replace "-" with NaN)
                temp_series = edited_df[selected_col].replace("-", np.nan)
                grade_data = pd.to_numeric(temp_series, errors='coerce').dropna()
                
                if len(grade_data) > 0:
                    st.markdown("<div class='section-header'>STATISTICAL DATA</div>", unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                            <div class='stat-card'>
                                <h4>TOTAL</h4>
                                <h3>{len(grade_data)}</h3>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class='stat-card'>
                                <h4>MEAN</h4>
                                <h3>{grade_data.mean():.2f}</h3>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                            <div class='stat-card'>
                                <h4>MEDIAN</h4>
                                <h3>{grade_data.median():.2f}</h3>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                            <div class='stat-card'>
                                <h4>STD DEV</h4>
                                <h3>{grade_data.std():.2f}</h3>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    col1, col2, col3, _ = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                            <div class='stat-card'>
                                <h4>MIN</h4>
                                <h3>{grade_data.min():.2f}</h3>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class='stat-card'>
                                <h4>MAX</h4>
                                <h3>{grade_data.max():.2f}</h3>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                            <div class='stat-card'>
                                <h4>RANGE</h4>
                                <h3>{grade_data.max() - grade_data.min():.2f}</h3>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<div class='section-header'>GRAPH VISUALIZATION</div>", unsafe_allow_html=True)
                    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                    
                    fig, ax = plt.subplots(figsize=(14, 7))
                    
                    if bins_input:
                        try:
                            bins = [float(x.strip()) for x in bins_input.split(",")]
                        except:
                            bins = np.arange(min_grade, max_grade + interval_size, interval_size)
                    else:
                        bins = np.arange(min_grade, max_grade + interval_size, interval_size)
                    
                    if graph_type == "Histogram":
                        n, bins, patches = ax.hist(grade_data, bins=bins, edgecolor='black', alpha=0.7)
                        colors = get_colors(len(patches), color_theme)
                        for i, patch in enumerate(patches):
                            patch.set_facecolor(colors[i])
                        ax.set_xlabel('Grade Intervals', fontsize=12)
                        ax.set_ylabel('Number of Students', fontsize=12)
                        ax.set_title(f'Histogram of {selected_col}', fontsize=14)
                        ax.grid(True, alpha=0.3)
                        ax.legend(['Frequency'], loc='upper right')
                        
                        for rect in patches:
                            height = rect.get_height()
                            if height > 0:
                                ax.text(rect.get_x() + rect.get_width()/2., height + 0.1,
                                       f'{int(height)}', ha='center', va='bottom', fontsize=10)
                    
                    elif graph_type == "Bar Graph":
                        counts, bin_edges = np.histogram(grade_data, bins=bins)
                        bar_positions = range(len(counts))
                        bar_labels = [f'{int(bins[i])}-{int(bins[i+1])}' for i in range(len(bins)-1)]
                        
                        colors = get_colors(len(counts), color_theme)
                        bars = ax.bar(bar_positions, counts, color=colors, edgecolor='black', alpha=0.7, label='Frequency')
                        
                        ax.set_xticks(bar_positions)
                        ax.set_xticklabels(bar_labels, rotation=45)
                        ax.set_xlabel('Grade Ranges', fontsize=12)
                        ax.set_ylabel('Number of Students', fontsize=12)
                        ax.set_title(f'Bar Graph of {selected_col}', fontsize=14)
                        ax.grid(True, alpha=0.3)
                        ax.legend()
                        
                        for bar in bars:
                            height = bar.get_height()
                            if height > 0:
                                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                       f'{int(height)}', ha='center', va='bottom', fontsize=10)
                    
                    elif graph_type == "Line Graph":
                        sorted_data = np.sort(grade_data)
                        x = range(len(sorted_data))
                        
                        colors = get_colors(len(sorted_data), color_theme)
                        scatter = ax.scatter(x, sorted_data, c=colors, s=50, alpha=0.6, label='Grades')
                        line = ax.plot(x, sorted_data, 'b-', alpha=0.5, linewidth=1, label='Trend')
                        
                        ax.set_xlabel('Student Rank', fontsize=12)
                        ax.set_ylabel('Grade', fontsize=12)
                        ax.set_title(f'Line Graph of {selected_col}', fontsize=14)
                        ax.grid(True, alpha=0.3)
                        ax.legend()
                    
                    elif graph_type == "Cumulative Frequency Curve":
                        sorted_data = np.sort(grade_data)
                        y = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
                        
                        colors = get_colors(len(sorted_data), color_theme)
                        scatter = ax.scatter(sorted_data, y, c=colors, s=50, alpha=0.6, label='Data Points')
                        line = ax.plot(sorted_data, y, 'b-', linewidth=2, label='Cumulative Curve')
                        
                        ax.set_xlabel('Grade', fontsize=12)
                        ax.set_ylabel('Cumulative Frequency', fontsize=12)
                        ax.set_title(f'Cumulative Frequency Curve of {selected_col}', fontsize=14)
                        ax.grid(True, alpha=0.3)
                        ax.set_yticklabels(['{:,.0%}'.format(x) for x in ax.get_yticks()])
                        ax.legend()
                    
                    elif graph_type == "Pie Chart":
                        counts, bin_edges = np.histogram(grade_data, bins=bins)
                        labels = [f'{int(bins[i])}-{int(bins[i+1])}' for i in range(len(bins)-1) if counts[i] > 0]
                        sizes = [count for count in counts if count > 0]
                        
                        colors = get_colors(len(sizes), color_theme)
                        
                        if pie_display == "Percentages (%)":
                            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                                              autopct='%1.1f%%', startangle=90)
                        elif pie_display == "360 Degrees":
                            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                                              autopct=lambda p: f'{p*3.6:.1f}°', startangle=90)
                        else:
                            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                                              autopct=lambda p: f'{p:.1f}%\n({p*3.6:.1f}°)', startangle=90)
                        
                        ax.set_title(f'Pie Chart of {selected_col}', fontsize=14)
                        ax.legend(wedges, labels, title="Grade Ranges", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
                        
                        for text in texts:
                            text.set_fontsize(10)
                        for autotext in autotexts:
                            autotext.set_fontsize(9)
                            autotext.set_color('white')
                            autotext.set_fontweight('bold')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                        fig.savefig(tmp_file.name, format='png', dpi=300, bbox_inches='tight')
                        graph_path = tmp_file.name
                    
                    st.markdown("<div class='section-header'>DOWNLOAD REPORT</div>", unsafe_allow_html=True)
                    
                    settings = {
                        'min_grade': min_grade,
                        'max_grade': max_grade,
                        'interval': interval_size,
                        'bins': bins_input,
                        'color_theme': color_theme
                    }
                    
                    if graph_type == "Pie Chart":
                        settings['pie_display'] = pie_display
                    
                    stats = {
                        'column': selected_col,
                        'total': len(grade_data),
                        'mean': grade_data.mean(),
                        'median': grade_data.median(),
                        'std': grade_data.std(),
                        'min': grade_data.min(),
                        'max': grade_data.max()
                    }
                    
                    pdf_buffer = create_pdf_report(edited_df, grade_data, stats, graph_type, settings, graph_path)
                    
                    st.download_button(
                        label="DOWNLOAD COMPLETE PDF REPORT",
                        data=pdf_buffer,
                        file_name=f"Grade_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    os.unlink(graph_path)
                    
                else:
                    st.warning("No valid numeric data in selected column")
            else:
                st.warning("No numeric columns found for analysis. Available columns: " + ", ".join(df.columns.tolist()))
            
    except Exception as e:
        st.error(f"Error: {e}")
        st.exception(e)

else:
    st.markdown("""
        <div style='text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-top: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);'>
            <h3 style='font-family: Playfair Display; font-size: 28px; font-weight: 400; color: white; margin: 0;'>Welcome to Grade Management System</h3>
            <p style='font-family: Poppins; color: white; margin: 15px 0 0 0; opacity: 0.9;'>Upload your Excel file above to start analyzing grades</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='footer'>Grade Management System | Advanced Analytics Dashboard | Mobile Friendly</div>", unsafe_allow_html=True)