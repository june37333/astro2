# ----------------------------------------------------------------------------
# Twins Study Visualization App
# ----------------------------------------------------------------------------
# Repository structure:
#  ├── app.py                    # This Streamlit app
#  ├── data/                     # Folder for CSV data files
#  │    ├── gene_expression.csv  # Columns: Timepoint, Twin, Gene, Expression
#  │    └── oxidative_stress.csv # Columns: Timepoint, Marker, Value
#  └── requirements.txt          # List dependencies: streamlit, pandas, plotly
# ----------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------------------------
# App Configuration
# ---------------------------------
st.set_page_config(
    page_title="Twins Study: Gene & Oxidative Stress",
    layout="wide"
)
st.title("🧬 Gene Expression & Oxidative Stress vs Spaceflight Duration")

# ---------------------------------
# Sidebar: Controls
# ---------------------------------
st.sidebar.header("🔧 Settings")

# 1) Spaceflight duration slider (days)
max_days = 340  # Scott Kelly's ISS duration
days_in_space = st.sidebar.slider(
    "Spaceflight Duration (days)",
    min_value=0,
    max_value=max_days,
    value=max_days
)

# 2) CSV uploader toggle
enable_upload = st.sidebar.checkbox("Use CSV Uploader", value=False)

# 3) File paths
data_dir = 'data'
gene_file = os.path.join(data_dir, 'gene_expression.csv')
ox_file = os.path.join(data_dir, 'oxidative_stress.csv')

# ---------------------------------
# Data Loading Function
# ---------------------------------
@st.cache_data
def load_data(path, label):
    """
    Load CSV from path or via uploader.
    """
    if enable_upload:
        uploaded = st.sidebar.file_uploader(f"Upload {label} CSV", type=['csv'])
        if uploaded is not None:
            return pd.read_csv(uploaded)
        return None
    if os.path.exists(path):
        return pd.read_csv(path)
    st.sidebar.warning(f"File not found: {path}")
    return None

# ---------------------------------
# Load Data
# ---------------------------------
gene_df = load_data(gene_file, 'Gene Expression')
ox_df = load_data(ox_file, 'Oxidative Stress')

# Pre-check: Ensure data loaded
if gene_df is None or ox_df is None:
    st.warning(
        "Please provide both 'gene_expression.csv' and 'oxidative_stress.csv' in 'data/' or via uploader."
    )
    st.stop()

# ---------------------------------
# Filter by Timepoint
# ---------------------------------
def filter_by_days(df):
    """
    Return subset of df where Timepoint <= days_in_space.
    """
    if 'Timepoint' not in df.columns:
        return df
    return df[df['Timepoint'] <= days_in_space]

gene_f = filter_by_days(gene_df)
ox_f = filter_by_days(ox_df)

# ---------------------------------
# Sidebar: Variable Selection
# ---------------------------------
with st.sidebar.expander("Select Variables", expanded=True):
    # Gene selector
    assert 'Gene' in gene_df.columns, "Column 'Gene' not found"
    selected_gene = st.selectbox("Select Gene", gene_df['Gene'].unique())

    # Oxidative stress marker selector
    assert 'Marker' in ox_df.columns, "Column 'Marker' not found"
    selected_marker = st.selectbox("Select Oxidative Marker", ox_df['Marker'].unique())

# ---------------------------------
# Main Layout: Two Plots Side-by-Side
# ---------------------------------
col1, col2 = st.columns(2)

# Gene Expression Plot
with col1:
    st.subheader(f"Gene Expression: {selected_gene}")
    df_gene = gene_f[gene_f['Gene'] == selected_gene]
    if {'Timepoint', 'Twin', 'Expression'}.issubset(df_gene.columns):
        fig_gene = px.line(
            df_gene,
            x='Timepoint', y='Expression', color='Twin', markers=True,
            title=f"{selected_gene} Expression over {days_in_space} days",
            labels={'Timepoint':'Days in Space', 'Expression':'Expression Level'}
        )
        st.plotly_chart(fig_gene, use_container_width=True)
    else:
        st.error("Required columns ['Timepoint','Twin','Expression'] missing in gene_expression.csv")

# Oxidative Stress Plot
with col2:
    st.subheader(f"Oxidative Stress: {selected_marker}")
    df_ox = ox_f[ox_f['Marker'] == selected_marker]
    if {'Timepoint', 'Value'}.issubset(df_ox.columns):
        fig_ox = px.line(
            df_ox,
            x='Timepoint', y='Value', markers=True,
            title=f"{selected_marker} over {days_in_space} days",
            labels={'Timepoint':'Days in Space', 'Value':'Level'}
        )
        st.plotly_chart(fig_ox, use_container_width=True)
    else:
        st.error("Required columns ['Timepoint','Marker','Value'] missing in oxidative_stress.csv")

# ---------------------------------
# Footer: Instructions for GitHub & Deployment
# ---------------------------------
st.markdown("---")
st.markdown(
    "**To publish on GitHub:**\n"
    "1. Add `app.py` and `requirements.txt` to your repo root.\n"
    "2. Create a `data/` directory and include your CSVs: `gene_expression.csv`, `oxidative_stress.csv`.\n"
    "3. Commit and push to GitHub.\n"
    "4. Connect repo in Streamlit Cloud for automatic deployment."
)
