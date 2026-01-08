import streamlit as st
import pandas as pd
import networkx as nx
from model import build_batch_genealogy_graph, get_bom_list, get_product_list, analyze_graph
from graph_view import render_genealogy_graph

# Page configuration
st.set_page_config(
    page_title="Pharma Batch Genealogy System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1a3c6e;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #5d7fa3;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton button {
        background-color: #1e88e5;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏭 Pharmaceutical Batch Genealogy System</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Track material flow, traceability, and batch relationships across manufacturing processes</p>', unsafe_allow_html=True)

# Initialize session state
if 'graph_loaded' not in st.session_state:
    st.session_state.graph_loaded = False
if 'G' not in st.session_state:
    st.session_state.G = None
if 'data' not in st.session_state:
    st.session_state.data = None

# Load data button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Load Batch Genealogy Data", use_container_width=True):
        with st.spinner("Loading batch data and building genealogy graph..."):
            try:
                # Try to build graph
                G, data = build_batch_genealogy_graph()
                st.session_state.G = G
                st.session_state.data = data
                st.session_state.graph_loaded = True
                st.success("✅ Data loaded successfully!")
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
                st.session_state.graph_loaded = False

# Main app logic
if st.session_state.graph_loaded and st.session_state.G is not None:
    G = st.session_state.G
    data = st.session_state.data
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Graph Statistics")
        
        # Show graph stats
        stats = analyze_graph(G)
        st.metric("Total Batches", stats["total_nodes"])
        st.metric("Total Relationships", stats["total_edges"])
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Raw Materials", stats["raw_materials"])
        with col_b:
            st.metric("Finished Products", stats["finished_products"])
        
        st.divider()
        
        st.markdown("### 🔍 Batch Selection")
        
        # Get nodes that are finished products
        finished_products = [n for n in G.nodes() if G.nodes[n].get("type") == "Finished Product"]
        
        if finished_products:
            selected_batch = st.selectbox(
                "Select Target Batch",
                options=finished_products,
                index=0,
                help="Select a finished product batch to trace its genealogy"
            )
        else:
            selected_batch = None
            st.warning("No finished product batches found")
        
        st.divider()
        
        st.markdown("### 🔬 Trace Mode")
        trace_mode = st.radio(
            "Select Trace Direction",
            ["none", "forward", "backward", "both"],
            index=0,
            format_func=lambda x: {
                "none": "🟢 Full Graph View",
                "forward": "➡️ Downstream Trace",
                "backward": "⬅️ Upstream Trace",
                "both": "↔️ Complete Trace"
            }[x],
            help="Select how to trace materials through the supply chain"
        )
        
        st.divider()
        
        # Debug info
        with st.expander("🔧 Debug Information"):
            st.write(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            st.write(f"Selected batch: {selected_batch}")
            st.write(f"Trace mode: {trace_mode}")
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Batch Genealogy Graph")
        
        if selected_batch:
            # Show selected batch info
            node_data = G.nodes[selected_batch]
            st.info(f"**Selected Batch:** {selected_batch} - {node_data.get('material', 'Unknown material')}")
            
            # Render the graph
            render_genealogy_graph(
                G, 
                target_batch_id=selected_batch,
                trace_mode=trace_mode
            )
        else:
            st.info("Select a batch from the sidebar to visualize its genealogy")
    
    with col2:
        st.markdown("### 📋 Batch Details")
        
        if selected_batch:
            node_data = G.nodes[selected_batch]
            
            # Display batch details in a nice format
            st.markdown(f"**Batch ID:** `{selected_batch}`")
            st.markdown(f"**Material:** {node_data.get('material', 'N/A')}")
            st.markdown(f"**Type:** {node_data.get('type', 'N/A')}")
            st.markdown(f"**Quantity:** {node_data.get('quantity', 'N/A')} {node_data.get('unit', '')}")
            st.markdown(f"**Status:** {node_data.get('status', 'N/A')}")
            st.markdown(f"**Quality:** {node_data.get('quality', 'N/A')}")
            
            if 'product' in node_data:
                st.markdown(f"**Product:** {node_data.get('product', 'N/A')}")
            if 'expiry_date' in node_data:
                st.markdown(f"**Expiry Date:** {node_data.get('expiry_date', 'N/A')}")
            if 'manufacturing_date' in node_data:
                st.markdown(f"**Manufacturing Date:** {node_data.get('manufacturing_date', 'N/A')}")
            
            st.divider()
            
            # Show BOM
            bom_df = get_bom_list(selected_batch)
            if not bom_df.empty:
                st.markdown("**📦 Bill of Materials (BOM):**")
                st.dataframe(bom_df, use_container_width=True)
            else:
                st.info("No BOM data available for this batch")
            
            st.divider()
            
            # Show connected batches
            st.markdown("**🔗 Connected Batches:**")
            
            # Predecessors (what went into this batch)
            predecessors = list(G.predecessors(selected_batch))
            if predecessors:
                st.markdown("**Inputs (Predecessors):**")
                for pred in predecessors:
                    pred_data = G.nodes[pred]
                    st.markdown(f"- `{pred}`: {pred_data.get('material', '')}")
            else:
                st.markdown("No direct inputs found")
            
            # Successors (what this batch produced)
            successors = list(G.successors(selected_batch))
            if successors:
                st.markdown("**Outputs (Successors):**")
                for succ in successors:
                    succ_data = G.nodes[succ]
                    st.markdown(f"- `{succ}`: {succ_data.get('material', '')}")
            else:
                st.markdown("No direct outputs found")
            
            st.divider()
            
            # Raw data for debugging
            with st.expander("📄 View Raw Node Data"):
                st.json(node_data)
        else:
            st.info("Select a batch to see details")
    
    # Bottom section
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.expander("📋 All Batches"):
            batch_list = []
            for node in G.nodes():
                node_data = G.nodes[node]
                batch_list.append({
                    "Batch ID": node,
                    "Type": node_data.get('type', 'Unknown'),
                    "Material": node_data.get('material', 'Unknown'),
                    "Quantity": node_data.get('quantity', ''),
                    "Status": node_data.get('status', '')
                })
            st.dataframe(pd.DataFrame(batch_list))
    
    with col2:
        with st.expander("🔄 All Relationships"):
            edge_list = []
            for u, v, data in G.edges(data=True):
                edge_list.append({
                    "From": u,
                    "To": v,
                    "Relationship": data.get('relationship', 'unknown'),
                    "Quantity": data.get('quantity', ''),
                    "Unit": data.get('unit', '')
                })
            st.dataframe(pd.DataFrame(edge_list))
    
    with col3:
        with st.expander("📊 Graph Analysis"):
            st.write(stats)
            if stats["is_connected"]:
                st.success("Graph is connected")
            else:
                st.warning("Graph is not fully connected")
            
            # Calculate and show degree centrality
            if G.number_of_nodes() > 0:
                in_degrees = dict(G.in_degree())
                out_degrees = dict(G.out_degree())
                
                # Find most connected nodes
                most_inputs = max(in_degrees.items(), key=lambda x: x[1]) if in_degrees else (None, 0)
                most_outputs = max(out_degrees.items(), key=lambda x: x[1]) if out_degrees else (None, 0)
                
                st.markdown(f"**Most inputs:** {most_inputs[0]} ({most_inputs[1]} inputs)")
                st.markdown(f"**Most outputs:** {most_outputs[0]} ({most_outputs[1]} outputs)")

else:
    # Show welcome/loading screen
    st.markdown("""
    ## Welcome to the Pharma Batch Genealogy System
    
    This system helps you visualize and trace the flow of materials through pharmaceutical manufacturing processes.
    
    ### 🚀 Getting Started:
    1. Click the **"Load Batch Genealogy Data"** button above
    2. Select a finished product batch from the sidebar
    3. Choose a trace mode to visualize material flow
    4. Explore the genealogy graph and batch details
    
    ### 📊 What you can do:
    - **Trace upstream**: See what raw materials went into a product
    - **Trace downstream**: See what products were made from a material
    - **View BOM**: See the Bill of Materials for any batch
    - **Analyze relationships**: Understand material flow across processes
    
    ### ⚠️ If you see an empty graph:
    - Make sure the data files are properly formatted
    - Check that the graph construction logic is correct
    - Verify that nodes have proper attributes (type, material, etc.)
    
    Click the button above to load the demo data and get started!
    """)
    
    # Show sample data structure
    with st.expander("📁 Expected Data Structure"):
        st.markdown("""
        Your data should include columns like:
        - `batch_id`: Unique identifier for each batch
        - `type`: "Raw Material", "Intermediate", or "Finished Product"
        - `material`: Description of the material
        - `quantity`: Amount
        - `unit`: Unit of measurement
        - `status`: Batch status
        - `quality`: Quality grade
        """)
