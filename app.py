import streamlit as st
from data_mock import load_mock_batch
from model import build_batch_graph
from graph_view import render_graph

st.set_page_config(
    page_title="MES Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        padding-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        margin: 0.5rem 0;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🏭 MES Batch Genealogy & Material Trace Dashboard</h1>", unsafe_allow_html=True)

# Load data
batch_id = st.selectbox("Select Batch", ["B001", "B002", "B003"], help="Choose a batch to visualize")
data = load_mock_batch(batch_id)
G = build_batch_graph(data)

# Sidebar with improved styling
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    st.divider()
    
    st.markdown("**Visualization Settings**")
    dev_mode = st.toggle("🔍 Focus on Deviations", value=False, 
                        help="Dim non-failing nodes")
    
    trace_mode = st.selectbox(
        "🔗 Trace Mode",
        ["None", "Backward", "Forward", "Bidirectional", "MaterialGenealogy"],
        index=0,
        help="Highlight connected nodes in trace"
    )
    
    st.divider()
    st.markdown("**Node Selection**")
    node_options = list(G.nodes)
    selected_node = st.selectbox("Select Node", node_options, index=0)
    
    # Display node info in sidebar if selected
    if selected_node:
        st.divider()
        n_data = G.nodes[selected_node]
        st.markdown(f"**Selected:** `{n_data['label']}`")
        st.markdown(f"**Type:** `{n_data['type']}`")
        if n_data.get("result"):
            st.markdown(f"**Result:** `{n_data['result']}`")

# Layout with better proportions
col_tree, col_graph = st.columns([1, 3])

# Hierarchy Tree with improved styling
with col_tree:
    st.markdown("### 📁 Hierarchy View")
    
    # Summary metrics
    total_pis = len([pi for pi in data["pis"]])
    failed_pis = len([pi for pi in data["pis"] if pi["result"] == "FAIL"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total PIs", total_pis)
    with col2:
        st.metric("Failed", failed_pis, delta=f"-{failed_pis}" if failed_pis else None)
    
    # Phases with expanders
    for phase in data["phases"]:
        phase_pis = [pi for pi in data["pis"] if pi["phase"] == phase["id"]]
        phase_fails = len([pi for pi in phase_pis if pi["result"] == "FAIL"])
        
        with st.expander(
            f"📂 {phase['name']} ({phase_fails} ⚠️)" if phase_fails else f"📂 {phase['name']}",
            expanded=True
        ):
            for pi in phase_pis:
                # Determine button color based on result
                if pi["result"] == "FAIL":
                    button_style = "background-color: #ffeaea; color: #c0392b; border-color: #e74c3c;"
                    icon = "❌"
                else:
                    button_style = "background-color: #eafaf1; color: #27ae60; border-color: #2ecc71;"
                    icon = "✅"
                
                # Create a styled button
                if st.button(
                    f"{icon} {pi['name']}",
                    key=pi['id'],
                    use_container_width=True,
                    help=f"Click to select {pi['name']}"
                ):
                    selected_node = pi['id']
                    st.rerun()

# Graph Visualization
with col_graph:
    st.markdown("### 📊 Interactive Batch Graph")
    
    # Graph controls
    col_graph_ctrl1, col_graph_ctrl2 = st.columns(2)
    with col_graph_ctrl1:
        if st.button("🔄 Reset View", use_container_width=True):
            # Could implement reset logic here
            pass
    
    # Render the improved graph
    render_graph(G, 
                selected_node=selected_node, 
                deviation_only=dev_mode, 
                trace_mode=trace_mode)

# Footer with detailed information
st.divider()
st.markdown("### 📋 Node Details")

if selected_node:
    n_data = G.nodes[selected_node]
    
    # Create a nice details panel
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"**Node ID:** `{selected_node}`")
        st.markdown(f"**Type:** `{n_data['type']}`")
        if n_data.get("result"):
            st.markdown(f"**Result:** `{n_data['result']}`")
    
    with col2:
        details = []
        for k in ["parameters", "limits", "timestamp", "deviation", "product", "status"]:
            if k in n_data and n_data[k]:
                details.append(f"**{k.capitalize()}:** `{n_data[k]}`")
        
        if details:
            st.markdown("\n".join(details))
        else:
            st.info("No additional details available for this node.")
else:
    st.info("👆 Select a node from the hierarchy or graph to view detailed information.")
