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
    }
    .trace-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid;
        margin: 0.5rem 0;
    }
    .trace-forward { border-left-color: #2ecc71; }
    .trace-backward { border-left-color: #e74c3c; }
    .trace-both { border-left-color: #f39c12; }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 class='main-header'>🏭 Pharmaceutical Batch Genealogy & Traceability System</h1>", unsafe_allow_html=True)

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
            index=0,
            help="Select a finished product batch to trace"
        )
    else:
        selected_batch = None
        st.warning("No batches available")
    
    st.divider()
    
    st.markdown("### 🔬 Trace Mode")
    
    # Trace mode selection
    trace_mode = st.radio(
        "Select Trace Direction",
        ["none", "forward", "backward", "both"],
        format_func=lambda x: {
            "none": "🟢 No Trace (Show All)",
            "forward": "➡️ Forward Trace (Downstream)",
            "backward": "⬅️ Backward Trace (Upstream)",
            "both": "↔️ Both Directions (Full Genealogy)"
        }[x],
        help="Trace materials forward to products or backward to raw materials"
    )
    
    # Trace explanation
    trace_descriptions = {
        "none": "Shows all batches without highlighting",
        "forward": "Highlights products made FROM this batch",
        "backward": "Highlights materials used TO MAKE this batch", 
        "both": "Shows complete material flow in both directions"
    }
    
    st.info(f"**{trace_descriptions[trace_mode]}**")
    
    st.divider()
    
    # Quick stats
    if selected_batch and selected_batch in G.nodes:
        node_data = G.nodes[selected_batch]
        st.markdown("### 📊 Selected Batch Info")
        st.markdown(f"**Batch:** `{selected_batch}`")
        st.markdown(f"**Type:** `{node_data.get('type', 'N/A')}`")
        st.markdown(f"**Material:** `{node_data.get('material', 'N/A')}`")
        st.markdown(f"**Quantity:** `{node_data.get('quantity', 'N/A')}`")

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📈 Interactive Genealogy Graph")
    
    # Trace mode indicator
    trace_icons = {
        "none": "🟢",
        "forward": "➡️", 
        "backward": "⬅️",
        "both": "↔️"
    }
    
    st.markdown(f"**Trace Mode:** {trace_icons[trace_mode]} **{trace_mode.upper()}**")
    
    if selected_batch:
        # Render the enhanced graph with trace mode
        render_genealogy_graph(
            G, 
            target_batch_id=selected_batch,
            trace_mode=trace_mode
        )
        
        # Graph interpretation
        with st.expander("📖 How to read the trace", expanded=False):
            if trace_mode == "none":
                st.markdown("""
                **All connections shown equally:**
                - 🔵 Blue nodes = Raw Materials
                - 🟣 Purple nodes = Intermediate Batches  
                - 🟢 Green nodes = Finished Products
                - ⚫ Gray lines = Material flows
                """)
            elif trace_mode == "forward":
                st.markdown("""
                **Forward Trace (Downstream):**
                - 🟠 Orange diamond = Selected target batch
                - 🔴 Red lines = Paths FROM target TO finished products
                - 🟢 Green nodes = Products made from target batch
                - ⚫ Dimmed nodes = Not in forward trace
                """)
            elif trace_mode == "backward":
                st.markdown("""
                **Backward Trace (Upstream):**
                - 🟠 Orange diamond = Selected target batch  
                - 🔴 Red lines = Paths FROM raw materials TO target
                - 🔵 Blue nodes = Raw materials used to make target
                - ⚫ Dimmed nodes = Not in backward trace
                """)
            else:  # both
                st.markdown("""
                **Full Genealogy Trace:**
                - 🟠 Orange diamond = Selected target batch
                - 🔴 Red lines = Complete material flow
                - 🔵 Blue nodes = Raw materials used
                - 🟢 Green nodes = Products produced
                - Shows entire supply chain for this batch
                """)
    else:
        st.info("👈 Select a batch from the sidebar to visualize")

with col2:
    st.markdown("### 📋 Bill of Materials & Trace Info")
    
    if selected_batch:
        # BOM Table
        bom_df = get_bom_list(selected_batch)
        
        if not bom_df.empty:
            st.markdown("**📦 Materials Consumed:**")
            st.dataframe(
                bom_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Batch ID": st.column_config.TextColumn(width="medium"),
                    "Material": st.column_config.TextColumn(width="large"),
                    "Quantity": st.column_config.NumberColumn(format="%.2f"),
                    "Unit": st.column_config.TextColumn(width="small")
                }
            )
        else:
            st.info("No BOM data available")
        
        st.divider()
        
        # Trace statistics
        st.markdown("### 🔢 Trace Statistics")
        
        if trace_mode != "none":
            # Calculate trace stats
            ancestors = nx.ancestors(G, selected_batch) if trace_mode in ["backward", "both"] else set()
            descendants = nx.descendants(G, selected_batch) if trace_mode in ["forward", "both"] else set()
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                total_traced = len(ancestors) + len(descendants) + 1  # +1 for target itself
                st.metric("Total Traced", total_traced)
            
            with col_stat2:
                st.metric("Upstream", len(ancestors))
            
            with col_stat3:
                st.metric("Downstream", len(descendants))
            
            # Material types in trace
            if ancestors:
                raw_in_trace = len([n for n in ancestors if G.nodes[n].get("type") == "Raw Material"])
                st.metric("Raw Materials", raw_in_trace)
        
        st.divider()
        
        # Material flow summary
        st.markdown("### 🔄 Material Flow")
        
        if trace_mode == "forward":
            st.success("**Flow:** Selected Batch → Finished Products")
            st.caption("Shows what products are made from this batch")
        elif trace_mode == "backward":
            st.info("**Flow:** Raw Materials → Selected Batch")  
            st.caption("Shows what materials are used to make this batch")
        elif trace_mode == "both":
            st.warning("**Flow:** Raw Materials → Selected Batch → Finished Products")
            st.caption("Complete supply chain visibility")
    else:
        st.info("Select a batch to view details")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 20px;">
    <p><b>Pharmaceutical Batch Genealogy System</b> | Version 2.0 | Enhanced Trace Visualization</p>
    <p style="font-size: 0.9em;">Trace materials forward to products or backward to raw materials with clear highlighting</p>
</div>
""", unsafe_allow_html=True)
