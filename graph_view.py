from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx
import json

def render_genealogy_graph(G, selected_batch=None, show_quantities=True, 
                          highlight_paths=True, legend_position="top-right"):
    """Render batch genealogy graph showing material flow"""
    
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#2d3436",
        notebook=False
    )
    
    # Configure layout for hierarchical flow
    net.toggle_physics(True)
    net.hrepulsion(
        node_distance=150,
        central_gravity=0.3,
        spring_length=200,
        spring_strength=0.05,
        damping=0.09
    )
    
    # === NODE STYLING based on type and level ===
    for node_id, data in G.nodes(data=True):
        # Determine node type and styling
        node_type = data.get("type", "unknown")
        level = data.get("level", 0)
        
        # Base styling
        shape, color, size, border_color = "ellipse", "#95a5a6", 25, "#7f8c8d"
        
        # Color by node type
        if node_type == "batch":
            if data.get("product", "").startswith("Tablet"):
                color, border_color = "#3498db", "#2980b9"  # Blue for tablet batches
            elif "API" in data.get("product", ""):
                color, border_color = "#e74c3c", "#c0392b"  # Red for API
            elif "Excipient" in data.get("product", ""):
                color, border_color = "#2ecc71", "#27ae60"  # Green for excipients
            else:
                color, border_color = "#9b59b6", "#8e44ad"  # Purple for other batches
            shape = "box"
            
        elif node_type == "material":
            material_type = data.get("material_type", "raw")
            if material_type == "raw":
                color, border_color = "#f39c12", "#d68910"  # Orange for raw materials
            elif material_type == "intermediate":
                color, border_color = "#1abc9c", "#16a085"  # Teal for intermediates
            elif material_type == "packaging":
                color, border_color = "#34495e", "#2c3e50"  # Dark gray for packaging
            shape = "circle"
            
        elif node_type == "product":
            color, border_color = "#9b59b6", "#8e44ad"  # Purple for final products
            shape = "diamond"
            size = 30
        
        # Size by level (center batch is largest)
        if level == 0:  # Target batch
            size = 40
            shape = "star"
            border_color = "#f1c40f"
            border_width = 3
        elif abs(level) == 1:
            size = 30
            border_width = 2
        else:
            size = 25
            border_width = 1
        
        # Highlight selected batch
        if node_id == selected_batch:
            color = "#f1c40f"
            border_color = "#f39c12"
            border_width = 4
            size = 45
            shape = "star"
        
        # Build label with quantity
        label = data.get("label", node_id)
        if show_quantities and data.get("quantity"):
            label = f"{label}\n{data['quantity']}"
        
        # Build tooltip
        tooltip = [f"<b>{data.get('label', node_id)}</b>"]
        if data.get("type"):
            tooltip.append(f"Type: {data['type']}")
        if data.get("status"):
            tooltip.append(f"Status: {data['status']}")
        if data.get("quantity"):
            tooltip.append(f"Quantity: {data['quantity']}")
        if data.get("date"):
            tooltip.append(f"Date: {data['date']}")
        if data.get("lot"):
            tooltip.append(f"Lot: {data['lot']}")
        if data.get("specification"):
            tooltip.append(f"Spec: {data['specification']}")
        if data.get("supplier"):
            tooltip.append(f"Supplier: {data['supplier']}")
        
        # Add node
        net.add_node(
            node_id,
            label=label,
            shape=shape,
            color=color,
            size=size,
            title="<br>".join(tooltip),
            borderWidth=border_width,
            borderColor=border_color,
            font={
                "size": 14 + max(0, 2 - abs(level)),  # Larger font for closer nodes
                "face": "Arial",
                "color": "#2d3436"
            }
        )
    
    # === EDGE STYLING ===
    for u, v, data in G.edges(data=True):
        edge_color, width, dashes = "#bdc3c7", 2, False
        
        rel = data.get("relationship", "")
        if rel == "consumed_by":
            edge_color = "#e74c3c"  # Red for consumption
            width = 3
            dashes = [5, 5]
        elif rel == "produces":
            edge_color = "#2ecc71"  # Green for production
            width = 3
        
        # Add quantity label to edge if available
        edge_label = ""
        if show_quantities and data.get("quantity"):
            edge_label = data["quantity"]
        elif rel:
            edge_label = rel.replace("_", " ")
        
        net.add_edge(
            u, v,
            label=edge_label,
            color=edge_color,
            width=width,
            dashes=dashes,
            arrows="to",
            font={
                "size": 11,
                "align": "middle",
                "color": edge_color
            },
            smooth={
                "type": "cubicBezier",
                "roundness": 0.3
            }
        )
    
    # === LAYOUT CONFIGURATION ===
    net.set_options("""
    var options = {
      "layout": {
        "hierarchical": {
          "enabled": true,
          "levelSeparation": 200,
          "nodeSpacing": 150,
          "treeSpacing": 250,
          "direction": "LR",  // Left to Right flow
          "sortMethod": "directed"
        }
      },
      "physics": {
        "enabled": true,
        "hierarchicalRepulsion": {
          "centralGravity": 0.0,
          "springLength": 200,
          "springConstant": 0.01,
          "nodeDistance": 150,
          "damping": 0.09
        },
        "solver": "hierarchicalRepulsion"
      },
      "interaction": {
        "dragNodes": true,
        "hover": true,
        "tooltipDelay": 100
      }
    }
    """)
    
    # === LEGEND ===
    legend_html = """
    <div style="
        position: absolute;
        top: 10px;
        right: 10px;
        background: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ddd;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: Arial, sans-serif;
        font-size: 12px;
        z-index: 1000;
        max-width: 200px;
    ">
        <div style="font-weight: bold; margin-bottom: 10px; color: #2c3e50;">📦 Batch Genealogy Legend</div>
        
        <div style="margin-bottom: 8px;">
            <div style="display: inline-block; width: 12px; height: 12px; background: #3498db; border: 2px solid #2980b9; margin-right: 8px; border-radius: 
