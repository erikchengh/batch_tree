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

st.title("🏭 Pharmaceutical Batch Genealogy System")

try:
    # Try to build graph
    G, data = build_batch_genealogy_graph()
    graph_loaded = True
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    G = None
    data = None
    graph_loaded = False

if graph_loaded and G is not None:
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔍 Batch Selection")
        
        # Get nodes that are finished products
        finished_products = [n for n in G.nodes() if G.nodes[n].get("type") == "Finished Product"]
        
        if finished_products:
            selected_batch = st.selectbox(
                "Select Target Batch",
                options=finished_products,
                index=0
            )
        else:
            selected_batch = None
            st.warning("No finished product batches found")
        
        st.divider()
        
        st.markdown("### 🔬 Trace Mode")
        trace_mode = st.radio(
            "Select Trace Direction",
            ["none", "forward", "backward", "both"],
            format_func=lambda x: {
                "none": "🟢 No Trace",
                "forward": "➡️ Forward Trace",
                "backward": "⬅️ Backward Trace",
                "both": "↔️ Both Directions"
            }[x]
        )
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Batch Genealogy Graph")
        
        if selected_batch:
            render_genealogy_graph(
                G, 
                target_batch_id=selected_batch,
                trace_mode=trace_mode
            )
        else:
            st.info("Select a batch from the sidebar")
    
    with col2:
        st.markdown("### 📋 Batch Details")
        
        if selected_batch:
            node_data = G.nodes[selected_batch]
            st.json(node_data)  # Show all node data for debugging
            
            # Show BOM
            bom_df = get_bom_list(selected_batch)
            if not bom_df.empty:
                st.markdown("**Bill of Materials:**")
                st.dataframe(bom_df)
else:
    st.error("Failed to load batch data. Please check your data files.")
