import streamlit as st
import pandas as pd
from model import (
    build_batch_genealogy_graph, 
    get_bom_list, 
    get_product_list, 
    analyze_graph,
    get_batch_quality_summary,
    trace_forward,
    trace_backward
)
from graph_view import render_genealogy_graph
import json

# Page configuration
st.set_page_config(
    page_title="Pharma Batch Genealogy | GMP Traceability",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        
