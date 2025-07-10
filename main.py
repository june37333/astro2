import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Twins Study: Gene Expr & Oxidative Stress",
                   layout="wide")
st.title("🧬 Gene Expression & Oxidative Stress vs Spaceflight Duration")

# Sidebar settings
st.sidebar.header("🔧 Settings")
# Spaceflight duration slider (days)
max_days = 340
days_in_space = st.sidebar.slider(
    "Spaceflight Duration (days)", 0, max_days, max_days
)
# CSV uploader toggle
use_uploader = st.sidebar.checkbox("Use CSV Uploader", value=False)

# File paths
GENE_FILE = 'data/gene_expression.csv'
OX_FILE = 'data/oxidative_stress.csv'

@st.cache_data
def load_csv(path, label):
    if use_uploader:
        uploaded = st.sidebar.file_uploader(f"Upload {label} CSV", type='csv')
        if uploaded:
            return pd.read_csv(uploaded)
        return None
    if os.path.exists(path):
        return pd.read_csv(path)
    st.sidebar.warning(f"File not found: {path}")
    return None

# Load data
gene_df = load_csv(GENE_FILE, 'Gene Expression')
ox_df = load_csv(OX_FILE, 'Oxidative Stress')

# Filter by days function
def filter_days(df):
    if df is None or 'Timepoint' not in df.columns:
        return None
    return df[df['Timepoint'] <= days_in_space]

# Only proceed if both datasets are loaded
if gene_df is None or ox_df is None:
    st.warning("Please upload or place both 'gene_expression.csv' and 'oxidative_stress.csv' in data/.")
    st.stop()

# Sidebar selectors
with st.sidebar:
    # Gene selection
    if 'Gene' in gene_df.columns:
        gene_list = gene_df['Gene'].unique().tolist()
        selected_gene = st.selectbox("Select Gene", gene_list)
    else:
        st.error("'Gene' column missing in gene_expression.csv")
        st.stop()
    # Oxidative marker selection
    if 'Marker' in ox_df.columns:
        marker_list = ox_df['Marker'].unique().tolist()
        selected_marker = st.selectbox("Select Oxidative Marker", marker_list)
    else:
        st.error("'Marker' column missing in oxidative_stress.csv")
        st.stop()

# Filtered data for plots
gene_f = filter_days(gene_df)
go_f = filter_days(ox_df)

# Gene expression plot
col1, col2 = st.columns(2)
with col1:
    st.header(f"Gene Expression: {selected_gene}")
    df_g = gene_f[gene_f['Gene'] == selected_gene]
    if {'Timepoint','Twin','Expression'}.issubset(df_g.columns):
        fig1 = px.line(df_g, x='Timepoint', y='Expression', color='Twin',
                       markers=True,
                       title=f"{selected_gene} Expression over {days_in_space} days",
                       labels={'Expression':'Expression Level','Timepoint':'Days in Space'})
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.error("Required columns ['Timepoint','Twin','Expression'] missing in gene_expression.csv")

# Oxidative stress plot
with col2:
    st.header(f"Oxidative Stress: {selected_marker}")
    df_o = go_f[go_f['Marker'] == selected_marker]
    if {'Timepoint','Value'}.issubset(df_o.columns):
        fig2 = px.line(df_o, x='Timepoint', y='Value',
                       markers=True,
                       title=f"{selected_marker} over {days_in_space} days",
                       labels={'Value':'Level','Timepoint':'Days in Space'})
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.error("Required columns ['Timepoint','Value'] missing in oxidative_stress.csv")

st.markdown("---")
st.info(
    "*Prepare 'gene_expression.csv' with columns ['Timepoint','Twin','Gene','Expression'] and 'oxidative_stress.csv' with ['Timepoint','Marker','Value']*"
)
