from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx
import tempfile
import os
import json
import re
import streamlit as st
import math
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# Professional pharmaceutical color scheme (based on USP/FDA guidelines)
PHARMA_COLORS = {
    # Material Classes
    "API": {"primary": "#1565C0", "secondary": "#1976D2", "light": "#E3F2FD", "icon": "🧬"},
    "EXCIPIENT": {"primary": "#2E7D32", "secondary": "#43A047", "light": "#E8F5E9", "icon": "📦"},
    "PROCESS_AID": {"primary": "#6A1B9A", "secondary": "#7B1FA2", "light": "#F3E5F5", "icon": "💧"},
    "INTERMEDIATE": {"primary": "#E65100", "secondary": "#EF6C00", "light": "#FFF3E0", "icon": "⚗️"},
    "BULK": {"primary": "#00838F", "secondary": "#00ACC1", "light": "#E0F7FA", "icon": "🏭"},
    "FINISHED": {"primary": "#C62828", "secondary": "#D32F2F", "light": "#FFEBEE", "icon": "💊"},
    
    # Quality Statuses
    "RELEASED": {"color": "#2E7D32", "icon": "✅"},
    "QUARANTINE": {"color": "#F57C00", "icon": "⏳"},
    "PENDING_QC": {"color": "#7B1FA2", "icon": "🔬"},
    "REJECTED": {"color": "#C62828", "icon": "❌"},
    "ON_HOLD": {"color": "#FF5722", "icon": "⚠️"},
    
    # Process Stages
    "DISPENSING": {"color": "#5D4037", "icon": "⚖️"},
    "GRANULATION": {"color": "#F4511E", "icon": "🔄"},
    "BLENDING": {"color": "#FB8C00", "icon": "🌀"},
    "COMPRESSION": {"color": "#43A047", "icon": "⬇️"},
    "COATING": {"color": "#00ACC1", "icon": "🎨"},
    "ENCAPSULATION": {"color": "#8E24AA", "icon": "💊"},
    "PACKAGING": {"color": "#3949AB", "icon": "📦"},
    "RELEASE": {"color": "#00897B", "icon": "✅"}
}


def render_genealogy_graph(G: nx.DiGraph, target_batch_id: Optional[str] = None, trace_mode: str = "none"):
    """
    Render professional pharmaceutical batch genealogy visualization
    Compliant with FDA 21 CFR Part 11 display requirements
    """
    
    if G is None or G.number_of_nodes() == 0:
        st.warning("⚠️ No batch data available for visualization.")
        return
    
    # Create subgraph for visualization
    if target_batch_id and target_batch_id in G.nodes():
        viz_graph = create_genealogy_subgraph(G, target_batch_id, trace_mode)
    else:
        viz_graph = G.copy()
    
    if viz_graph.number_of_nodes() == 0:
        st.error("❌ Could not create visualization from the data")
        return
    
    # Display graph statistics
    display_graph_stats(viz_graph, target_batch_id)
    
    # Create PyVis network
    net = Network(
        height="800px",
        width="100%",
        directed=True,
        bgcolor="#FAFBFC",
        font_color="#1E293B",
        notebook=False
    )
    
    # Calculate hierarchical layout
    positions = calculate_hierarchical_layout(viz_graph, target_batch_id)
    
    # Add nodes with professional pharmaceutical styling
    for node_id, node_data in viz_graph.nodes(data=True):
        styling = get_pharma_node_styling(node_data, node_id, target_batch_id, trace_mode)
        pos = positions.get(node_id, {"x": 0, "y": 0})
        
        net.add_node(
            str(node_id),
            label=styling["label"],
            title=styling["tooltip"],
            color={
                "background": styling["background"],
                "border": styling["border"],
                "highlight": {"background": styling["highlight_bg"], "border": styling["highlight_border"]}
            },
            shape=styling["shape"],
            size=styling["size"],
            borderWidth=styling["border_width"],
            x=pos["x"],
            y=pos["y"],
            fixed=True,
            physics=False,
            font={
                "size": styling["font_size"],
                "face": "'Inter', 'Segoe UI', system-ui, sans-serif",
                "color": styling["font_color"],
                "align": "center",
                "bold": styling["bold"],
                "multi": True
            },
            shadow={
                "enabled": True,
                "color": "rgba(0,0,0,0.12)",
                "size": 8,
                "x": 2,
                "y": 4
            }
        )
    
    # Add edges with professional styling
    for u, v, edge_data in viz_graph.edges(data=True):
        styling = get_pharma_edge_styling(u, v, edge_data, target_batch_id, viz_graph)
        
        net.add_edge(
            str(u),
            str(v),
            color={"color": styling["color"], "opacity": styling["opacity"]},
            width=styling["width"],
            arrows={"to": {"enabled": True, "scaleFactor": 1.0, "type": "arrow"}},
            smooth={"type": "cubicBezier", "roundness": 0.3},
            dashes=styling["dashes"],
            title=styling["title"],
            label=styling.get("label", ""),
            font={"size": 10, "color": "#64748B", "align": "horizontal"},
            length=styling["length"]
        )
    
    # Configure visualization options
    config = create_network_config()
    net.set_options(json.dumps(config))
    
    # Render the network
    render_network(net, target_batch_id, viz_graph)


def create_genealogy_subgraph(G: nx.DiGraph, target_batch_id: str, trace_mode: str) -> nx.DiGraph:
    """Create a subgraph focused on the target batch"""
    subgraph = nx.DiGraph()
    
    # Always include target
    if target_batch_id in G.nodes():
        subgraph.add_node(target_batch_id, **G.nodes[target_batch_id])
    
    # Get ancestors (backward trace)
    ancestors = nx.ancestors(G, target_batch_id)
    for ancestor in ancestors:
        subgraph.add_node(ancestor, **G.nodes[ancestor])
    
    # Get descendants (forward trace) if target is not a finished product
    node_type = G.nodes[target_batch_id].get("type", "")
    if node_type != "Finished Product":
        descendants = nx.descendants(G, target_batch_id)
        for descendant in descendants:
            subgraph.add_node(descendant, **G.nodes[descendant])
    
    # Add edges
    all_nodes = set(subgraph.nodes())
    for u, v, data in G.edges(data=True):
        if u in all_nodes and v in all_nodes:
            subgraph.add_edge(u, v, **data)
    
    return subgraph


def calculate_hierarchical_layout(G: nx.DiGraph, target_batch_id: Optional[str] = None) -> Dict:
    """Calculate hierarchical positions for batch genealogy"""
    positions = {}
    
    if G.number_of_nodes() == 0:
        return positions
    
    # Group nodes by type/stage
    layers = {
        "Raw Material": [],
        "Intermediate": [],
        "Finished Product": []
    }
    
    for node in G.nodes():
        node_type = G.nodes[node].get("type", "Unknown")
        if node_type in layers:
            layers[node_type].append(node)
        else:
            # Check process stage for intermediates
            process_stage = G.nodes[node].get("process_stage", "")
            if process_stage:
                layers["Intermediate"].append(node)
            else:
                layers["Raw Material"].append(node)
    
    # Sort intermediates by process stage order
    stage_order = {"GRANULATION": 1, "BLENDING": 2, "COMPRESSION": 3, "COATING": 4, "ENCAPSULATION": 4, "PACKAGING": 5}
    layers["Intermediate"].sort(key=lambda x: stage_order.get(G.nodes[x].get("process_stage", ""), 99))
    
    # Calculate positions
    canvas_width = 1200
    canvas_height = 800
    
    y_positions = {
        "Raw Material": 50,
        "Intermediate": 300,
        "Finished Product": 550
    }
    
    for layer_name, nodes in layers.items():
        if not nodes:
            continue
        
        y = y_positions.get(layer_name, 300)
        n = len(nodes)
        
        if n == 1:
            positions[nodes[0]] = {"x": canvas_width // 2, "y": y}
        else:
            spacing = min(canvas_width // (n + 1), 200)
            start_x = (canvas_width - (n - 1) * spacing) // 2
            
            for i, node in enumerate(nodes):
                positions[node] = {"x": start_x + i * spacing, "y": y}
    
    # Adjust for intermediate sub-layers
    intermediate_nodes = layers["Intermediate"]
    if intermediate_nodes:
        stages = defaultdict(list)
        for node in intermediate_nodes:
            stage = G.nodes[node].get("process_stage", "OTHER")
            stages[stage].append(node)
        
        stage_y_offset = 0
        for stage, nodes in sorted(stages.items(), key=lambda x: stage_order.get(x[0], 99)):
            for node in nodes:
                if node in positions:
                    positions[node]["y"] += stage_y_offset
            stage_y_offset += 80
    
    return positions


def get_pharma_node_styling(node_data: Dict, node_id: str, target_batch_id: Optional[str], trace_mode: str) -> Dict:
    """Get professional pharmaceutical node styling"""
    
    node_type = node_data.get("type", "Unknown")
    material_class = node_data.get("material_class", "")
    status = node_data.get("status", "QUARANTINE")
    process_stage = node_data.get("process_stage", "")
    is_target = str(node_id) == str(target_batch_id)
    
    # Get color scheme based on material class
    if material_class in PHARMA_COLORS:
        colors = PHARMA_COLORS[material_class]
        primary = colors["primary"]
        secondary = colors["secondary"]
        light = colors["light"]
        icon = colors["icon"]
    else:
        # Default colors based on node type
        if node_type == "Raw Material":
            primary, secondary, light = "#1565C0", "#1976D2", "#E3F2FD"
            icon = "📦"
        elif node_type == "Intermediate":
            primary, secondary, light = "#E65100", "#EF6C00", "#FFF3E0"
            icon = "⚗️"
        elif node_type == "Finished Product":
            primary, secondary, light = "#C62828", "#D32F2F", "#FFEBEE"
            icon = "💊"
        else:
            primary, secondary, light = "#607D8B", "#78909C", "#ECEFF1"
            icon = "📋"
    
    # Override icon based on specific material type
    material_name = str(node_data.get("material_name", "")).upper()
    if "API" in material_class or "API" in material_name:
        icon = "🧬"
    elif "WATER" in material_name or "SOLVENT" in material_name:
        icon = "💧"
    elif "TABLET" in material_name:
        icon = "💊"
    elif "CAPSULE" in material_name:
        icon = "💊"
    elif "COATING" in material_name or "OPADRY" in material_name:
        icon = "🎨"
    elif "BLEND" in material_name or "GRANUL" in material_name:
        icon = "🔄"
    
    # Determine shape based on node type
    if node_type == "Finished Product":
        shape = "star"
    elif node_type == "Intermediate":
        shape = "hexagon"
    elif material_class == "API":
        shape = "diamond"
    else:
        shape = "dot"
    
    # Size and styling based on importance
    if is_target:
        size = 55
        border_width = 4
        font_size = 14
        bold = True
        background = primary
        border = "#FFB300"  # Gold border for target
        highlight_bg = secondary
        highlight_border = "#FFC107"
    elif node_type == "Finished Product":
        size = 50
        border_width = 3
        font_size = 13
        bold = True
        background = primary
        border = secondary
        highlight_bg = secondary
        highlight_border = primary
    elif node_type == "Intermediate":
        size = 42
        border_width = 2
        font_size = 12
        bold = False
        background = primary
        border = secondary
        highlight_bg = secondary
        highlight_border = primary
    else:  # Raw materials
        size = 38
        border_width = 2
        font_size = 11
        bold = False
        background = primary
        border = secondary
        highlight_bg = secondary
        highlight_border = primary
    
    # Create label
    label = format_pharma_node_label(node_id, node_data, icon)
    
    # Create 
