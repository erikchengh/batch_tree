from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx
import tempfile
import os
import json
import re
import streamlit as st

def render_genealogy_graph(G, target_batch_id=None, trace_mode="none"):
    """
    Render a professional pharmaceutical batch genealogy graph
    
    Args:
        G: NetworkX graph
        target_batch_id: Batch to focus on
        trace_mode: "none", "forward", "backward", "both"
    """
    
    # Check if graph is empty
    if G.number_of_nodes() == 0:
        st.warning("⚠️ No graph data available. Please check your data source.")
        return
    
    st.info(f"📊 Rendering graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Create network with pharma professional theme
    net = Network(
        height="800px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#1a3c6e"
    )
    
    # DISABLE PHYSICS - Static professional layout
    net.toggle_physics(False)
    
    # Determine trace highlighting
    highlight_nodes, highlight_edges = calculate_trace_highlights(G, target_batch_id, trace_mode)
    
    # Calculate professional hierarchical positions
    positions = calculate_pharma_positions(G, target_batch_id)
    
    # Debug: Show node count
    if len(positions) == 0:
        # Fallback to automatic layout if no positions calculated
        st.warning("⚠️ Using automatic layout. No specific positions calculated.")
    
    # === ADD PHARMA-STYLED NODES ===
    nodes_added = 0
    for node_id, node_data in G.nodes(data=True):
        # Ensure node_data is a dictionary
        if not isinstance(node_data, dict):
            node_data = {}
        
        # Get pharma-specific styling
        styling = get_pharma_node_styling(node_data, node_id, target_batch_id, node_id in highlight_nodes)
        
        # Get position
        pos = positions.get(node_id, {"x": None, "y": None})
        
        # Use automatic positioning if not set
        if pos["x"] is None or pos["y"] is None:
            # Spread nodes automatically
            idx = list(G.nodes()).index(node_id)
            pos["x"] = 100 + (idx % 10) * 150
            pos["y"] = 100 + (idx // 10) * 150
        
        # Add node with pharma styling
        net.add_node(
            str(node_id),  # Ensure node_id is string
            label=styling["label"],
            color=styling["color"],
            shape=styling["shape"],
            size=styling["size"],
            title=generate_pharma_tooltip(node_data, node_id),
            borderWidth=styling["border_width"],
            borderColor=styling["border_color"],
            x=pos["x"],
            y=pos["y"],
            fixed=True,
            physics=False,
            shadow=styling["shadow"],
            font={
                "size": styling["font_size"],
                "face": "Arial, sans-serif",
                "color": styling["font_color"],
                "align": "center",
                "bold": styling["bold"]
            }
        )
        nodes_added += 1
    
    # === ADD PHARMA-STYLED EDGES ===
    edges_added = 0
    for u, v, edge_data in G.edges(data=True):
        # Ensure edge_data is a dictionary
        if not isinstance(edge_data, dict):
            edge_data = {}
        
        edge_styling = get_pharma_edge_styling(str(u), str(v), edge_data, highlight_edges, target_batch_id)
        
        net.add_edge(
            str(u),  # Ensure node IDs are strings
            str(v),
            label=edge_styling["label"],
            color=edge_styling["color"],
            width=edge_styling["width"],
            arrows=edge_styling["arrows"],
            opacity=edge_styling["opacity"],
            dashes=edge_styling["dashes"],
            smooth=True,
            font=edge_styling["font"],
            length=edge_styling["length"]
        )
        edges_added += 1
    
    st.success(f"✅ Added {nodes_added} nodes and {edges_added} edges to graph")
    
    # === PHARMA PROFESSIONAL CONFIGURATION ===
    config = {
        "physics": {
            "enabled": False,
            "stabilization": {
                "enabled": True,
                "iterations": 1000
            }
        },
        "interaction": {
            "dragNodes": True,
            "dragView": True,
            "zoomView": True,
            "hover": True,
            "tooltipDelay": 100,
            "multiselect": False,
            "navigationButtons": True,
            "keyboard": {"enabled": False}
        },
        "edges": {
            "smooth": {"enabled": True, "type": "continuous"},
            "arrows": {
                "to": {
                    "enabled": True,
                    "scaleFactor": 0.8,
                    "type": "arrow"
                }
            },
            "color": {"inherit": False},
            "shadow": False
        },
        "nodes": {
            "borderWidth": 2,
            "font": {"align": "center"},
            "shadow": {"enabled": True, "color": "rgba(0,0,0,0.1)", "size": 5},
            "scaling": {
                "min": 20,
                "max": 50,
                "label": {"enabled": True}
            }
        },
        "layout": {
            "improvedLayout": True,
            "hierarchical": {
                "enabled": False
            }
        }
    }
    
    net.set_options(json.dumps(config))
    
    # === SAVE AND RENDER ===
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
            net.save_graph(tmp.name)
            tmp_path = tmp.name
        
        with open(tmp_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Add pharma professional legend
        legend_html = generate_pharma_legend(target_batch_id, trace_mode, highlight_nodes)
        html_content = html_content.replace('</body>', f'{legend_html}</body>')
        
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        with open(tmp_path, 'r', encoding='utf-8') as f:
            components.html(f.read(), height=900, scrolling=False)
        
        os.unlink(tmp_path)
        st.success("🎯 Graph rendered successfully!")
        
    except Exception as e:
        st.error(f"❌ Error rendering graph: {str(e)}")
        # Try to show the graph without legend as fallback
        try:
            net.show("graph.html")
            st.warning("⚠️ Graph saved to graph.html as fallback")
        except:
            st.error("Failed to save graph as fallback")

def calculate_trace_highlights(G, target_batch_id, trace_mode):
    """Calculate which nodes/edges to highlight based on trace mode"""
    highlight_nodes = set()
    highlight_edges = set()
    
    if target_batch_id and target_batch_id in G.nodes:
        highlight_nodes.add(target_batch_id)
        
        if trace_mode in ["forward", "both"]:
            try:
                descendants = nx.descendants(G, target_batch_id)
                highlight_nodes.update(descendants)
                
                for desc in descendants:
                    try:
                        if nx.has_path(G, target_batch_id, desc):
                            path = nx.shortest_path(G, target_batch_id, desc)
                            for i in range(len(path) - 1):
                                highlight_edges.add((path[i], path[i + 1]))
                    except:
                        continue
            except nx.NetworkXError:
                pass
        
        if trace_mode in ["backward", "both"]:
            try:
                ancestors = nx.ancestors(G, target_batch_id)
                highlight_nodes.update(ancestors)
                
                for anc in ancestors:
                    try:
                        if nx.has_path(G, anc, target_batch_id):
                            path = nx.shortest_path(G, anc, target_batch_id)
                            for i in range(len(path) - 1):
                                highlight_edges.add((path[i], path[i + 1]))
                    except:
                        continue
            except nx.NetworkXError:
                pass
    
    return highlight_nodes, highlight_edges

def calculate_pharma_positions(G, target_batch_id=None):
    """Calculate positions for pharma process flow layout"""
    positions = {}
    
    if G.number_of_nodes() == 0:
        return positions
    
    # Group by pharmaceutical process stage
    raw_materials = [n for n in G.nodes() if G.nodes[n].get("type") == "Raw Material"]
    apis = [n for n in raw_materials if "API" in str(G.nodes[n].get("material", "")).upper()]
    excipients = [n for n in raw_materials if n not in apis]
    
    intermediates = [n for n in G.nodes() if G.nodes[n].get("type") == "Intermediate"]
    blends = [n for n in intermediates if "BLEND" in str(G.nodes[n].get("material", "")).upper()]
    solutions = [n for n in intermediates if n not in blends]
    
    finished_products = [n for n in G.nodes() if G.nodes[n].get("type") == "Finished Product"]
    tablets = [n for n in finished_products if "TAB" in str(n).upper()]
    capsules = [n for n in finished_products if "CAP" in str(n).upper()]
    others = [n for n in finished_products if n not in tablets and n not in capsules]
    
    # Pharmaceutical Process Flow Columns with better positioning
    columns = {
        "API": {"x": 100, "nodes": apis[:20]},  # Limit to 20 nodes per column
        "Excipients": {"x": 300, "nodes": excipients[:20]},
        "Blending": {"x": 500, "nodes": blends[:20]},
        "Solutions": {"x": 700, "nodes": solutions[:20]},
        "Tablets": {"x": 900, "nodes": tablets[:20]},
        "Capsules": {"x": 1100, "nodes": capsules[:20]},
        "Other Products": {"x": 1300, "nodes": others[:20]}
    }
    
    # Position nodes in their process columns with better spacing
    for col_name, col_data in columns.items():
        y_start = 100
        y_spacing = 120
        for i, node in enumerate(col_data["nodes"]):
            positions[node] = {"x": col_data["x"], "y": y_start + i * y_spacing}
    
    # Handle remaining nodes that weren't categorized
    all_categorized = set()
    for col_data in columns.values():
        all_categorized.update(col_data["nodes"])
    
    remaining_nodes = [n for n in G.nodes() if n not in all_categorized]
    
    # Position remaining nodes in a grid
    grid_x = 100
    grid_y = 100
    for i, node in enumerate(remaining_nodes[:100]):  # Limit to 100 remaining nodes
        positions[node] = {"x": grid_x + (i % 10) * 150, "y": grid_y + (i // 10) * 150}
    
    # Center target node if provided
    if target_batch_id and target_batch_id in positions:
        positions[target_batch_id]["x"] = 700  # Center horizontally
        positions[target_batch_id]["y"] = 400  # Center vertically
    
    return positions

def get_pharma_node_styling(node_data, node_id, target_batch_id, is_highlighted):
    """Get pharmaceutical professional styling for nodes"""
    
    node_type = node_data.get("type", "Unknown")
    material = str(node_data.get("material", "")).upper()
    is_target = str(node_id) == str(target_batch_id)
    
    # Pharma Color Scheme
    pharma_colors = {
        "Raw Material": {
            "API": {"color": "#1e88e5", "border": "#0d47a1"},
            "Excipient": {"color": "#43a047", "border": "#1b5e20"},
            "Solvent": {"color": "#5e35b1", "border": "#311b92"},
            "default": {"color": "#78909c", "border": "#37474f"}
        },
        "Intermediate": {
            "Blend": {"color": "#ff9800", "border": "#e65100"},
            "Solution": {"color": "#00acc1", "border": "#006064"},
            "Granulation": {"color": "#8e24aa", "border": "#4a148c"},
            "default": {"color": "#fb8c00", "border": "#e65100"}
        },
        "Finished Product": {
            "Tablet": {"color": "#00c853", "border": "#1b5e20"},
            "Capsule": {"color": "#ff4081", "border": "#c51162"},
            "Injection": {"color": "#2962ff", "border": "#0039cb"},
            "default": {"color": "#00bfa5", "border": "#00796b"}
        },
        "Unknown": {
            "default": {"color": "#9e9e9e", "border": "#616161"}
        }
    }
    
    # Determine specific type
    specific_type = "default"
    if "API" in material:
        specific_type = "API"
    elif any(x in material for x in ["EXCIPIENT", "FILLER", "BINDER", "DILUENT"]):
        specific_type = "Excipient"
    elif any(x in material for x in ["SOLVENT", "WATER", "ETHANOL", "ISOPROPYL"]):
        specific_type = "Solvent"
    elif "BLEND" in material or "MIX" in material:
        specific_type = "Blend"
    elif "SOLUTION" in material or "LIQUID" in material:
        specific_type = "Solution"
    elif "GRANULATION" in material:
        specific_type = "Granulation"
    elif "TABLET" in material or "TAB" in str(node_id).upper():
        specific_type = "Tablet"
    elif "CAPSULE" in material or "CAP" in str(node_id).upper():
        specific_type = "Capsule"
    
    # Get colors
    color_info = pharma_colors.get(node_type, {}).get(specific_type, 
                    pharma_colors.get(node_type, {}).get("default", 
                    {"color": "#607d8b", "border": "#37474f"}))
    
    # Shapes based on pharmaceutical item
    shape_map = {
        "Raw Material": "ellipse",
        "Intermediate": "box",
        "Finished Product": "star",
        "API": "diamond",
        "Tablet": "hexagon",
        "Capsule": "ellipse",
        "Blend": "triangle",
        "Solution": "dot"
    }
    
    shape = shape_map.get(specific_type, shape_map.get(node_type, "circle"))
    
    # Sizes
    if is_target:
        size = 45
        border_width = 4
        font_size = 16
        font_color = "#d84315"
        bold = True
        shadow = True
    elif is_highlighted:
        size = 35
        border_width = 3
        font_size = 14
        font_color = color_info["border"]
        bold = True
        shadow = True
    else:
        size = 28 if node_type == "Finished Product" else 25 if node_type == "Intermediate" else 22
        border_width = 2
        font_size = 12
        font_color = "#455a64"
        bold = False
        shadow = False
    
    # Create label with pharmaceutical abbreviations
    label = format_pharma_label(node_id, node_data.get("material", ""))
    
    return {
        "label": label,
        "color": color_info["color"],
        "border_color": color_info["border"],
        "shape": shape,
        "size": size,
        "border_width": border_width,
        "font_size": font_size,
        "font_color": font_color,
        "bold": bold,
        "shadow": shadow
    }

def format_pharma_label(batch_id, material):
    """Format pharmaceutical labels professionally"""
    # Convert to string
    batch_str = str(batch_id)
    material_str = str(material) if material else "Unknown"
    
    # Shorten material name
    material_words = material_str.split()
    if len(material_words) > 2:
        material_short = ' '.join(material_words[:2]) + '...'
    else:
        material_short = material_str
    
    # Use batch ID abbreviation
    if batch_str.startswith("RM-"):
        prefix = "RM"
    elif batch_str.startswith("INT-"):
        prefix = "INT"
    elif batch_str.startswith("FP-"):
        prefix = "FP"
    else:
        prefix = batch_str.split('-')[0] if '-' in batch_str else batch_str[:4]
    
    # Get numeric part
    numbers = re.findall(r'\d+', batch_str)
    number_part = numbers[0] if numbers else batch_str[-4:]
    
    return f"{prefix}-{number_part}\n{material_short[:12]}"

def get_pharma_edge_styling(u, v, edge_data, highlight_edges, target_batch_id):
    """Get pharmaceutical professional styling for edges"""
    is_highlighted = (str(u), str(v)) in highlight_edges or (str(u), str(v)) in [tuple(map(str, e)) for e in highlight_edges]
    is_target_edge = (str(u) == str(target_batch_id) or str(v) == str(target_batch_id))
    relationship = str(edge_data.get("relationship", ""))
    
    # Pharma edge styling
    if is_highlighted:
        color = "#d32f2f"
        width = 4
        opacity = 1.0
        dashes = False
        font_color = "#d32f2f"
    elif is_target_edge:
        color = "#ff9800"
        width = 3
        opacity = 0.9
        dashes = [5, 5]
        font_color = "#ff9800"
    elif relationship == "consumed_by":
        color = "#78909c"
        width = 2
        opacity = 0.7
        dashes = False
        font_color = "#546e7a"
    elif relationship == "produces":
        color = "#4caf50"
        width = 2
        opacity = 0.7
        dashes = [10, 5]
        font_color = "#2e7d32"
    else:
        color = "#b0bec5"
        width = 1
        opacity = 0.5
        dashes = True
        font_color = "#78909c"
    
    # Format edge label professionally
    label = format_edge_label(edge_data)
    
    return {
        "label": label,
        "color": color,
        "width": width,
        "arrows": "to",
        "opacity": opacity,
        "dashes": dashes,
        "font": {
            "size": 11,
            "color": font_color,
            "align": "middle",
            "strokeWidth": 0
        },
        "length": 200
    }

def format_edge_label(edge_data):
    """Format edge labels professionally"""
    relationship = str(edge_data.get("relationship", ""))
    quantity = edge_data.get("quantity")
    unit = edge_data.get("unit", "")
    
    # Professional relationship names
    rel_map = {
        "consumed_by": "Consumes",
        "produces": "Produces",
        "precedes": "Precedes",
        "coated_with": "Coated With",
        "mixed_with": "Mixed With",
        "transformed_into": "Transforms To",
        "contains": "Contains"
    }
    
    display_rel = rel_map.get(relationship, relationship.replace("_", " ").title())
    
    if quantity is not None and str(quantity).strip():
        try:
            # Try to convert quantity to a number
            if isinstance(quantity, str):
                # Remove any non-numeric characters (except decimal point)
                quantity_str = re.sub(r'[^\d.]', '', quantity)
                if quantity_str:
                    quantity_num = float(quantity_str)
                else:
                    quantity_num = None
            else:
                quantity_num = float(quantity)
            
            if quantity_num is not None:
                # Format quantity professionally
                if quantity_num >= 1000:
                    formatted_qty = f"{quantity_num/1000:.1f}k"
                elif quantity_num == int(quantity_num):
                    # If it's a whole number, display as integer
                    formatted_qty = str(int(quantity_num))
                else:
                    # If it has decimals, display with 1 decimal place
                    formatted_qty = f"{quantity_num:.1f}"
                
                # Add unit if provided
                if unit:
                    return f"{display_rel}\n{formatted_qty} {unit}"
                else:
                    return f"{display_rel}\n{formatted_qty}"
        except (ValueError, TypeError, AttributeError):
            # If conversion fails, just use the relationship
            pass
    
    return display_rel

def generate_pharma_tooltip(node_data, node_id):
    """Generate professional pharmaceutical tooltip"""
    # Extract batch label for tooltip header
    if "label" in node_data:
        label_parts = str(node_data.get("label")).split('\n')
        batch_label = label_parts[0] if len(label_parts) > 0 else str(node_id)
    else:
        batch_label = str(node_id)
    
    # Get node color for border
    node_color = node_data.get('color', '#1e88e5')
    
    tooltip = f"""
    <div style="padding: 12px; font-family: 'Arial', sans-serif; max-width: 350px; background: white; border-radius: 8px; box-shadow: 0 6px 24px rgba(0,0,0,0.15); border-left: 4px solid {node_color};">
        <div style="font-weight: 700; font-size: 14px; margin-bottom: 8px; color: #1a237e; border-bottom: 2px solid #e8eaf6; padding-bottom: 6px;">
            🏭 {batch_label}
        </div>
        
        <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
    """
    
    # Pharma-specific fields in order of importance
    fields = [
        ("📦", "Material", node_data.get("material", ""), "#1a3c6e"),
        ("🏷️", "Type", node_data.get("type", ""), "#1e88e5"),
        ("⚖️", "Quantity", node_data.get("quantity", ""), "#43a047"),
        ("💊", "Product", node_data.get("product", ""), "#8e24aa"),
        ("📊", "Status", node_data.get("status", ""), "#fb8c00"),
        ("✅", "Quality", node_data.get("quality", ""), "#00acc1"),
        ("🔢", "Batch ID", node_id, "#546e7a")
    ]
    
    for icon, label, value, color in fields:
        if value is not None and str(value).strip() and str(value).lower() != "nan":
            tooltip += f"""
            <tr>
                <td style="padding: 4px 0; color: #546e7a; font-weight: 500; width: 40%;">{icon} {label}:</td>
                <td style="padding: 4px 0; color: {color}; font-weight: 600; text-align: right;">{value}</td>
            </tr>
            """
    
    # Add additional fields if they exist
    additional_fields = ["lot", "expiry_date", "manufacturer", "location", "manufacturing_date", "expiration_date"]
    for field in additional_fields:
        if field in node_data and node_data[field] is not None:
            value = node_data[field]
            if str(value).strip() and str(value).lower() != "nan":
                tooltip += f"""
                <tr>
                    <td style="padding: 4px 0; color: #546e7a; font-weight: 500;">📋 {field.title().replace('_', ' ')}:</td>
                    <td style="padding: 4px 0; color: #757575; font-weight: 500; text-align: right;">{value}</td>
                </tr>
                """
    
    tooltip += """
        </table>
        
        <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #f5f5f5; font-size: 11px; color: #78909c;">
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span style="margin-right: 6px;">📋</span>
                <span>GMP Batch Record Reference</span>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="margin-right: 6px;">🔗</span>
                <span>Pharmaceutical Traceability</span>
            </div>
        </div>
    </div>
    """
    return tooltip

def generate_pharma_legend(target_batch_id, trace_mode, highlight_nodes):
    """Generate pharmaceutical professional legend"""
    
    trace_descriptions = {
        "none": "Full material flow view",
        "forward": "Downstream product trace",
        "backward": "Upstream material trace",
        "both": "Complete genealogy trace"
    }
    
    highlight_count = len(highlight_nodes) if highlight_nodes else 0
    
    target_section = ""
    if target_batch_id:
        target_section = f"""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 12px; border-radius: 8px; margin-bottom: 16px; border-left: 4px solid #1e88e5;">
            <div style="font-weight: 700; color: #0d47a1; font-size: 13px;">🧬 TARGET BATCH</div>
            <div style="font-family: monospace; background: white; padding: 6px; border-radius: 4px; margin-top: 6px; border: 1px solid #bbdefb;">
                <code style="color: #1a3c6e;">{target_batch_id}</code>
            </div>
            <div style="font-size: 11px; color: #1565c0; margin-top: 6px;">
                {trace_descriptions.get(trace_mode, "")} • {highlight_count} batches in trace
            </div>
        </div>
        """
    
    return f"""
    <div style="
        position: absolute;
        top: 20px;
        right: 20px;
        padding: 20px;
        font-family: 'Arial', 'Segoe UI', sans-serif;
        font-size: 12.5px;
        background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(250,251,252,0.98) 100%);
        border-radius: 12px;
        border: 1px solid #e1e8ed;
        box-shadow: 0 8px 32px rgba(26, 60, 110, 0.12);
        z-index: 1000;
        max-width: 280px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 2px solid #1e88e5;">
            <div style="font-size: 20px; margin-right: 10px; color: #1e88e5;">💊</div>
            <div>
                <div style="font-weight: 800; font-size: 15px; color: #1a3c6e; letter-spacing: 0.5px;">PHARMA GENEALOGY</div>
                <div style="font-size: 11px; color: #5d7fa3; margin-top: 2px;">Material Traceability System</div>
            </div>
        </div>
        
        {target_section}
        
        <div style="margin-bottom: 16px;">
            <div style="font-weight: 700; color: #37474f; font-size: 12px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;">🧪 BATCH TYPES</div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <div style="background: rgba(30, 136, 229, 0.08); padding: 8px; border-radius: 6px; border: 1px solid rgba(30, 136, 229, 0.2);">
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <div style="width: 10px; height: 10px; background: #1e88e5; border-radius: 50%; margin-right: 6px;"></div>
                        <span style="font-weight: 600; font-size: 11px;">API</span>
                    </div>
                    <div style="font-size: 10px; color: #5d7fa3;">Active Ingredient</div>
                </div>
                
                <div style="background: rgba(67, 160, 71, 0.08); padding: 8px; border-radius: 6px; border: 1px solid rgba(67, 160, 71, 0.2);">
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <div style="width: 10px; height: 10px; background: #43a047; border-radius: 50%; margin-right: 6px;"></div>
                        <span style="font-weight: 600; font-size: 11px;">Excipient</span>
                    </div>
                    <div style="font-size: 10px; color: #5d7fa3;">Inactive Ingredient</div>
                </div>
                
                <div style="background: rgba(255, 152, 0, 0.08); padding: 8px; border-radius: 6px; border: 1px solid rgba(255, 152, 0, 0.2);">
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <div style="width: 10px; height: 10px; background: #ff9800; border: 1px solid #e65100; margin-right: 6px;"></div>
                        <span style="font-weight: 600; font-size: 11px;">Blend</span>
                    </div>
                    <div style="font-size: 10px; color: #5d7fa3;">Intermediate Mix</div>
                </div>
                
                <div style="background: rgba(0, 200, 83, 0.08); padding: 8px; border-radius: 6px; border: 1px solid rgba(0, 200, 83, 0.2);">
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <div style="width: 10px; height: 10px; background: #00c853; border-radius: 0 50% 50% 50%; transform: rotate(45deg); margin-right: 6px;"></div>
                        <span style="font-weight: 600; font-size: 11px;">Tablet</span>
                    </div>
                    <div style="font-size: 10px; color: #5d7fa3;">Final Product</div>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 16px;">
            <div style="font-weight: 700; color: #37474f; font-size: 12px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">🔗 TRACE VISUALIZATION</div>
            
            <div style="display: flex; align-items: center; margin-bottom: 8px; padding: 8px; background: #fff8e1; border-radius: 6px; border-left: 3px solid #ffd54f;">
                <div style="width: 20px; height: 3px; background: #d32f2f; margin-right: 10px;"></div>
                <div>
                    <div style="font-weight: 600; font-size: 11.5px; color: #d32f2f;">Active Trace Path</div>
                    <div style="font-size: 10px; color: #5d7fa3;">Current material flow in focus</div>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 8px; padding: 8px; background: #f3e5f5; border-radius: 6px; border-left: 3px solid #ba68c8;">
                <div style="width: 20px; height: 2px; background: #8e24aa; margin-right: 10px;"></div>
                <div>
                    <div style="font-weight: 600; font-size: 11.5px; color: #8e24aa;">Production Flow</div>
                    <div style="font-size: 10px; color: #5d7fa3;">Manufacturing process steps</div>
                </div>
            </div>
        </div>
        
        <div style="padding-top: 12px; border-top: 1px solid #eceff1;">
            <div style="font-size: 11px; color: #5d7fa3; line-height: 1.5;">
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <span style="margin-right: 6px; color: #1e88e5;">👆</span>
                    <span><b>Hover</b> for batch details (GMP records)</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <span style="margin-right: 6px; color: #1e88e5;">🖱️</span>
                    <span><b>Drag</b> to reposition for clarity</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <span style="margin-right: 6px; color: #1e88e5;">🔍</span>
                    <span><b>Scroll</b> to zoom • For audit trails</span>
                </div>
            </div>
            <div style="margin-top: 10px; font-size: 10px; color: #90a4ae; text-align: center; font-style: italic;">
                Pharmaceutical Grade Visualization
            </div>
        </div>
    </div>
    """
