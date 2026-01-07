import streamlit as st
from data_mock import load_mock_batch
from model import build_batch_graph
from graph_view import render_graph

st.set_page_config(layout="wide")
st.title("PAS-X Batch Tree Dashboard (POC)")

# Batch selector
batch_id = st.selectbox("Select Batch", ["B001"])

# Load data
data = load_mock_batch(batch_id)

# Build graph
G = build_batch_graph(data)

# Layout
left, right = st.columns([1, 2])

with left:
    st.subheader("Batch Hierarchy")

    st.markdown(f"**Batch {batch_id}**")
    for p in data["phases"]:
        st.markdown(f"- **{p['name']}**")
        for pi in data["pis"]:
            if pi["phase"] == p["id"]:
                icon = "❌" if pi["result"] == "FAIL" else "✔️"
                st.markdown(f"  - {pi['name']} {icon}")

with right:
    st.subheader("Execution Graph")
    render_graph(G)

st.divider()

st.subheader("Details Panel")
st.info("Click interaction comes next (node → parameters, limits, materials)")

