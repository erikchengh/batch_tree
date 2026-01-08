from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx
import tempfile
import os
import json
import re
import streamlit as st
import random

def render_genealogy_graph(G, target_batch_id=None, trace_mode="none"):
    """
    Render a simple pharmaceutical batch tree
    
    Args:
        G: NetworkX graph
        target_batch_id: Batch to focus on
        trace_mode: "none", "forward", "backward", "both"
    """
    
    # Check if graph is empty
    if G is None or G.number_of_nodes() == 0:
        st.warning("⚠️ No graph data available. Please check your data source.")
        return
    
    # Create a simple direct tree
    tree = create_simple_tree(G, target_batch_id)
    
    if tree.number_of_nodes() == 0:
        st.error("❌ Could not create tree from the data")
        return
    
    st.info(f"📊 Rendering batch tree with {tree.number_of_nodes()} nodes and {tree.number_of_edges()} edges")
    
    # Create pyvis network
    net = Network(
        height="700px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#333333",
        notebook=False
    )
    
    # === ADD NODES ===
    node_positions = {}
    level_spacing = 200
    node_spacing = 150
    
    # Get node lists by type
    finished_products = [n for n in tree.nodes() if tree.nodes[n].get("type") == "Finished Product"]
    raw_materials = [n for n in tree.nodes() if tree.nodes[n].get("type") == "Raw Material"]
    
    # Position finished products at top
    y_top = 100
    for i, node in enumerate(finished_products):
        x = 400 + (i - len(finished_products)/2) * node_spacing
        node_positions[node] = (x, y_top)
    
    # Position raw materials at bottom
    y_bottom = 500
    for i, node in enumerate(raw_materials):
        x = 400 + (i - len(raw_materials)/2) * node_spacing
        node_positions[node] = (x, y_bottom)
    
    # Add nodes to network
    for node_id in tree.nodes():
        node_data = tree.nodes[node_id]
        is_target = str(node_id) == str(target_batch_id)
        
        # Get styling
        styling = get_simple_node_styling(node_data, node_id, is_target)
        
        # Get position
        pos = node_positions.get(node_id, (400, 300))
        
        net.add_node(
            str(node_id),
            label=styling["label"],
            color=styling["color"],
            shape=styling["shape"],
            size=styling["size"],
            title=generate_simple_tooltip(node_data, node_id),
            borderWidth=styling["border_width"],
            borderColor=styling["border_color"],
            x=pos[0],
            y=pos[1],
            fixed=True,
            physics=False,
            font={
                "size": styling["font_size"],
                "face": "Arial",
                "color": styling["font_color"],
                "align": "center"
            }
        )
    
    # === ADD EDGES ===
    for u, v, edge_data in tree.edges(data=True):
        net.add_edge(
            str(u),
            str(v),
            color="#4CAF50",
            width=2,
            arrows="to",
            smooth=True
        )
    
    # === SET OPTIONS ===
    options = {
        "physics": {"enabled": False},
        "interaction": {
            "dragNodes": True,
            "dragView": True,
            "zoomView": True,
            "hover": True
        },
        "edges": {
            "smooth": {"type": "straightCross", "roundness": 0.2},
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.8}},
            "color": {"inherit": False}
        },
        "layout": {"improvedLayout": True}
    }
    
    net.set_options(json.dumps(options))
    
    # === SAVE AND RENDER ===
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
            net.save_graph(tmp.name)
            tmp_path = tmp.name
        
        with open(tmp_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Add custom CSS for better appearance
        css = """
        <style>
        .vis-network {
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
        }
        .vis-tooltip {
            background-color: white !important;
            border: 1px solid #ccc !important;
            border-radius: 4px !important;
            padding: 8px !important;
            font-family: Arial !important;
        }
        </style>
        """
        
        # Add legend
        legend = generate_simple_legend(target_batch_id, tree)
        
        html_content = html_content.replace('</head>', f'{css}</head>')
        html_content = html_content.replace('</body>', f'{legend}</body>')
        
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        with open(tmp_path, 'r', encoding='utf-8') as f:
            components.html(f.read(), height=800, scrolling=False)
        
        os.unlink(tmp_path)
        st.success("✅ Batch tree rendered successfully!")
        
    except Exception as e:
        st.error(f"❌ Error rendering tree: {str(e)}")
        st.error("Try checking if pyvis is installed: pip install pyvis")

def create_simple_tree(G, target_batch_id=None):
    """Create a simple tree showing raw materials -> finished product"""
    tree = nx.DiGraph()
    
    if target_batch_id is None or target_batch_id not in G:
        # Get first finished product
        finished_products = [n for n in G.nodes() if G.nodes[n].get("type") == "Finished Product"]
        if finished_products:
            target_batch_id = finished_products[0]
        else:
            return tree
    
    # Add the target product
    tree.add_node(target_batch_id, **G.nodes[target_batch_id])
    
    # Find connected raw materials (skip intermediates)
    raw_materials = []
    visited = set()
    
    def find_raw_materials(node):
        if node in visited:
            return
        visited.add(node)
        
        for predecessor in G.predecessors(node):
            pred_data = G.nodes[predecessor]
            if pred_data.get("type") == "Raw Material":
                raw_materials.append(predecessor)
            else:
                find_raw_materials(predecessor)
    
    find_raw_materials(target_batch_id)
    
    # Add raw materials and connect them to the product
    for rm in raw_materials:
        tree.add_node(rm, **G.nodes[rm])
        tree.add_edge(rm, target_batch_id, relationship="used_in")
    
    return tree

def get_simple_node_styling(node_data, node_id, is_target):
    """Get simple styling for nodes"""
    
    node_type = node_data.get("type", "Unknown")
    material = str(node_data.get("material", "")).upper()
    
    # Colors based on type
    if node_type == "Finished Product":
        color = "#4CAF50"  # Green
        border = "#2E7D32"
        shape = "star"
        size = 40
        font_size = 14
        font_color = "#1B5E20"
    elif node_type == "Raw Material":
        if "API" in material:
            color = "#2196F3"  # Blue for API
            border = "#0D47A1"
        elif any(x in material for x in ["EXCIPIENT", "FILLER", "BINDER"]):
            color = "#FF9800"  # Orange for excipients
            border = "#E65100"
        elif any(x in material for x in ["SOLVENT", "WATER"]):
            color = "#9C27B0"  # Purple for solvents
            border = "#4A148C"
        else:
            color = "#9E9E9E"  # Gray for others
            border = "#616161"
        shape = "circle"
        size = 35
        font_size = 12
        font_color = "#424242"
    else:
        color = "#795548"
        border = "#3E2723"
        shape = "box"
        size = 30
        font_size = 11
        font_color = "#212121"
    
    # Make target larger and bold
    if is_target:
        size = 50
        border_width = 4
        font_size = 16
        font_color = "#D32F2F"
        bold = True
    else:
        border_width = 2
        bold = False
    
    # Create label
    label = format_simple_label(node_id, node_data.get("material", ""))
    
    return {
        "label": label,
        "color": color,
        "border_color": border,
        "shape": shape,
        "size": size,
        "border_width": border_width,
        "font_size": font_size,
        "font_color": font_color,
        "bold": bold,
        "shadow": True
    }

def format_simple_label(batch_id, material):
    """Format labels simply"""
    batch_str = str(batch_id)
    material_str = str(material) if material else ""
    
    # Shorten material
    if len(material_str) > 15:
        material_short = material_str[:15] + "..."
    else:
        material_short = material_str
    
    # Get prefix
    if batch_str.startswith("RM-"):
        prefix = "RM"
    elif batch_str.startswith("FP-"):
        prefix = "FP"
    elif batch_str.startswith("INT-"):
        prefix = "INT"
    else:
        prefix = batch_str.split('-')[0] if '-' in batch_str else batch_str[:3]
    
    # Get numbers
    numbers = re.findall(r'\d+', batch_str)
    number_part = numbers[0] if numbers else ""
    
    return f"{prefix}-{number_part}\n{material_short}"

def generate_simple_tooltip(node_data, node_id):
    """Generate simple tooltip"""
    info = f"""
    <div style="padding: 10px; font-family: Arial; max-width: 300px;">
        <div style="font-weight: bold; color: #1a237e; margin-bottom: 5px;">
            {node_id}
        </div>
        <div style="color: #546e7a; margin-bottom: 3px;">
            <strong>Material:</strong> {node_data.get('material', 'N/A')}
        </div>
        <div style="color: #546e7a; margin-bottom: 3px;">
            <strong>Type:</strong> {node_data.get('type', 'N/A')}
        </div>
        <div style="color: #546e7a; margin-bottom: 3px;">
            <strong>Quantity:</strong> {node_data.get('quantity', 'N/A')} {node_data.get('unit', '')}
        </div>
        <div style="color: #546e7a; margin-bottom: 3px;">
            <strong>Status:</strong> {node_data.get('status', 'N/A')}
        </div>
    </div>
    """
    return info

def generate_simple_legend(target_batch_id, tree):
    """Generate simple legend"""
    if not target_batch_id:
        return ""
    
    target_data = tree.nodes[target_batch_id]
    raw_materials = [n for n in tree.nodes() if tree.nodes[n].get("type") == "Raw Material"]
    
    return f"""
    <div style="
        position: absolute;
        top: 20px;
        right: 20px;
        padding: 15px;
        font-family: Arial, sans-serif;
        font-size: 12px;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
        max-width: 250px;
    ">
        <div style="font-weight: bold; font-size: 14px; color: #1a237e; margin-bottom: 10px; border-bottom: 2px solid #4CAF50; padding-bottom: 5px;">
            🌳 Batch Tree
        </div>
        
        <div style="margin-bottom: 10px; padding: 8px; background: #E8F5E9; border-radius: 4px; border-left: 4px solid #4CAF50;">
            <div style="font-weight: bold; color: #2E7D32; font-size: 12px;">Target Product</div>
            <div style="font-family: monospace; color: #1a237e; font-size: 11px; margin-top: 3px;">{target_batch_id}</div>
            <div style="color: #546e7a; font-size: 10px; margin-top: 2px;">{target_data.get('material', '')}</div>
        </div>
        
        <div style="margin-bottom: 10px;">
            <div style="font-weight: bold; color: #37474f; font-size: 11px; margin-bottom: 5px;">Legend:</div>
            
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 12px; height: 12px; background: #4CAF50; border-radius: 0 50% 50% 50%; transform: rotate(45deg); margin-right: 8px;"></div>
                <div>
                    <div style="font-weight: 600; font-size: 11px; color: #2E7D32;">Finished Product</div>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 12px; height: 12px; background: #2196F3; border-radius: 50%; margin-right: 8px;"></div>
                <div>
                    <div style="font-weight: 600; font-size: 11px; color: #1565C0;">API Materials</div>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 12px; height: 12px; background: #FF9800; border-radius: 50%; margin-right: 8px;"></div>
                <div>
                    <div style="font-weight: 600; font-size: 11px; color: #E65100;">Excipients</div>
                </div>
            </div>
        </div>
        
        <div style="color: #757575; font-size: 10px; border-top: 1px solid #f0f0f0; padding-top: 8px;">
            <div style="margin-bottom: 3px;">Raw Materials: {len(raw_materials)}</div>
            <div>Hover over nodes for details</div>
        </div>
    </div>
    """
