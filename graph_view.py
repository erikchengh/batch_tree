from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx
import tempfile
import os
import json

def render_genealogy_graph(G, target_batch_id=None, highlight_upstream=True, highlight_downstream=True):
    """
    Render a COMPLETELY STATIC batch genealogy graph
    No movement, no physics, clean and stable
    """
    
    # Create network with static settings
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#2d3436"
    )
    
    # DISABLE ALL PHYSICS - COMPLETELY STATIC
    net.toggle_physics(False)
    
    # Determine which nodes to highlight
    highlight_nodes = set()
    if target_batch_id and target_batch_id in G.nodes:
        highlight_nodes.add(target_batch_id)
        
        if highlight_upstream:
            # Find all ancestors (raw materials feeding into target)
            highlight_nodes.update(nx.ancestors(G, target_batch_id))
        
        if highlight_downstream:
            # Find all descendants (products using target)
            highlight_nodes.update(nx.descendants(G, target_batch_id))
    
    # Calculate fixed positions for clean layout
    positions = {}
    
    # Separate nodes by type
    raw_materials = [n for n in G.nodes() if G.nodes[n].get("type") == "Raw Material"]
    intermediates = [n for n in G.nodes() if G.nodes[n].get("type") == "Intermediate"]
    finished_products = [n for n in G.nodes() if G.nodes[n].get("type") == "Finished Product"]
    
    # Position in columns (raw -> intermediate -> finished)
    column_positions = {
        "Raw Material": 100,
        "Intermediate": 500,
        "Finished Product": 900
    }
    
    # Position raw materials (left column)
    y_pos = 100
    for node in raw_materials:
        positions[node] = {"x": column_positions["Raw Material"], "y": y_pos}
        y_pos += 180
    
    # Position intermediates (middle column)
    y_pos = 100
    for node in intermediates:
        positions[node] = {"x": column_positions["Intermediate"], "y": y_pos}
        y_pos += 180
    
    # Position finished products (right column)
    y_pos = 100
    for node in finished_products:
        positions[node] = {"x": column_positions["Finished Product"], "y": y_pos}
        y_pos += 180
    
    # Add nodes with fixed positions
    for node_id, node_data in G.nodes(data=True):
        # Determine styling
        opacity = 1.0
        border_width = 2
        font_size = 14
        
        # Highlight target and related nodes
        if highlight_nodes:
            if node_id in highlight_nodes:
                border_width = 4
                font_size = 16
            else:
                opacity = 0.4
        
        # Get pre-calculated position
        pos = positions.get(node_id, {"x": None, "y": None})
        
        # Add node with FIXED position
        net.add_node(
            node_id,
            label=node_data.get("label", node_id),
            color=node_data.get("color", "#3498db"),
            shape=node_data.get("shape", "ellipse"),
            size=node_data.get("size", 25),
            title=generate_node_tooltip(node_data),
            opacity=opacity,
            borderWidth=border_width,
            x=pos["x"],  # FIXED X POSITION
            y=pos["y"],  # FIXED Y POSITION
            fixed=True,  # CRITICAL: Node cannot move
            physics=False,  # NO physics
            font={
                "size": font_size,
                "face": "Arial",
                "color": "#2d3436",
                "align": "center"
            }
        )
    
    # Add edges (straight lines only)
    for u, v, edge_data in G.edges(data=True):
        edge_opacity = 0.7
        edge_width = 2
        
        # Highlight edges connected to target
        if highlight_nodes and (u in highlight_nodes or v in highlight_nodes):
            edge_opacity = 1.0
            edge_width = 4
        
        net.add_edge(
            u, v,
            label=edge_data.get("label", ""),
            color=edge_data.get("color", "#95a5a6"),
            width=edge_width,
            arrows="to",
            opacity=edge_opacity,
            smooth=False  # STRAIGHT LINES - no curves
        )
    
    # === STATIC CONFIGURATION - VALID JSON ===
    static_config = {
        "physics": {
            "enabled": False  # COMPLETELY DISABLED - NO MOVEMENT
        },
        "interaction": {
            "dragNodes": False,  # DISABLE DRAGGING - COMPLETELY STATIC
            "dragView": True,    # Allow panning the view
            "zoomView": True,    # Allow zooming
            "hover": True,       # Show tooltips on hover
            "tooltipDelay": 200,
            "multiselect": False
        },
        "edges": {
            "smooth": {"enabled": False},  # Straight edges only
            "arrows": {
                "to": {
                    "enabled": True,
                    "scaleFactor": 0.8
                }
            }
        },
        "nodes": {
            "borderWidth": 2,
            "font": {
                "align": "center"
            }
        },
        "layout": {
            "hierarchical": {
                "enabled": False
            }
        }
    }
    
    # Set options with valid JSON
    net.set_options(json.dumps(static_config))
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
        net.save_graph(tmp.name)
        tmp_path = tmp.name
    
    # Read and inject legend
    with open(tmp_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Add legend
    legend_html = generate_legend_html()
    html_content = html_content.replace('</body>', f'{legend_html}</body>')
    
    # Write back
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Render in Streamlit
    with open(tmp_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=800, scrolling=False)
    
    # Clean up
    os.unlink(tmp_path)

def generate_node_tooltip(node_data):
    """Generate HTML tooltip for node"""
    tooltip_lines = []
    
    # Title
    label = node_data.get("label", "Unknown").split('\n')[0]
    tooltip_lines.append(f"<b>{label}</b>")
    
    # Material
    if "material" in node_data:
        tooltip_lines.append(f"Material: {node_data['material']}")
    
    # Type
    if "type" in node_data:
        tooltip_lines.append(f"Type: {node_data['type']}")
    
    # Quantity
    if "quantity" in node_data:
        tooltip_lines.append(f"Quantity: {node_data['quantity']}")
    
    # Product
    if "product" in node_data:
        tooltip_lines.append(f"Product: {node_data['product']}")
    
    # Status
    if "status" in node_data:
        tooltip_lines.append(f"Status: {node_data['status']}")
    
    # Quality
    if "quality" in node_data:
        tooltip_lines.append(f"Quality: {node_data['quality']}")
    
    # Format as HTML
    return '<div style="padding: 10px; font-family: Arial;">' + '<br>'.join(tooltip_lines) + '</div>'

def generate_legend_html():
    """Generate HTML legend for the graph"""
    return '''
    <div style="
        position: absolute;
        top: 20px;
        right: 20px;
        padding: 15px;
        font-family: Arial, sans-serif;
        font-size: 13px;
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 8px;
        border: 1px solid #ddd;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        max-width: 220px;
    ">
        <div style="font-weight: bold; margin-bottom: 10px; color: #2c3e50;">📊 Legend</div>
        
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <div style="width: 12px; height: 12px; background-color: #3498db; border-radius: 50%; margin-right: 8px;"></div>
            <span>Raw Material</span>
        </div>
        
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <div style="width: 12px; height: 12px; background-color: #9b59b6; border-radius: 3px; margin-right: 8px;"></div>
            <span>Intermediate Batch</span>
        </div>
        
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <div style="width: 12px; height: 12px; background-color: #2ecc71; border-radius: 0 50% 50% 50%; transform: rotate(45deg); margin-right: 8px;"></div>
            <span>Finished Product</span>
        </div>
        
        <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #eee;">
            <div style="font-size: 11px; color: #7f8c8d;">
                • Hover over nodes for details<br>
                • Scroll to zoom in/out<br>
                • Drag background to pan<br>
                <i>Static layout - No movement</i>
            </div>
        </div>
    </div>
    '''
