# import streamlit as st
# from data_mock import load_mock_batch
# from model import build_batch_graph
# from graph_view import render_graph

# st.set_page_config(layout="wide")
# st.title("PAS-X Batch Tree Dashboard (POC)")

# # Batch selector
# batch_id = st.selectbox("Select Batch", ["B001"])

# # Load data
# data = load_mock_batch(batch_id)

# # Build graph
# G = build_batch_graph(data)

# # Layout
# left, right = st.columns([1, 2])

# with left:
#     st.subheader("Batch Hierarchy")

#     st.markdown(f"**Batch {batch_id}**")
#     for p in data["phases"]:
#         st.markdown(f"- **{p['name']}**")
#         for pi in data["pis"]:
#             if pi["phase"] == p["id"]:
#                 icon = "❌" if pi["result"] == "FAIL" else "✔️"
#                 st.markdown(f"  - {pi['name']} {icon}")

# with right:
#     st.subheader("Execution Graph")
#     render_graph(G)

# st.divider()

# st.subheader("Details Panel")
# st.info("Click interaction comes next (node → parameters, limits, materials)")

import streamlit as st
from data_mock import load_mock_batch
from model import build_batch_graph
from graph_view import render_graph

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="PAS-X Batch Tree Dashboard",
    layout="wide"
)

st.title("🏭 PAS-X Batch Tree Dashboard")
st.caption("Execution hierarchy • genealogy • deviation insight")

# -----------------------------
# Session state
# -----------------------------
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None

# -----------------------------
# Batch selector
# -----------------------------
batch_id = st.selectbox("Select Batch", ["B001"])

# -----------------------------
# Load data & build graph
# -----------------------------
data = load_mock_batch(batch_id)
G = build_batch_graph(data)

# -----------------------------
# KPI Summary
# -----------------------------
failed_pis = [
    pi for pi in data["pis"] if pi["result"] == "FAIL"
]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Batch Status", data["batch"]["status"])
k2.metric("Phases", len(data["phases"]))
k3.metric("Total PIs", len(data["pis"]))
k4.metric("Failed PIs", len(failed_pis))

st.divider()

# -----------------------------
# Node selector (Graph ↔ UI bridge)
# -----------------------------
with st.sidebar:
    st.subheader("🧩 Graph Selection")
    node_ids = list(G.nodes)
    st.session_state.selected_node = st.selectbox(
        "Selected Node",
        node_ids,
        index=node_ids.index(st.session_state.selected_node)
        if st.session_state.selected_node in node_ids
        else 0
    )

# -----------------------------
# Main layout
# -----------------------------
left, right = st.columns([1.1, 2])

# LEFT: Hierarchy Tree
with left:
    st.subheader("📋 Batch Hierarchy")
    st.markdown(f"**Batch {batch_id}**  \nProduct: `{data['batch']['product']}`")

    for phase in data["phases"]:
        with st.expander(f"⚙️ {phase['name']}", expanded=True):
            for pi in data["pis"]:
                if pi["phase"] == phase["id"]:
                    icon = "❌" if pi["result"] == "FAIL" else "✅"
                    if st.button(
                        f"{icon} {pi['name']}",
                        key=pi["id"],
                        use_container_width=True
                    ):
                        st.session_state.selected_node = pi["id"]

# RIGHT: Graph
with right:
    st.subheader("🧭 Execution & Genealogy Graph")
    render_graph(G, selected_node=st.session_state.selected_node)

# -----------------------------
# Details Panel
# -----------------------------
st.divider()
st.subheader("🔍 Details")

if st.session_state.selected_node:
    node = st.session_state.selected_node
    data_node = G.nodes[node]

    st.markdown(f"### {data_node['label']}")
    st.markdown(f"**Type:** `{data_node['type']}`")

    if data_node["type"] == "PI":
        status_icon = "❌" if data_node.get("result") == "FAIL" else "✅"
        st.markdown(f"**Result:** {status_icon} `{data_node.get('result')}`")

    st.markdown("#### Metadata")
    st.json(data_node)
else:
    st.info("Select a node from the hierarchy or graph.")


