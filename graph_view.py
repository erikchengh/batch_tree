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

def render_genealogy_graph(G, target_batch_id=None, trace_mode="none"):
    """
    Render a professional pharmaceutical batch tree with icons
    """
    
    if G is None or G.number_of_nodes() == 0:
        st.warning("⚠️ No graph data available.")
        return
    
    # Create a proper tree structure
    tree = create_pharma_tree(G, target_batch_id)
    
    if tree.number_of_nodes() == 0:
        st.error("❌ Could not create tree from the data")
        return
    
    st.info(f"🌳 Batch Tree: {tree.number_of_nodes()} nodes, {tree.number_of_edges()} edges")
    
    # Create network
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#f8fafc",
        font_color="#1e293b",
        notebook=False
    )
    
    # Calculate hierarchical positions
    positions = calculate_tree_layout(tree, target_batch_id)
    
    # Add nodes with professional styling
    for node_id, node_data in tree.nodes(data=True):
        styling = get_pharma_tree_node_styling(node_data, node_id, target_batch_id)
        pos = positions.get(node_id, {"x": 0, "y": 0})
        
        net.add_node(
            str(node_id),
            label=styling["label"],
            title=styling["tooltip"],
            color=styling["color"],
            shape=styling["shape"],
            size=styling["size"],
            borderWidth=styling["border_width"],
            borderColor=styling["border_color"],
            x=pos["x"],
            y=pos["y"],
            fixed=True,
            physics=False,
            font={
                "size": styling["font_size"],
                "face": "Segoe UI, Arial, sans-serif",
                "color": styling["font_color"],
                "align": "center",
                "bold": styling["bold"]
            },
            shadow=True
        )
    
    # Add edges with professional styling
    for u, v, edge_data in tree.edges(data=True):
        styling = get_pharma_tree_edge_styling(u, v, edge_data, target_batch_id)
        
        net.add_edge(
            str(u),
            str(v),
            color=styling["color"],
            width=styling["width"],
            arrows={"to": {"enabled": True, "scaleFactor": 1.2}},
            smooth={"type": "cubicBezier", "roundness": 0.4},
            dashes=styling["dashes"],
            font=styling["font"],
            label=styling.get("label", ""),
            length=styling["length"]
        )
    
    # Configure tree layout
    config = {
        "physics": {"enabled": False},
        "interaction": {
            "dragNodes": True,
            "dragView": True,
            "zoomView": True,
            "hover": True,
            "tooltipDelay": 200,
            "navigationButtons": True
        },
        "edges": {
            "smooth": {"enabled": True, "type": "cubicBezier", "roundness": 0.3},
            "color": {"inherit": False},
            "arrows": {"to": {"enabled": True, "scaleFactor": 1.2}},
            "shadow": {"enabled": True, "color": "rgba(0,0,0,0.1)", "size": 3}
        },
        "nodes": {
            "shape": "dot",
            "font": {"align": "center"},
            "shadow": {"enabled": True, "color": "rgba(0,0,0,0.15)", "size": 5},
            "borderWidth": 2,
            "scaling": {"min": 20, "max": 60}
        },
        "layout": {
            "improvedLayout": True,
            "hierarchical": {
                "enabled": False
            }
        }
    }
    
    net.set_options(json.dumps(config))
    
    # Save and render
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
            net.save_graph(tmp.name)
            tmp_path = tmp.name
        
        with open(tmp_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Add custom CSS for pharmaceutical theme
        css = """
        <style>
        .vis-network {
            border: 2px solid #e2e8f0 !important;
            border-radius: 12px !important;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
        }
        .vis-tooltip {
            background: white !important;
            border: 2px solid #cbd5e1 !important;
            border-radius: 8px !important;
            padding: 12px !important;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
            max-width: 320px !important;
        }
        .vis-tooltip h3 {
            color: #1e3a8a !important;
            margin-top: 0 !important;
            border-bottom: 2px solid #e2e8f0 !important;
            padding-bottom: 8px !important;
        }
        </style>
        """
        
        legend = generate_pharma_tree_legend(target_batch_id, tree)
        
        html_content = html_content.replace('</head>', f'{css}</head>')
        html_content = html_content.replace('</body>', f'{legend}</body>')
        
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        with open(tmp_path, 'r', encoding='utf-8') as f:
            components.html(f.read(), height=800, scrolling=False)
        
        os.unlink(tmp_path)
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def create_pharma_tree(G, target_batch_id=None):
    """Create a pharmaceutical batch tree"""
    tree = nx.DiGraph()
    
    if target_batch_id is None or target_batch_id not in G:
        # Get first finished product
        finished_products = [n for n in G.nodes() if G.nodes[n].get("type") == "Finished Product"]
        if finished_products:
            target_batch_id = finished_products[0]
        else:
            return tree
    
    target_data = G.nodes[target_batch_id]
    target_type = target_data.get("type", "Unknown")
    
    # Add target as root
    tree.add_node(target_batch_id, **target_data)
    
    if target_type == "Finished Product":
        # Find all raw materials that go into this product
        raw_materials = find_direct_raw_materials(G, target_batch_id)
        
        for rm in raw_materials:
            tree.add_node(rm, **G.nodes[rm])
            tree.add_edge(rm, target_batch_id, 
                         relationship="used_in",
                         quantity=G[rm][target_batch_id].get("quantity", "") if G.has_edge(rm, target_batch_id) else "",
                         unit=G[rm][target_batch_id].get("unit", "") if G.has_edge(rm, target_batch_id) else "")
    
    elif target_type == "Raw Material":
        # Find all finished products that use this material
        finished_products = find_direct_finished_products(G, target_batch_id)
        
        for fp in finished_products:
            tree.add_node(fp, **G.nodes[fp])
            tree.add_edge(target_batch_id, fp,
                         relationship="used_in",
                         quantity=G[target_batch_id][fp].get("quantity", "") if G.has_edge(target_batch_id, fp) else "",
                         unit=G[target_batch_id][fp].get("unit", "") if G.has_edge(target_batch_id, fp) else "")
    
    return tree

def find_direct_raw_materials(G, node):
    """Find direct raw material predecessors"""
    raw_materials = []
    visited = set()
    
    to_visit = [node]
    
    while to_visit:
        current = to_visit.pop(0)
        if current in visited:
            continue
        visited.add(current)
        
        for predecessor in G.predecessors(current):
            if predecessor in visited:
                continue
            
            pred_type = G.nodes[predecessor].get("type")
            if pred_type == "Raw Material":
                raw_materials.append(predecessor)
            elif pred_type == "Intermediate":
                # Skip intermediate, continue exploring
                to_visit.append(predecessor)
    
    return list(set(raw_materials))

def find_direct_finished_products(G, node):
    """Find direct finished product successors"""
    finished_products = []
    visited = set()
    
    to_visit = [node]
    
    while to_visit:
        current = to_visit.pop(0)
        if current in visited:
            continue
        visited.add(current)
        
        for successor in G.successors(current):
            if successor in visited:
                continue
            
            succ_type = G.nodes[successor].get("type")
            if succ_type == "Finished Product":
                finished_products.append(successor)
            elif succ_type == "Intermediate":
                # Skip intermediate, continue exploring
                to_visit.append(successor)
    
    return list(set(finished_products))

def calculate_tree_layout(tree, target_batch_id):
    """Calculate positions for a beautiful tree layout"""
    positions = {}
    
    if tree.number_of_nodes() == 0:
        return positions
    
    # Get node lists
    finished_products = [n for n in tree.nodes() if tree.nodes[n].get("type") == "Finished Product"]
    raw_materials = [n for n in tree.nodes() if tree.nodes[n].get("type") == "Raw Material"]
    
    # Center positions
    center_x, center_y = 500, 300
    
    # Position target at center top
    if target_batch_id and target_batch_id in tree.nodes():
        positions[target_batch_id] = {"x": center_x, "y": 100}
    
    # Position finished products
    fp_count = len(finished_products)
    fp_spacing = min(800 / max(1, fp_count), 200)
    start_x = center_x - (fp_count - 1) * fp_spacing / 2
    
    for i, fp in enumerate(finished_products):
        if fp == target_batch_id:
            continue
        positions[fp] = {"x": start_x + i * fp_spacing, "y": 100}
    
    # Position raw materials in a circular layout around target
    rm_count = len(raw_materials)
    radius = 300
    angle_step = 360 / max(1, rm_count)
    
    for i, rm in enumerate(raw_materials):
        angle = math.radians(i * angle_step)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        positions[rm] = {"x": x, "y": y}
    
    return positions

def get_pharma_tree_node_styling(node_data, node_id, target_batch_id):
    """Get professional pharmaceutical node styling with icons"""
    
    node_type = node_data.get("type", "Unknown")
    material = str(node_data.get("material", "")).upper()
    is_target = str(node_id) == str(target_batch_id)
    
    # Determine material category
    if "API" in material:
        category = "API"
        icon = "🧪"  # Test tube for API
        color = "#1e88e5"
        border = "#0d47a1"
        shape = "diamond"
    elif any(x in material for x in ["EXCIPIENT", "FILLER", "BINDER", "DILUENT"]):
        category = "Excipient"
        icon = "📦"  # Package for excipient
        color = "#43a047"
        border = "#1b5e20"
        shape = "triangle"
    elif any(x in material for x in ["SOLVENT", "WATER", "ETHANOL"]):
        category = "Solvent"
        icon = "💧"  # Droplet for solvent
        color = "#5e35b1"
        border = "#311b92"
        shape = "ellipse"
    elif node_type == "Finished Product":
        if "TABLET" in material or "TAB" in node_id:
            category = "Tablet"
            icon = "💊"  # Pill for tablet
            color = "#00c853"
            border = "#1b5e20"
            shape = "star"
        elif "CAPSULE" in material or "CAP" in node_id:
            category = "Capsule"
            icon = "💊"  # Pill for capsule
            color = "#ff4081"
            border = "#c51162"
            shape = "hexagon"
        else:
            category = "Product"
            icon = "🏭"  # Factory for other products
            color = "#00bfa5"
            border = "#00796b"
            shape = "star"
    else:
        category = "Unknown"
        icon = "📄"
        color = "#9e9e9e"
        border = "#616161"
        shape = "circle"
    
    # Size and styling based on importance
    if is_target:
        size = 60
        border_width = 4
        font_size = 16
        bold = True
        shadow = True
    elif node_type == "Finished Product":
        size = 50
        border_width = 3
        font_size = 14
        bold = True
        shadow = True
    else:  # Raw materials
        size = 40
        border_width = 2
        font_size = 12
        bold = False
        shadow = True
    
    # Create label with icon
    label = format_node_label(node_id, node_data.get("material", ""), icon)
    
    # Create tooltip
    tooltip = create_pharma_tooltip(node_data, node_id, icon)
    
    return {
        "label": label,
        "color": color,
        "border_color": border,
        "shape": shape,
        "size": size,
        "border_width": border_width,
        "font_size": font_size,
        "font_color": "#1e293b",
        "bold": bold,
        "shadow": shadow,
        "tooltip": tooltip
    }

def format_node_label(batch_id, material, icon):
    """Format node label with icon"""
    batch_str = str(batch_id)
    material_str = str(material)
    
    # Get batch number
    numbers = re.findall(r'\d+', batch_str)
    batch_num = numbers[0] if numbers else ""
    
    # Shorten material name
    if len(material_str) > 12:
        material_short = material_str[:12] + "..."
    else:
        material_short = material_str
    
    # Determine type prefix
    if batch_str.startswith("RM-"):
        prefix = "RM"
    elif batch_str.startswith("FP-"):
        prefix = "FP"
    else:
        prefix = batch_str.split('-')[0] if '-' in batch_str else ""
    
    return f"{icon}\n{prefix}{'-' + batch_num if batch_num else ''}\n{material_short}"

def create_pharma_tooltip(node_data, node_id, icon):
    """Create professional pharmaceutical tooltip"""
    
    html = f"""
    <div style="font-family: 'Segoe UI', system-ui, sans-serif; max-width: 300px; background: white; padding: 15px; border-radius: 10px; border-left: 4px solid {node_data.get('color', '#1e88e5')}; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
        <div style="display: flex; align-items: center; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 2px solid #e2e8f0;">
            <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
            <div>
                <div style="font-weight: 700; color: #1e3a8a; font-size: 14px;">{node_id}</div>
                <div style="color: #475569; font-size: 12px; margin-top: 2px;">{node_data.get('material', 'Unknown')}</div>
            </div>
        </div>
        
        <table style="width: 100%; font-size: 12px; border-collapse: collapse; color: #334155;">
    """
    
    # Add key information
    fields = [
        ("📋", "Type", node_data.get("type", "")),
        ("⚖️", "Quantity", f"{node_data.get('quantity', '')} {node_data.get('unit', '')}"),
        ("🏷️", "Status", node_data.get("status", "")),
        ("✅", "Quality", node_data.get("quality", "")),
        ("📅", "Manufactured", node_data.get("manufacturing_date", ""))
    ]
    
    for field_icon, label, value in fields:
        if value and str(value).strip() and str(value).lower() != "nan":
            html += f"""
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 6px 0; width: 40%; color: #64748b; font-weight: 500;">
                    {field_icon} {label}:
                </td>
                <td style="padding: 6px 0; text-align: right; color: #1e293b; font-weight: 600;">
                    {value}
                </td>
            </tr>
            """
    
    html += """
        </table>
        
        <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8;">
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span style="margin-right: 6px;">📋</span>
                <span>Pharmaceutical Batch Record</span>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="margin-right: 6px;">🔗</span>
                <span>GMP Compliant • Traceability</span>
            </div>
        </div>
    </div>
    """
    
    return html

def get_pharma_tree_edge_styling(u, v, edge_data, target_batch_id):
    """Get professional edge styling for tree"""
    
    is_target_related = (str(u) == str(target_batch_id) or str(v) == str(target_batch_id))
    
    if is_target_related:
        color = "#ff9800"  # Orange for target connections
        width = 3
        dashes = False
        length = 200
    else:
        color = "#81c784"  # Green for other connections
        width = 2
        dashes = [5, 5]
        length = 180
    
    # Add label if quantity exists
    label = ""
    if edge_data.get("quantity"):
        qty = edge_data.get("quantity", "")
        unit = edge_data.get("unit", "")
        if qty and unit:
            label = f"{qty} {unit}"
    
    return {
        "color": color,
        "width": width,
        "dashes": dashes,
        "length": length,
        "font": {
            "size": 10,
            "color": "#555",
            "align": "middle"
        },
        "label": label
    }

def generate_pharma_tree_legend(target_batch_id, tree):
    """Generate professional pharmaceutical tree legend"""
    
    if not target_batch_id or target_batch_id not in tree.nodes():
        return ""
    
    target_data = tree.nodes[target_batch_id]
    raw_materials = [n for n in tree.nodes() if tree.nodes[n].get("type") == "Raw Material"]
    
    return f"""
    <div style="
        position: absolute;
        top: 20px;
        left: 20px;
        padding: 20px;
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 13px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        z-index: 1000;
        max-width: 300px;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #3b82f6;">
            <span style="font-size: 28px; margin-right: 12px; color: #3b82f6;">🌳</span>
            <div>
                <div style="font-weight: 800; font-size: 16px; color: #1e293b; letter-spacing: 0.3px;">PHARMA BATCH TREE</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 3px;">Material Genealogy • GMP Traceability</div>
            </div>
        </div>
        
        <div style="margin-bottom: 20px;">
            <div style="font-weight: 700; color: #334155; font-size: 12px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                🎯 TARGET BATCH
            </div>
            <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); padding: 14px; border-radius: 8px; border-left: 4px solid #3b82f6;">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 20px; margin-right: 10px;">💊</span>
                    <div>
                        <div style="font-weight: 700; color: #1e40af; font-size: 13px;">{target_batch_id}</div>
                        <div style="font-size: 11px; color: #3b82f6; margin-top: 2px;">{target_data.get('material', '')}</div>
                    </div>
                </div>
                <div style="font-size: 11px; color: #475569; margin-top: 6px;">
                    {len(raw_materials)} raw materials • {tree.number_of_edges()} connections
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 20px;">
            <div style="font-weight: 700; color: #334155; font-size: 12px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                🏷️ NODE LEGEND
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div style="background: rgba(30, 136, 229, 0.08); padding: 10px; border-radius: 6px; border: 1px solid rgba(30, 136, 229, 0.2);">
                    <div style="display: flex; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 18px; margin-right: 8px;">🧪</span>
                        <span style="font-weight: 600; font-size: 11px; color: #1e88e5;">API Material</span>
                    </div>
                    <div style="font-size: 10px; color: #5d7fa3;">Active Ingredients</div>
                </div>
                
                <div style="background: rgba(67, 160, 71, 0.08); padding: 10px; border-radius: 6px; border: 1px solid rgba(67, 160, 71, 0.2);">
                    <div style="display: flex; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 18px; margin-right: 8px;">📦</span>
                        <span style="font-weight: 600; font-size: 11px; color: #43a047;">Excipients</span>
                    </div>
                    <div style="font-size: 10px; color: #5d7fa3;">Inactive Ingredients</div>
                </div>
                
                <div style="background: rgba(0, 200, 83, 0.08); padding: 10px; border-radius: 6px; border: 1px solid rgba(0, 200, 83, 0.2);">
                    <div style="display: flex; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 18px; margin-right: 8px;">💊</span>
                        <span style="font-weight: 600; font-size: 11px; color: #00c853;">Finished Product</span>
                    </div>
                    <div style="font-size: 10px; color: #5d7fa3;">Final Dosage Form</div>
                </div>
                
                <div style="background: rgba(255, 152, 0, 0.08); padding: 10px; border-radius: 6px; border: 1px solid rgba(255, 152, 0, 0.2);">
                    <div style="display: flex; align-items: center; margin-bottom: 6px;">
                        <div style="width: 20px; height: 3px; background: #ff9800; margin-right: 8px;"></div>
                        <span style="font-weight: 600; font-size: 11px; color: #ff9800;">Active Flow</span>
                    </div>
                    <div style="font-size: 10px; color: #5d7fa3;">Material Connection</div>
                </div>
            </div>
        </div>
        
        <div style="padding-top: 15px; border-top: 1px solid #e2e8f0;">
            <div style="font-size: 11px; color: #64748b; line-height: 1.6;">
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <span style="margin-right: 8px; color: #3b82f6; font-size: 14px;">👆</span>
                    <span><strong>Hover</strong> over nodes for batch details</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <span style="margin-right: 8px; color: #3b82f6; font-size: 14px;">🖱️</span>
                    <span><strong>Drag</strong> to reposition tree layout</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <span style="margin-right: 8px; color: #3b82f6; font-size: 14px;">🔍</span>
                    <span><strong>Scroll</strong> to zoom in/out</span>
                </div>
            </div>
            <div style="margin-top: 12px; font-size: 10px; color: #94a3b8; text-align: center; font-style: italic;">
                Pharmaceutical Material Flow Tree
            </div>
        </div>
    </div>
    """
