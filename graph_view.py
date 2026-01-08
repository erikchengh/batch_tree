from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx
import tempfile
import os
import json

def render_genealogy_graph(G, target_batch_id=None, trace_mode="none"):
    """
    Render a static batch genealogy graph with trace modes
    
    Args:
        G: NetworkX graph
        target_batch_id: Batch to focus on
        trace_mode: "none", "forward", "backward", "both"
    """
    
    # Create network
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#f8f9fa",
        font_color="#2d3436"
    )
    
    # DISABLE PHYSICS - Static graph
    net.toggle_physics(False)
    
    # Determine which nodes/edges to highlight based on trace mode
    highlight_nodes = set()
    highlight_edges = set()
    
    if target_batch_id and target_batch_id in G.nodes:
        highlight_nodes.add(target_batch_id)
        
        if trace_mode in ["forward", "both"]:
            # Find all descendants (forward trace)
            descendants = nx.descendants(G, target_batch_id)
            highlight_nodes.update(descendants)
            
            # Highlight edges in forward direction
            for desc in descendants:
                if nx.has_path(G, target_batch_id, desc):
                    path = nx.shortest_path(G, target_batch_id, desc)
                    for i in range(len(path) - 1):
                        highlight_edges.add((path[i], path[i + 1]))
        
        if trace_mode in ["backward", "both"]:
            # Find all ancestors (backward trace)
            ancestors = nx.ancestors(G, target_batch_id)
            highlight_nodes.update(ancestors)
            
            # Highlight edges in backward direction
            for anc in ancestors:
                if nx.has_path(G, anc, target_batch_id):
                    path = nx.shortest_path(G, anc, target_batch_id)
                    for i in range(len(path) - 1):
                        highlight_edges.add((path[i], path[i + 1]))
    
    # Calculate hierarchical positions
    positions = calculate_hierarchical_positions(G, target_batch_id)
    
    # === ADD NODES ===
    for node_id, node_data in G.nodes(data=True):
        # Determine styling
        is_highlighted = node_id in highlight_nodes
        is_target = node_id == target_batch_id
        
        # Colors based on node type
        color_map = {
            "Raw Material": "#3498db",
            "Intermediate": "#9b59b6", 
            "Finished Product": "#2ecc71"
        }
        
        # Shapes based on node type
        shape_map = {
            "Raw Material": "ellipse",
            "Intermediate": "box",
            "Finished Product": "star"
        }
        
        node_type = node_data.get("type", "Unknown")
        color = color_map.get(node_type, "#95a5a6")
        shape = shape_map.get(node_type, "circle")
        size = 25 if node_type == "Intermediate" else 30
        
        # Special styling for highlighted/target nodes
        if is_target:
            color = "#f39c12"  # Orange for target
            shape = "diamond"
            size = 40
            border_width = 4
            shadow = True
        elif is_highlighted:
            border_width = 3
            shadow = True
        else:
            border_width = 2
            shadow = False
        
        # Get position
        pos = positions.get(node_id, {"x": None, "y": None})
        
        # Add node
        net.add_node(
            node_id,
            label=node_data.get("label", node_id),
            color=color,
            shape=shape,
            size=size,
            title=generate_enhanced_tooltip(node_data),
            borderWidth=border_width,
            borderColor="#2c3e50",
            x=pos["x"],
            y=pos["y"],
            fixed=True,
            physics=False,
            shadow=shadow,
            font={
                "size": 14 if is_highlighted else 12,
                "face": "Arial",
                "color": "#2d3436" if is_highlighted else "#7f8c8d",
                "align": "center",
                "bold": is_highlighted
            }
        )
    
    # === ADD EDGES ===
    for u, v, edge_data in G.edges(data=True):
        is_highlighted = (u, v) in highlight_edges
        is_target_edge = (u == target_batch_id or v == target_batch_id)
        
        # Edge styling
        if is_highlighted:
            color = "#e74c3c"  # Red for highlighted trace
            width = 4
            opacity = 1.0
            dashes = False
        elif is_target_edge:
            color = "#f39c12"  # Orange for target-related
            width = 3
            opacity = 0.9
            dashes = [5, 5]
        else:
            color = "#bdc3c7"  # Gray for normal
            width = 2
            opacity = 0.6
            dashes = False
        
        # Add edge
        net.add_edge(
            u, v,
            label=edge_data.get("label", ""),
            color=color,
            width=width,
            arrows="to",
            opacity=opacity,
            dashes=dashes,
            smooth=False,
            font={
                "size": 11,
                "color": color,
                "align": "middle"
            }
        )
    
    # === CONFIGURATION ===
    config = {
        "physics": {"enabled": False},
        "interaction": {
            "dragNodes": False,
            "dragView": True,
            "zoomView": True,
            "hover": True,
            "tooltipDelay": 150,
            "multiselect": False,
            "navigationButtons": True
        },
        "edges": {
            "smooth": {"enabled": False},
            "arrows": {
                "to": {
                    "enabled": True,
                    "scaleFactor": 0.8,
                    "type": "arrow"
                }
            },
            "color": {"inherit": False}
        },
        "nodes": {
            "borderWidth": 2,
            "font": {"align": "center"},
            "shadow": {"enabled": True}
        },
        "layout": {"hierarchical": {"enabled": False}}
    }
    
    net.set_options(json.dumps(config))
    
    # === SAVE AND RENDER ===
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
        net.save_graph(tmp.name)
        tmp_path = tmp.name
    
    with open(tmp_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Add enhanced legend with trace info
    legend_html = generate_enhanced_legend_html(target_batch_id, trace_mode, highlight_nodes)
    html_content = html_content.replace('</body>', f'{legend_html}</body>')
    
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    with open(tmp_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=800, scrolling=False)
    
    os.unlink(tmp_path)

def calculate_hierarchical_positions(G, target_batch_id=None):
    """Calculate positions for hierarchical layout"""
    positions = {}
    
    # Group nodes by type and connectivity
    raw_materials = []
    intermediates = []
    finished_products = []
    
    for node in G.nodes():
        node_type = G.nodes[node].get("type", "Unknown")
        
        if node_type == "Raw Material":
            raw_materials.append(node)
        elif node_type == "Intermediate":
            intermediates.append(node)
        elif node_type == "Finished Product":
            finished_products.append(node)
        else:
            intermediates.append(node)  # Default
    
    # Position in columns
    column_x = {"raw": 100, "intermediate": 450, "finished": 800}
    
    # Position raw materials (left)
    y = 100
    for node in raw_materials[:8]:  # Limit to 8 per column
        positions[node] = {"x": column_x["raw"], "y": y}
        y += 120
    
    # Position intermediates (middle)
    y = 100
    for node in intermediates[:8]:
        positions[node] = {"x": column_x["intermediate"], "y": y}
        y += 120
    
    # Position finished products (right)
    y = 100
    for node in finished_products[:8]:
        positions[node] = {"x": column_x["finished"], "y": y}
        y += 120
    
    # Position target node prominently if provided
    if target_batch_id and target_batch_id in positions:
        positions[target_batch_id]["y"] = 400  # Center vertically
    
    return positions

def generate_enhanced_tooltip(node_data):
    """Generate detailed HTML tooltip"""
    tooltip = f"""
    <div style="padding: 12px; font-family: 'Segoe UI', Arial, sans-serif; max-width: 320px; background: white; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); border-left: 4px solid {node_data.get('color', '#3498db')};">
        <div style="font-weight: 700; font-size: 15px; margin-bottom: 10px; color: #2c3e50;">
            {node_data.get('label', 'Unknown').split('\\n')[0]}
        </div>
        
        <div style="display: grid; grid-template-columns: 100px auto; gap: 6px; font-size: 12.5px;">
    """
    
    fields = [
        ("Type", node_data.get("type"), ""),
        ("Material", node_data.get("material"), ""),
        ("Product", node_data.get("product"), ""),
        ("Quantity", node_data.get("quantity"), ""),
        ("Status", node_data.get("status"), "#2ecc71" if node_data.get("status") == "Released" else "#f39c12"),
        ("Quality", node_data.get("quality"), "#2ecc71" if node_data.get("quality") == "Approved" else "#e74c3c"),
        ("Batch ID", node_data.get("batch_id", list(node_data.keys())[0] if node_data else ""), "")
    ]
    
    for label, value, color in fields:
        if value:
            color_style = f"color: {color};" if color else "color: #2c3e50; font-weight: 500;"
            tooltip += f"""
            <div style="color: #7f8c8d; font-weight: 500;">{label}:</div>
            <div style="{color_style}">{value}</div>
            """
    
    tooltip += """
        </div>
    </div>
    """
    return tooltip

def generate_enhanced_legend_html(target_batch_id, trace_mode, highlight_nodes):
    """Generate legend with trace information"""
    
    trace_info = {
        "none": "No trace active",
        "forward": "Showing downstream products",
        "backward": "Showing upstream materials", 
        "both": "Showing full genealogy"
    }
    
    highlight_count = len(highlight_nodes) if highlight_nodes else 0
    
    return f"""
    <div style="
        position: absolute;
        top: 20px;
        right: 20px;
        padding: 18px;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,249,250,0.98) 100%);
        border-radius: 12px;
        border: 1px solid #dfe6e9;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        z-index: 1000;
        max-width: 280px;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 15px; padding-bottom: 12px; border-bottom: 2px solid #3498db;">
            <div style="font-size: 18px; margin-right: 10px;">🏭</div>
            <div>
                <div style="font-weight: 700; font-size: 16px; color: #2c3e50;">Batch Genealogy</div>
                <div style="font-size: 11px; color: #7f8c8d; margin-top: 2px;">Trace Visualization</div>
            </div>
        </div>
        
        {f'<div style="background: #fff3cd; padding: 10px; border-radius: 6px; margin-bottom: 15px; border-left: 4px solid #ffc107;"><div style="font-weight: 600; color: #856404;">Target Batch: <code>{target_batch_id}</code></div><div style="font-size: 12px; color: #856404; margin-top: 4px;">{trace_info.get(trace_mode, "")} • {highlight_count} nodes highlighted</div></div>' if target_batch_id else ''}
        
        <div style="margin-bottom: 15px;">
            <div style="font-weight: 600; color: #495057; font-size: 12.5px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Node Types</div>
            <div style="display: flex; align-items: center; margin-bottom: 8px; padding: 8px 10px; background: rgba(52, 152, 219, 0.08); border-radius: 6px;">
                <div style="width: 14px; height: 14px; background: #3498db; border-radius: 50%; margin-right: 10px; border: 2px solid #2980b9;"></div>
                <span style="font-weight: 500;">Raw Material</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 8px; padding: 8px 10px; background: rgba(155, 89, 182, 0.08); border-radius: 6px;">
                <div style="width: 14px; height: 14px; background: #9b59b6; border-radius: 3px; margin-right: 10px; border: 2px solid #8e44ad;"></div>
                <span style="font-weight: 500;">Intermediate</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 8px; padding: 8px 10px; background: rgba(46, 204, 113, 0.08); border-radius: 6px;">
                <div style="width: 14px; height: 14px; background: #2ecc71; border-radius: 0 50% 50% 50%; transform: rotate(45deg); margin-right: 10px; border: 2px solid #27ae60;"></div>
                <span style="font-weight: 500;">Finished Product</span>
            </div>
            <div style="display: flex; align-items: center; padding: 8px 10px; background: rgba(243, 156, 18, 0.08); border-radius: 6px;">
                <div style="width: 14px; height: 14px; background: #f39c12; border-radius: 0; transform: rotate(45deg); margin-right: 10px; border: 2px solid #d68910;"></div>
                <span style="font-weight: 500;">Target Batch</span>
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <div style="font-weight: 600; color: #495057; font-size: 12.5px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Trace Colors</div>
            <div style="display: flex; align-items: center; margin-bottom: 6px;">
                <div style="width: 24px; height: 3px; background: #e74c3c; margin-right: 10px; position: relative;">
                    <div style="position: absolute; right: -6px; top: -4px; width: 0; height: 0; border-top: 5px solid transparent; border-bottom: 5px solid transparent; border-left: 8px solid #e74c3c;"></div>
                </div>
                <span style="font-size: 12.5px;"><b>Highlighted Trace</b> (Active path)</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 6px;">
                <div style="width: 24px; height: 2px; background: #f39c12; margin-right: 10px; position: relative;">
                    <div style="position: absolute; right: -6px; top: -4px; width: 0; height: 0; border-top: 5px solid transparent; border-bottom: 5px solid transparent; border-left: 8px solid #f39c12;"></div>
                </div>
                <span style="font-size: 12.5px;">Related to Target</span>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="width: 24px; height: 1px; background: #bdc3c7; margin-right: 10px; position: relative;">
                    <div style="position: absolute; right: -6px; top: -4px; width: 0; height: 0; border-top: 5px solid transparent; border-bottom: 5px solid transparent; border-left: 8px solid #bdc3c7;"></div>
                </div>
                <span style="font-size: 12.5px;">Normal Connection</span>
            </div>
        </div>
        
        <div style="margin-top: 15px; padding-top: 12px; border-top: 1px solid #e9ecef;">
            <div style="font-size: 12px; color: #6c757d; line-height: 1.5;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 5px;">
                    <span style="margin-right: 8px; color: #3498db;">•</span>
                    <span><b>Hover</b> over nodes for full details</span>
                </div>
                <div style="display: flex; align-items: flex-start; margin-bottom: 5px;">
                    <span style="margin-right: 8px; color: #3498db;">•</span>
                    <span><b>Scroll</b> to zoom • <b>Drag</b> to pan</span>
                </div>
                <div style="display: flex; align-items: flex-start;">
                    <span style="margin-right: 8px; color: #3498db;">•</span>
                    <span><b>Static layout</b> • No distracting movement</span>
                </div>
            </div>
        </div>
    </div>
    """
