import streamlit as st
import pandas as pd
from model import build_batch_genealogy_graph, get_bom_list, get_product_genealogy
from graph_view import render_genealogy_graph

st.set_page_config(
    page_title="Pharma Batch Genealogy System",
    layout="wide",
    page_icon="🏭"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #2c3e50;
        padding-bottom: 1rem;
        border-bottom: 3px solid #3498db;
        margin-bottom: 2rem;
        text-align: center;
    }
    .section-header {
        font-size: 1.5rem;
        color: #34495e;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #ecf0f1;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .data-table {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>🏭 Pharmaceutical Batch Genealogy & Traceability System</h1>", unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.markdown("### 🔍 Batch Selection")
    
    available_batches = ["B001", "API-2025-12-15", "EXC-2026-01-02", "FIN-2026-01-10"]
    selected_batch = st.selectbox(
        "Select Target Batch",
        available_batches,
        index=0,
        help="Select a batch to trace its genealogy"
    )
    
    st.divider()
    st.markdown("### ⚙️ Visualization Settings")
    
    trace_depth = st.slider(
        "Trace Depth",
        min_value=1,
        max_value=4,
        value=2,
        help="How many levels up/down to trace"
    )
    
    show_quantities = st.toggle("Show Quantities", value=True)
    
    analysis_type = st.radio(
        "Analysis Type",
        ["Genealogy Graph", "Bill of Materials", "Product Trace"],
        index=0
    )
    
    st.divider()
    st.markdown("### ℹ️ About")
    st.info("""
    This system traces:
    - **Upstream**: What raw materials were used
    - **Downstream**: What products were made
    - **Complete BOM**: All materials consumed
    """)

# Main Content Area
if analysis_type == "Genealogy Graph":
    # Build and display genealogy graph
    st.markdown(f"### 📊 Batch Genealogy: `{selected_batch}`")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.caption("Material Flow: ← Raw Materials → Finished Products")
    with col2:
        if st.button("🔄 Refresh Graph", use_container_width=True):
            st.rerun()
    with col3:
        if st.button("📥 Export Data", use_container_width=True):
            st.info("Export functionality to be implemented")
    
    # Build graph
    G = build_batch_genealogy_graph(selected_batch, depth=trace_depth)
    
    # Display graph
    render_genealogy_graph(
        G, 
        selected_batch=selected_batch,
        show_quantities=show_quantities
    )
    
    # Node details
    st.markdown("<div class='section-header'>📋 Selected Batch Details</div>", unsafe_allow_html=True)
    
    if selected_batch:
        # Get batch info from graph
        if selected_batch in G.nodes:
            batch_data = G.nodes[selected_batch]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Batch ID", selected_batch)
            with col2:
                st.metric("Product", batch_data.get("product", "N/A"))
            with col3:
                status = batch_data.get("status", "Unknown")
                color = "🟢" if status in ["Completed", "Released"] else "🟡" if status == "In Progress" else "🔴"
                st.metric("Status", f"{color} {status}")
            
            # Additional details
            with st.expander("📄 Batch Details", expanded=True):
                cols = st.columns(4)
                with cols[0]:
                    if batch_data.get("quantity"):
                        st.write(f"**Quantity:** {batch_data['quantity']}")
                with cols[1]:
                    if batch_data.get("date"):
                        st.write(f"**Manufacturing Date:** {batch_data['date']}")
                with cols[2]:
                    if batch_data.get("lot"):
                        st.write(f"**Lot Number:** {batch_data['lot']}")
                with cols[3]:
                    # Count connections
                    in_degree = G.in_degree(selected_batch)
                    out_degree = G.out_degree(selected_batch)
                    st.write(f"**Connections:** {in_degree} in, {out_degree} out")

elif analysis_type == "Bill of Materials":
    st.markdown(f"### 📋 Complete Bill of Materials: `{selected_batch}`")
    
    # Get BOM
    bom_data = get_bom_list(selected_batch)
    
    if bom_data:
        # Convert to DataFrame for display
        df_bom = pd.DataFrame(bom_data)
        
        # Add indentation for levels
        def indent_name(row):
            indent = "&nbsp;" * (row['level'] * 4)
            icon = "📦" if row['type'] == 'raw' else "⚙️" if row['type'] == 'intermediate' else "📁"
            return f"{indent}{icon} {row['material_name']}"
        
        df_bom['Material'] = df_bom.apply(indent_name, axis=1)
        
        # Display BOM
        st.dataframe(
            df_bom[['Material', 'material_batch', 'quantity', 'type', 'specification', 'supplier']],
            column_config={
                "Material": st.column_config.TextColumn("Material", width="large"),
                "material_batch": "Batch ID",
                "quantity": "Quantity",
                "type": "Type",
                "specification": "Specification",
                "supplier": "Supplier"
            },
            use_container_width=True,
            hide_index=True
        )
        
        # BOM Summary
        st.markdown("<div class='section-header'>📈 BOM Summary</div>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_items = len(df_bom)
            st.metric("Total Items", total_items)
        with col2:
            raw_materials = len(df_bom[df_bom['type'] == 'raw'])
            st.metric("Raw Materials", raw_materials)
        with col3:
            unique_suppliers = df_bom['supplier'].nunique()
            st.metric("Unique Suppliers", unique_suppliers)
        with col4:
            total_batches = df_bom['material_batch'].nunique()
            st.metric("Unique Batches", total_batches)
    else:
        st.warning(f"No BOM data available for batch {selected_batch}")

elif analysis_type == "Product Trace":
    st.markdown(f"### 🔄 Product Traceability: `{selected_batch}`")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### ⬆️ Upstream Trace (What made this)")
        upstream = get_product_genealogy(selected_batch, direction="up")
        
        if upstream:
            for item in upstream:
                level_indent = "&nbsp;" * (item['level'] * 4)
                icon = "🔼" if item['level'] == 0 else "↗️" if item['level'] < 0 else "↘️"
                
                with st.container():
                    cols = st.columns([1, 3, 2, 2])
                    with cols[0]:
                        st.write(f"{level_indent}{icon}")
                    with cols[1]:
                        st.write(f"**{item['batch_id']}**")
                    with cols[2]:
                        st.write(item['product'])
                    with cols[3]:
                        st.write(item['quantity'])
        else:
            st.info("No upstream trace data available")
    
    with col2:
        st.markdown("##### ⬇️ Downstream Trace (What this made)")
        downstream = get_product_genealogy(selected_batch, direction="down")
        
        if downstream:
            for item in downstream:
                level_indent = "&nbsp;" * (item['level'] * 4)
                icon = "🔽" if item['level'] == 0 else "↘️" if item['level'] < 0 else "↗️"
                
                with st.container():
                    cols = st.columns([1, 3, 2, 2])
                    with cols[0]:
                        st.write(f"{level_indent}{icon}")
                    with cols[1]:
                        st.write(f"**{item['batch_id']}**")
                    with cols[2]:
                        st.write(item['product'])
                    with cols[3]:
                        st.write(item['quantity'])
        else:
            st.info("No downstream trace data available")
    
    # Trace Summary
    st.markdown("<div class='section-header'>📊 Trace Summary</div>", unsafe_allow_html=True)
    
    total_upstream = len([x for x in upstream if x['level'] != 0])
    total_downstream = len([x for x in downstream if x['level'] != 0])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Upstream Batches", total_upstream)
    with col2:
        st.metric("Downstream Batches", total_downstream)
    with col3:
        st.metric("Total Traceable", total_upstream + total_downstream)

# Footer
st.divider()
st.caption("Pharmaceutical Batch Genealogy System v1.0 | Data is simulated for demonstration purposes")
