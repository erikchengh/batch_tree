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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #2c3e50;
        font-weight: 700;
        padding-bottom: 1rem;
        border-bottom: 3px solid #3498db;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #2c3e50, #3498db);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #3498db;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .stButton > button {
        border-radius: 8px;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2);
    }
    
    .highlight-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 class='main-header'>🏭 Pharmaceutical Batch Genealogy & Traceability System</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🔍 Batch Selection")
    
    # Get product list for selection
    products_df = get_product_list()
    product_options = products_df["batch_id"].tolist()
    
    selected_batch = st.selectbox(
        "Select Target Batch",
        options=product_options,
        index=0,
        help="Select a finished product batch to trace"
    )
    
    st.divider()
    
    st.markdown("### ⚙️ Visualization Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        show_upstream = st.toggle(
            "Show Raw Materials", 
            value=True,
            help="Show raw materials feeding into selected batch"
        )
    with col2:
        show_downstream = st.toggle(
            "Show Products", 
            value=False,
            help="Show products using selected batch"
        )
    
    trace_mode = st.radio(
        "Trace Mode",
        ["Full Genealogy", "Raw Materials Only", "Production Flow"],
        index=0,
        help="Control what relationships to show"
    )
    
    st.divider()
    
    # Quick stats
    G, _ = build_batch_genealogy_graph()
    batch_details = G.nodes.get(selected_batch, {})
    
    st.markdown("### 📊 Batch Info")
    if batch_details:
        st.markdown(f"**Batch:** `{selected_batch}`")
        st.markdown(f"**Type:** `{batch_details.get('type', 'N/A')}`")
        st.markdown(f"**Material:** `{batch_details.get('material', 'N/A')}`")
        st.markdown(f"**Quantity:** `{batch_details.get('quantity', 'N/A')}`")

# Main content - Two columns
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📈 Batch Genealogy Graph")
    
    # Build and render graph
    G, data = build_batch_genealogy_graph()
    
    # Adjust highlighting based on trace mode
    highlight_upstream = show_upstream and (trace_mode in ["Full Genealogy", "Raw Materials Only"])
    highlight_downstream = show_downstream and (trace_mode in ["Full Genealogy", "Production Flow"])
    
    # Render the interactive graph
    render_genealogy_graph(
        G, 
        target_batch_id=selected_batch,
        highlight_upstream=highlight_upstream,
        highlight_downstream=highlight_downstream
    )
    
    # Graph interpretation
    with st.expander("📖 How to read this graph", expanded=False):
        st.markdown("""
        **Flow Direction:** Materials flow from left (raw materials) to right (finished products)
        
        **Node Colors:**
        - 🔵 **Blue Circles** = Raw Materials (API, Excipients)
        - 🟣 **Purple Squares** = Intermediate Batches (Blends, Solutions)
        - 🟢 **Green Stars** = Finished Products (Tablets, Capsules)
        
        **Edge Meanings:**
        - 🔴 **Red Arrows** = Material consumption (Batch A → consumed by → Batch B)
        - 🔵 **Blue Arrows** = Process sequence (Step 1 → precedes → Step 2)
        
        **Interactions:**
        - Click any node to see details
        - Drag nodes to rearrange layout
        - Scroll to zoom in/out
        """)

with col2:
    st.markdown("### 📋 Bill of Materials (BOM)")
    
    # Get BOM for selected batch
    bom_df = get_bom_list(selected_batch)
    
    if not bom_df.empty:
        # Display BOM table
        st.dataframe(
            bom_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Batch ID": st.column_config.TextColumn(width="medium"),
                "Material": st.column_config.TextColumn(width="large"),
                "Quantity": st.column_config.NumberColumn(format="%.2f"),
                "Unit": st.column_config.TextColumn(width="small"),
                "Type": st.column_config.TextColumn(width="medium"),
                "Status": st.column_config.TextColumn(width="small")
            }
        )
        
        # BOM Summary
        total_items = len(bom_df)
        raw_materials = len(bom_df[bom_df["Type"] == "Raw Material"])
        intermediates = len(bom_df[bom_df["Type"] == "Intermediate"])
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Items", total_items)
        with col_b:
            st.metric("Raw Materials", raw_materials)
        with col_c:
            st.metric("Intermediates", intermediates)
    else:
        st.info("No BOM data available for selected batch")
    
    st.divider()
    
    st.markdown("### 🔄 Material Traceability")
    
    # Trace raw material to finished product
    if selected_batch.startswith("FP-"):
        st.markdown("**Raw Material Trace:**")
        
        # Find all raw materials used in this batch
        all_raw_materials = []
        for _, batch in data["batches"].iterrows():
            if batch["batch_id"].startswith("RM-"):
                all_raw_materials.append(batch["batch_id"])
        
        if all_raw_materials:
            for rm in all_raw_materials[:3]:  # Show first 3
                st.markdown(f"- `{rm}` → `{selected_batch}`")
            
            if len(all_raw_materials) > 3:
                with st.expander(f"Show all {len(all_raw_materials)} raw materials"):
                    for rm in all_raw_materials:
                        st.markdown(f"- `{rm}`")
        else:
            st.info("No raw material trace available")
    
    st.divider()
    
    # Batch details
    st.markdown("### 📄 Batch Details")
    
    batch_info = data["batches"][data["batches"]["batch_id"] == selected_batch]
    if not batch_info.empty:
        batch = batch_info.iloc[0]
        
        details_col1, details_col2 = st.columns(2)
        
        with details_col1:
            st.markdown(f"**Material:**\n`{batch['material']}`")
            st.markdown(f"**Quantity:**\n`{batch['quantity']} {batch['unit']}`")
            if 'product' in batch:
                st.markdown(f"**Product:**\n`{batch['product']}`")
        
        with details_col2:
            if 'manufacturing_date' in batch:
                st.markdown(f"**Manufactured:**\n`{batch['manufacturing_date']}`")
            if 'expiry' in batch:
                st.markdown(f"**Expiry:**\n`{batch['expiry']}`")
            if 'quality' in batch:
                st.markdown(f"**Quality:**\n`{batch['quality']}`")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 20px;">
    <p><b>Pharmaceutical Batch Genealogy System</b> | Version 1.0 | For Manufacturing Execution Systems (MES)</p>
    <p style="font-size: 0.9em;">Track material flow from raw materials to finished products with full traceability</p>
</div>
""", unsafe_allow_html=True)
