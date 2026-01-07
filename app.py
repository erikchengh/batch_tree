import streamlit as st
from data_mock import load_mock_batch
from model import build_batch_graph
from graph_view import render_graph

st.set_page_config(page_title="PAS-X Genealogy", layout="wide")

# --- Styles ---
st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 5px solid #2ecc71; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏭 PAS-X Batch Genealogy & Trace")

# --- Data Load ---
data = load_mock_batch("B001")
G = build_batch_graph(data)

# --- Sidebar Controls ---
with st.sidebar:
    st.header("🎮 Controls")
    
    st.subheader("1. View Mode")
    dev_mode = st.toggle("🔍 Deviation Focus", value=False)
    
    st.subheader("2. Genealogy Trace")
    # Only show trace options if not in deviation mode (to avoid conflict)
    if not dev_mode:
        trace_mode = st.radio(
            "Trace Direction:",
            ["None", "Backward", "Forward", "Bidirectional"],
            index=0,
            help="Trace material flow or process sequence"
        )
    else:
        trace_mode = "None"
        st.info("Tracing disabled in Deviation Mode")

    st.divider()
    
    # Navigation
    node_options = list(G.nodes)
    # Default to a Material node for demo purposes if available
    mat_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'Material']
    default_ix = node_options.index(mat_nodes[0]) if mat_nodes else 0
    
    selected_node = st.selectbox("Select Node", node_options, index=default_ix)

# --- Main Dashboard ---
col_tree, col_graph = st.columns([1, 2.5])

with col_tree:
    st.subheader("Hierarchy")
    # Simple list view to complement the graph
    for phase in data["phases"]:
        with st.expander(f"📁 {phase['name']}", expanded=True):
            for pi in data["pis"]:
                if pi["phase"] == phase["id"]:
                    if st.button(f"🔹 {pi['name']}", key=pi['id'], use_container_width=True):
                        st.session_state.selected_node = pi['id']
                        st.rerun() # Force reload to update graph selection

with col_graph:
    st.subheader("Interactive Graph")
    render_graph(
        G, 
        selected_node=selected_node, 
        deviation_only=dev_mode, 
        trace_mode=trace_mode
    )

# --- Footer Details ---
st.divider()
if selected_node:
    n_data = G.nodes[selected_node]
    st.markdown(f"**Selected:** `{n_data['label']}` | **Type:** `{n_data['type']}`")

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

# import streamlit as st
# from data_mock import load_mock_batch
# from model import build_batch_graph
# from graph_view import render_graph

# # -----------------------------
# # Page configuration
# # -----------------------------
# st.set_page_config(
#     page_title="PAS-X Batch Tree Dashboard",
#     layout="wide"
# )

# st.title("🏭 PAS-X Batch Tree Dashboard")
# st.caption("Execution hierarchy • genealogy • deviation insight")

# # -----------------------------
# # Session state
# # -----------------------------
# if "selected_node" not in st.session_state:
#     st.session_state.selected_node = None

# # -----------------------------
# # Batch selector
# # -----------------------------
# batch_id = st.selectbox("Select Batch", ["B001"])

# # -----------------------------
# # Load data & build graph
# # -----------------------------
# data = load_mock_batch(batch_id)
# G = build_batch_graph(data)

# # -----------------------------
# # KPI Summary
# # -----------------------------
# failed_pis = [
#     pi for pi in data["pis"] if pi["result"] == "FAIL"
# ]

# k1, k2, k3, k4 = st.columns(4)
# k1.metric("Batch Status", data["batch"]["status"])
# k2.metric("Phases", len(data["phases"]))
# k3.metric("Total PIs", len(data["pis"]))
# k4.metric("Failed PIs", len(failed_pis))

# st.divider()

# # -----------------------------
# # Node selector (Graph ↔ UI bridge)
# # -----------------------------
# with st.sidebar:
#     st.subheader("🧩 Graph Selection")
#     node_ids = list(G.nodes)
#     st.session_state.selected_node = st.selectbox(
#         "Selected Node",
#         node_ids,
#         index=node_ids.index(st.session_state.selected_node)
#         if st.session_state.selected_node in node_ids
#         else 0
#     )

# # -----------------------------
# # Main layout
# # -----------------------------
# left, right = st.columns([1.1, 2])

# # LEFT: Hierarchy Tree
# with left:
#     st.subheader("📋 Batch Hierarchy")
#     st.markdown(f"**Batch {batch_id}**  \nProduct: `{data['batch']['product']}`")

#     for phase in data["phases"]:
#         with st.expander(f"⚙️ {phase['name']}", expanded=True):
#             for pi in data["pis"]:
#                 if pi["phase"] == phase["id"]:
#                     icon = "❌" if pi["result"] == "FAIL" else "✅"
#                     if st.button(
#                         f"{icon} {pi['name']}",
#                         key=pi["id"],
#                         use_container_width=True
#                     ):
#                         st.session_state.selected_node = pi["id"]

# # RIGHT: Graph
# with right:
#     st.subheader("🧭 Execution & Genealogy Graph")
#     render_graph(G, selected_node=st.session_state.selected_node)

# # -----------------------------
# # Details Panel
# # -----------------------------
# st.divider()
# st.subheader("🔍 Details")

# if st.session_state.selected_node:
#     node = st.session_state.selected_node
#     data_node = G.nodes[node]

#     st.markdown(f"### {data_node['label']}")
#     st.markdown(f"**Type:** `{data_node['type']}`")

#     if data_node["type"] == "PI":
#         status_icon = "❌" if data_node.get("result") == "FAIL" else "✅"
#         st.markdown(f"**Result:** {status_icon} `{data_node.get('result')}`")

#     st.markdown("#### Metadata")
#     st.json(data_node)
# else:
#     st.info("Select a node from the hierarchy or graph.")


