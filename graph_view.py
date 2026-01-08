from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx
import tempfile
import os

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
        font_color="#2d3436",
        cdn_resources='remote'  # Load from CDN for better performance
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
    
    # === CALCULATE FIXED POSITIONS ===
    # This creates a clean, organized layout without movement
    positions = {}
    
    # Separate nodes by type for organized columns
    raw_materials = [n for n in G.nodes() if G.nodes[n].get("type") == "Raw Material"]
    intermediates = [n for n in G.nodes() if G.nodes[n].get("type") == "Intermediate"]
    finished_products = [n for n in G.nodes() if G.nodes[n].get("type") == "Finished Product"]
    
    # Position nodes in three columns
    column_x_positions = {
        "Raw Material": 100,
        "Intermediate": 500,
        "Finished Product": 900
    }
    
    # Position raw materials (left column)
    y_pos = 100
    for node in raw_materials:
        positions[node] = {"x": column_x_positions["Raw Material"], "y": y_pos}
        y_pos += 180
    
    # Position intermediates (middle column)
    y_pos = 100
    for node in intermediates:
        positions[node] = {"x": column_x_positions["Intermediate"], "y": y_pos}
        y_pos += 180
    
    # Position finished products (right column)
    y_pos = 100
    for node in finished_products:
        positions[node] = {"x": column_x_positions["Finished Product"], "y": y_pos}
        y_pos += 180
    
    # === ADD NODES WITH FIXED POSITIONS ===
    for node_id, node_data in G.nodes(data=True):
        # Determine styling
        opacity = 1.0
        border_width = 2
        shadow_enabled = True
        
        # Highlight target and related nodes
        if highlight_nodes:
            if node_id in highlight_nodes:
                border_width = 4
                shadow_enabled = True
            else:
                opacity = 0.4  # Dim non-highlighted nodes
                shadow_enabled = False
        
        # Get pre-calculated position
        pos = positions.get(node_id, {"x": None, "y": None})
        
        # Add node with FIXED position
        net.add_node(
            node_id,
            label=node_data["label"],
            color=node_data["color"],
            shape=node_data["shape"],
            size=node_data["size"],
            title=generate_node_tooltip(node_data),
            opacity=opacity,
            borderWidth=border_width,
            borderWidthSelected=border_width,
            borderColor="#2c3e50",
            x=pos["x"],  # FIXED X POSITION
            y=pos["y"],  # FIXED Y POSITION
            fixed=True,  # CRITICAL: Node cannot move
            physics=False,  # NO physics
            font={
                "size": node_data["size"] / 1.8,
                "face": "Arial",
                "color": "#2d3436",
                "strokeWidth": 1,
                "strokeColor": "#ffffff",
                "align": "center"
            },
            shadow={
                "enabled": shadow_enabled,
                "color": "rgba(0,0,0,0.15)",
                "size": 5,
                "x": 2,
                "y": 2
            }
        )
    
    # === ADD EDGES (STRAIGHT LINES) ===
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
            smooth=False,  # STRAIGHT LINES - no curves
            physics=False,  # NO edge physics
            font={
                "size": 11,
                "align": "middle",
                "color": "#7f8c8d",
                "strokeWidth": 0
            },
            selectionWidth=0,  # No highlight on selection
            hoverWidth=0  # No change on hover
        )
    
    # === STATIC CONFIGURATION (NO MOVEMENT) ===
    static_config = """
    var options = {
      "physics": {
        "enabled": false,  // COMPLETELY DISABLED - NO MOVEMENT
        "solver": null,
        "stabilization": {
          "enabled": false  // NO STABILIZATION NEEDED
        }
      },
      "interaction": {
        "dragNodes": false,  // DISABLE DRAGGING - COMPLETELY STATIC
        "dragView": true,    // But allow panning the view
        "zoomView": true,    // Allow zooming
        "hover": true,       // Show tooltips on hover
        "tooltipDelay": 100,
        "multiselect": false,
        "navigationButtons": true,  // Show navigation buttons
        "keyboard": {
          "enabled": false  // Disable keyboard navigation
        }
      },
      "edges": {
        "smooth": false,  // Straight edges only
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 0.8,
            "type": "arrow"
          }
        },
        "color": {
          "inherit": false
        },
        "shadow": false,
        "hoverWidth": 0
      },
      "nodes": {
        "borderWidth": 2,
        "borderWidthSelected": 2,
        "chosen": false,
        "font": {
          "align": "center"
        },
        "shadow": false,
        "size": 30
      },
      "layout": {
        "improvedLayout": false,  // Use our manual layout
        "randomSeed": undefined,
        "hierarchical": {
          "enabled": false
        }
      },
      "configure": {
        "enabled": false  // Hide configuration UI
      }
    }
    """
    
    net.set_options(static_config)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
        net.save_graph(tmp.name)
        tmp_path = tmp.name
    
    # Read and inject custom CSS/legend
    with open(tmp_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Add custom CSS to prevent any movement
    static_css = """
    <style>
    #mynetwork {
        cursor: grab !important;
    }
    #mynetwork:active {
        cursor: grabbing !important;
    }
    .vis-network {
        user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
    }
    .vis-node {
        cursor: default !important;
    }
    .vis-active {
        box-shadow: none !important;
    }
    </style>
    """
    
    # Add legend
    legend_html = generate_static_legend_html()
    
    # Combine everything
    html_content = html_content.replace('<head>', f'<head>{static_css}')
    html_content = html_content.replace('</body>', f'{legend_html}\n</body>')
    
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
    tooltip = f"""
    <div style="padding: 12px; font-family: Arial, sans-serif; max-width: 320px; background: white; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border: 1px solid #dfe6e9;">
        <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px; color: {node_data['color']}; border-bottom: 2px solid {node_data['color']}; padding-bottom: 4px;">
            {node_data['label'].split('\\n')[0]}
        </div>
        <div style="font-size: 12px; margin-bottom: 6px; display: flex;">
            <span style="min-width: 80px; color: #7f8c8d;">Material:</span>
            <span style="font-weight: 500;">{node_data['material']}</span>
        </div>
        <div style="font-size: 12px; margin-bottom: 6px; display: flex;">
            <span style="min-width: 80px; color: #7f8c8d;">Type:</span>
            <span style="font-weight: 500; color: {node_data['color']};">{node_data['type']}</span>
        </div>
        <div style="font-size: 12px; margin-bottom: 6px; display: flex;">
            <span style="min-width: 80px; color: #7f8c8d;">Quantity:</span>
            <span style="font-weight: 500;">{node_data['quantity']}</span>
        </div>
    """
    
    if node_data.get('product'):
        tooltip += f"""
        <div style="font-size: 12px; margin-bottom: 6px; display: flex;">
            <span style="min-width: 80px; color: #7f8c8d;">Product:</span>
            <span style="font-weight: 500;">{node_data['product']}</span>
        </div>
        """
    
    if node_data.get('status'):
        status_color = "#2ecc71" if node_data['status'] == "Released" else "#f39c12"
        tooltip += f"""
        <div style="font-size: 12px; margin-bottom: 6px; display: flex;">
            <span style="min-width: 80px; color: #7f8c8d;">Status:</span>
            <span style="font-weight: 500; color: {status_color};">{node_data['status']}</span>
        </div>
        """
    
    if node_data.get('quality'):
        quality_color = "#2ecc71" if node_data['quality'] == "Approved" else "#e74c3c"
        tooltip += f"""
        <div style="font-size: 12px; margin-bottom: 6px; display: flex;">
            <span style="min-width: 80px; color: #7f8c8d;">Quality:</span>
            <span style="font-weight: 500; color: {quality_color};">{node_data['quality']}</span>
        </div>
        """
    
    tooltip += "</div>"
    return tooltip

def generate_static_legend_html():
    """Generate HTML legend for the static graph"""
    return """
    <div style="
        position: absolute;
        top: 20px;
        right: 20px;
        padding: 16px;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        background-color: rgba(255, 255, 255, 0.98);
        border-radius: 10px;
        border: 1px solid #bdc3c7;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
        z-index: 1000;
        max-width: 240px;
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 2px solid #3498db;">
            <div style="font-size: 16px; margin-right: 8px;">📊</div>
            <div style="font-weight: 700; font-size: 15px; color: #2c3e50;">Batch Genealogy</div>
        </div>
        
        <div style="margin-bottom: 12px;">
            <div style="font-weight: 600; color: #34495e; font-size: 12px; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">NODE TYPES</div>
            <div style="display: flex; align-items: center; margin-bottom: 8px; padding: 6px 8px; background: #f8f9fa; border-radius: 5px;">
                <div style="width: 14px; height: 14px; background-color: #3498db; border-radius: 50%; margin-right: 10px; border: 2px solid #2980b9;"></div>
                <span style="font-weight: 500;">Raw Material</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 8px; padding: 6px 8px; background: #f8f9fa; border-radius: 5px;">
                <div style="width: 14px; height: 14px; background-color: #9b59b6; border-radius: 3px; margin-right: 10px; border: 2px solid #8e44ad;"></div>
                <span style="font-weight: 500;">Intermediate</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 8px; padding: 6px 8px; background: #f8f9fa; border-radius: 5px;">
                <div style="width: 14px; height: 14px; background-color: #2ecc71; border-radius: 0 50% 50% 50%; transform: rotate(45deg); margin-right: 10px; border: 2px solid #27ae60;"></div>
                <span style="font-weight: 500;">Finished Product</span>
            </div>
        </div>
        
        <div style="margin-bottom: 12px;">
            <div style="font-weight: 600; color: #34495e; font-size: 12px; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">FLOW DIRECTION</div>
            <div style="display: flex; align-items: center; margin-bottom: 6px;">
                <div style="width: 24px; height: 2px; background-color: #e74c3c; margin-right: 10px; position: relative;">
                    <div style="position: absolute; right: -6px; top: -4px; width: 0; height: 0; border-top: 5px solid transparent; border-bottom: 5px solid transparent; border-left: 8px solid #e74c3c;"></div>
                </div>
                <span style="font-size: 12px;">Material Consumption</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 6px;">
                <div style="width: 24px; height: 2px; background-color: #3498db; margin-right: 10px; position: relative;">
                    <div style="position: absolute; right: -6px; top: -4px; width: 0; height: 0; border-top: 5px solid transparent; border-bottom: 5px solid transparent; border-left: 8px solid #3498db;"></div>
                </div>
                <span style="font-size: 12px;">Process Sequence</span>
            </div>
        </div>
        
        <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid #dfe6e9;">
            <div style="font-size: 11px; color: #7f8c8d; line-height: 1.5;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 4px;">
                    <span style="margin-right: 6px;">•</span>
                    <span><b>Hover</b> over nodes for details</span>
                </div>
                <div style="display: flex; align-items: flex-start; margin-bottom: 4px;">
                    <span style="margin-right: 6px;">•</span>
                    <span><b>Scroll</b> to zoom in/out</span>
                </div>
                <div style="display: flex; align-items: flex-start;">
                    <span style="margin-right: 6px;">•</span>
                    <span><b>Drag</b> background to pan view</span>
                </div>
            </div>
            <div style="margin-top: 10px; font-size: 11px; color: #95a5a6; font-style: italic; text-align: center;">
                Static layout • No movement
            </div>
        </div>
    </div>
    """
