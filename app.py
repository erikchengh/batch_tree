import streamlit as st
import pandas as pd
from model import build_batch_genealogy_graph, get_bom_list, get_product_list
from graph_view import render_genealogy_graph

# Page configuration
st.set_page_config(
    page_title="Pharma Batch Genealogy System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🏭 Pharmaceutical Batch Genealogy & Traceability System")

# Build graph
G, data = build_batch_genealogy_graph()

# Sidebar
with st.sidebar:
    st.markdown("### 🔍 Batch Selection")
    
    # Get finished products for selection
    products_df = get_product_list()
    product_options = products_df["batch_id"].tolist() if not products_df.empty else []
    
    if product_options:
        selected_batch = st.selectbox(
            "Select Target Batch",
            options=product_options,
            index=0
        )
    else:
        selected_batch = None
        st.warning("No batches available")
    
    st.divider()
    
    st.markdown("### ⚙️ Visualization Settings")
    show_upstream = st.toggle("Show Raw Materials", value=True)
    show_downstream = st.toggle("Show Products", value=False)

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📈 Batch Genealogy Graph")
    
    if selected_batch:
        render_genealogy_graph(
            G, 
            target_batch_id=selected_batch,
            highlight_upstream=show_upstream,
            highlight_downstream=show_downstream
        )
    else:
        st.info("Select a batch from the sidebar")

with col2:
    st.markdown("### 📋 Bill of Materials (BOM)")
    
    if selected_batch:
        bom_df = get_bom_list(selected_batch)
        
        if not bom_df.empty:
            st.dataframe(bom_df, use_container_width=True)
        else:
            st.info("No BOM data available")
    else:
        st.info("Select a batch to view BOM")
