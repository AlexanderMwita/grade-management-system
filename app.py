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

# Custom CSS for animations (same as before)
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
        # Direct download link
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(download_url)
        if response.status_code == 200:
            return io.BytesIO(response.content)
    except:
        pass
    return None

# Splash screen
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

# Main title
st.markdown("""
    <div class='main-title'>
        <h1>GRADE MANAGEMENT SYSTEM</h1>
        <p>Advanced Analytics Dashboard</p>
    </div>
""", unsafe_allow_html=True)

# Upload section with multiple options
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

# Function to create PDF report (same as before)
def create_pdf_report(df, graph_data, stats, graph_type, settings, graph_path):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=rl_colors.Color(0.4, 0.4, 0.8),
        alignment=1,
        spaceAfter=30
    )
    
    story.append(Paragraph("GRADE ANALYSIS REPORT", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("FILE INFORMATION", styles['Heading2']))
    file_data = [
        ["File Name", "Uploaded File"],
        ["Total Rows", str(len(df))],
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
    
    story.append(Paragraph(f"{graph_type} OF {stats['column']}", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    img = Image(graph_path, width=450, height=250)
    story.append(img)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("COMPLETE DATA (ALL ROWS)", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    all_data = [df.columns.tolist()]
    for index, row in df.iterrows():
        all_data.append(row.tolist())
    
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

# Function to smart read Excel
def smart_read_excel(file):
    if isinstance(file, io.BytesIO):
        df = pd.read_excel(file)
        return df, "Uploaded"
    
    xl = pd.ExcelFile(file)
    for sheet in xl.sheet_names:
        df_sheet = pd.read_excel(file, sheet_name=sheet, header=None)
        for col in range(min(10, df_sheet.shape[1])):
            for row in range(min(20, df_sheet.shape[0])):
                cell_val = str(df_sheet.iloc[row, col]).upper()
                if 'S/NO' in cell_val or 'REG' in cell_val or 'NUMBER' in cell_val:
                    df = pd.read_excel(file, sheet_name=sheet, header=row)
                    df.columns = [str(col).strip() for col in df.columns]
                    df = df.dropna(axis=1, how='all')
                    df = df.dropna(how='all')
                    return df, sheet
    return pd.read_excel(file), "Sheet1"

# Main program logic (same as before)
if uploaded_file is not None:
    try:
        df, sheet_name = smart_read_excel(uploaded_file)
        
        st.markdown("<div class='section-header'>FILE INFORMATION</div>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class='stat-card'>
                    <h4>FILE NAME</h4>
                    <h3>{'Google Drive File' if isinstance(uploaded_file, io.BytesIO) else uploaded_file.name[:20]}...</h3>
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
                    <h4>ROWS</h4>
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
            max_grade = st.number_input("Max Grade", value=35, step=1)
            interval_size = st.slider("Interval Size", 2, 10, 5)
        
        with col3:
            bins_input = st.text_input(
                "Custom Intervals",
                placeholder="e.g., 0,5,10,15,20,25,30,35",
                value="0,5,10,15,20,25,30,35"
            )
            
            if graph_type == "Pie Chart":
                pie_display = st.radio(
                    "Pie Chart Options",
                    ["Percentages (%)", "360 Degrees", "Both"],
                    horizontal=True
                )
        
        st.markdown("<div class='section-header'>COLUMN NAMES</div>", unsafe_allow_html=True)
        valid_columns = [col for col in df.columns if 'Unnamed' not in str(col) or df[col].notna().any()]
        
        cols = st.columns(5)
        for i, col_name in enumerate(valid_columns[:15]):
            with cols[i % 5]:
                st.markdown(f"<div class='col-name-box'>{col_name}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>DATA EDITOR</div>", unsafe_allow_html=True)
        
        col1, col2, _ = st.columns([0.5, 0.5, 10])
        with col1:
            if st.button("+ Add Row", key="add_row", help="Add new row"):
                new_row = pd.DataFrame({col: [""] for col in df.columns})
                df = pd.concat([df, new_row], ignore_index=True)
                st.rerun()
        
        with col2:
            if st.button("+ Add Column", key="add_col", help="Add new column"):
                new_col_name = f"Column_{len(df.columns)}"
                df[new_col_name] = ""
                st.rerun()
        
        edited_df = st.data_editor(df, use_container_width=True, height=400)
        
        st.markdown("<div class='section-header'>SELECT DATA FOR ANALYSIS</div>", unsafe_allow_html=True)
        
        numeric_cols = []
        for col in edited_df.columns:
            try:
                cleaned = edited_df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                numeric_data = pd.to_numeric(cleaned, errors='coerce')
                if numeric_data.notna().sum() > 0:
                    numeric_cols.append(col)
            except:
                pass
        
        if numeric_cols:
            selected_col = st.selectbox("Choose column for analysis:", numeric_cols)
            
            cleaned = edited_df[selected_col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
            grade_data = pd.to_numeric(cleaned, errors='coerce').dropna()
            
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
            st.warning("No numeric columns found in the file")
            
    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.markdown("""
        <div style='text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-top: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);'>
            <h3 style='font-family: Playfair Display; font-size: 28px; font-weight: 400; color: white; margin: 0;'>Welcome to Grade Management System</h3>
            <p style='font-family: Poppins; color: white; margin: 15px 0 0 0; opacity: 0.9;'>Upload your Excel file above to start analyzing grades</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='footer'>Grade Management System | Advanced Analytics Dashboard | Mobile Friendly</div>", unsafe_allow_html=True)