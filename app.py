import streamlit as st
from data_mock import load_mock_batch
from model import build_batch_graph
from graph_view import render_graph

st.set_page_config(page_title="PAS-X Batch Genealogy", layout="wide")
st.title("PAS-X Batch Genealogy & Material Trace")

# -------------------------
# Load Data
# -------------------------
batch_id = st.selectbox("Select Batch", ["B001"])
data = load_mock_batch(batch_id)
G = build_batch_graph(data)

# -------------------------
# Sidebar Controls
# -------------------------
with st.sidebar:
    st.header("Visualization Controls")

    trace_mode = st.radio(
        "Trace Mode",
        ["None", "Backward", "Forward", "Bidirectional"],
        index=0
    )

    selected_node = st.selectbox(
        "Select Record",
        list(G.nodes)
    )

# -------------------------
# Layout
# -------------------------
col_tree, col_graph = st.columns([1.1, 2.4])

with col_tree:
    st.subheader("Electronic Batch Record")

    st.markdown(
        f"""
        <div style="padding:10px; background:#f4f6f8; border-left:6px solid #1e88e5;">
        <b>Batch {data['batch']['id']}</b><br>
        Product: {data['batch']['product']}<br>
        Status: {data['batch']['status']}
        </div>
        """,
        unsafe_allow_html=True
    )

    for phase in data["phases"]:
        st.markdown(
            f"""
            <div style="margin-top:12px; padding:8px; background:#eef2f5; font-weight:600;">
            Phase {phase['id']} – {phase['name']}
            </div>
            """,
            unsafe_allow_html=True
        )

        for pi in data["pis"]:
            if pi["phase"] == phase["id"]:
                status_color = "#2e7d32" if pi["result"] == "PASS" else "#c62828"
                status_text = "IN SPEC" if pi["result"] == "PASS" else "DEVIATION"

                if st.button(
                    f"{pi['id']} – {pi['name']}",
                    key=pi["id"],
                    use_container_width=True
                ):
                    selected_node = pi["id"]
                    st.rerun()

                st.markdown(
                    f"<div style='margin-left:12px; color:{status_color}; font-size:12px;'>"
                    f"Result: {status_text}</div>",
                    unsafe_allow_html=True
                )

with col_graph:
    st.subheader("Batch Genealogy View")
    render_graph(G, selected_node=selected_node, trace_mode=trace_mode)
