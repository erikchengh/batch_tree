import streamlit as st
from data_mock import load_mock_batch
from model import build_batch_graph
from graph_view import render_graph

st.set_page_config(page_title="PAS-X Professional Dashboard", layout="wide")
st.title("🏭 PAS-X Batch Genealogy & Trace Dashboard")

# --- Load data ---
batch_id = st.selectbox("Select Batch", ["B001"])
data = load_mock_batch(batch_id)
G = build_batch_graph(data)

# --- Sidebar Controls ---
with st.sidebar:
    st.header("🎮 Controls")
    dev_mode = st.toggle("🔍 Deviation Focus", value=False)

    st.subheader("Trace Mode")
    trace_mode = st.radio("Select Trace Direction", ["None", "Backward", "Forward", "Bidirectional"], index=0)

    node_options = list(G.nodes)
    selected_node = st.selectbox("Select Node", node_options, index=0)

# --- Main Layout ---
col_tree, col_graph = st.columns([1, 2.5])

# Left: Hierarchy
with col_tree:
    st.subheader("Hierarchy View")
    for phase in data["phases"]:
        with st.expander(f"📁 {phase['name']}", expanded=True):
            for pi in data["pis"]:
                if pi["phase"] == phase["id"]:
                    icon = "❌" if pi["result"]=="FAIL" else "✅"
                    if st.button(f"{icon} {pi['name']}", key=pi['id'], use_container_width=True):
                        selected_node = pi['id']
                        st.experimental_rerun()

# Right: Professional Graph
with col_graph:
    st.subheader("Interactive Batch Graph")
    render_graph(G, selected_node=selected_node, deviation_only=dev_mode, trace_mode=trace_mode)

# --- Footer Details ---
st.divider()
if selected_node:
    n_data = G.nodes[selected_node]
    st.markdown(f"**Selected Node:** `{n_data['label']}` | **Type:** `{n_data['type']}`")
    st.json(n_data)
else:
    st.info("Select a node from the hierarchy or graph to view details.")
