from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx
import tempfile
import os
import json
import re
import streamlit as st
from collections import defaultdict

def render_genealogy_graph(G, target_batch_id=None, trace_mode="none"):
    """
    Render a pharmaceutical batch tree as top-down hierarchical structure
    
    Args:
        G: NetworkX graph
        target_batch_id: Batch to focus on
        trace_mode: "none", "forward", "backward", "both"
    """
    
    # Check if graph is empty
    if G.number_of_nodes() == 0:
        st.warning("⚠️ No graph data available. Please check your data source.")
        return
    
    # Create a top-down tree structure
    tree_G = create_top_down_tree(G, target_batch_id)
    
    st.info(f"📊 Rendering batch tree with {tree_G.number_of_nodes()} nodes and {tree_G.number_of_edges()} edges")
    
    # Create network with pharma professional theme
    net = Network(
        height="800px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#1a3c6e",
        notebook=False
    )
    
    # DISABLE PHYSICS - We'll use hierarchical layout
    net.toggle_physics(False)
    
    # === ADD PHARMA-STYLED NODES ===
    nodes_added = 0
    node_ids = list(tree_G.nodes())
    
    for node_id in node_ids:
        node_data = tree_G.nodes[node_id]
        
        # Get pharma-specific styling
        is_target = str(node_id) == str(target_batch_id)
        styling = get_pharma_node_styling(node_data, node_id, target_batch_id, is_target)
        
        # Add node with pharma styling
        net.add_node(
            str(node_id),
            label=styling["label"],
            color=styling["color"],
            shape=styling["shape"],
            size=styling["size"],
            title=generate_pharma_tooltip(node_data, node_id),
            borderWidth=styling["border_width"],
            borderColor=styling["border_color"],
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
    for u, v, edge_data in tree_G.edges(data=True):
        if not isinstance(edge_data, dict):
            edge_data = {}
        
        # Create hierarchical tree edges
        edge_styling = get_tree_edge_styling(str(u), str(v), edge_data, target_batch_id)
        
        net.add_edge(
            str(u),
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
    
    st.success(f"✅ Added {nodes_added} nodes and {edges_added} edges to tree")
    
    # === TOP-DOWN TREE CONFIGURATION ===
    config = {
        "physics": {
            "enabled": False,
            "stabilization": {"enabled": False}
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
            "smooth": {
                "enabled": True,
                "type": "vertical",
                "forceDirection": "vertical",
                "roundness": 0.3
            },
            "arrows": {
                "to": {
                    "enabled": True,
                    "scaleFactor": 0.8,
                    "type": "arrow"
                }
            },
            "color": {"inherit": False},
            "shadow": False,
            "width": 2
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
            "improvedLayout": False,
            "hierarchical": {
                "enabled": True,
                "levelSeparation": 200,      # Vertical spacing between levels
                "nodeSpacing": 100,          # Horizontal spacing between nodes
                "treeSpacing": 200,          # Spacing between different trees
                "blockShifting": True,
                "edgeMinimization": True,
                "parentCentralization": True,
                "direction": "UD",           # Up-Down direction (Top-Down)
                "sortMethod": "directed",
                "shakeTowards": "roots"      # Shake towards the root (top)
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
        legend_html = generate_batch_tree_legend(target_batch_id, tree_G)
        html_content = html_content.replace('</body>', f'{legend_html}</body>')
        
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        with open(tmp_path, 'r', encoding='utf-8') as f:
            components.html(f.read(), height=900, scrolling=False)
        
        os.unlink(tmp_path)
        st.success("🌳 Batch tree rendered successfully!")
        
    except Exception as e:
        st.error(f"❌ Error rendering tree: {str(e)}")

def create_top_down_tree(G, target_batch_id=None):
    """
    Create a top-down tree structure with target batch at the top
    and raw materials at the bottom
    """
    tree = nx.DiGraph()
    
    if not target_batch_id or target_batch_id not in G:
        # If no target, use first finished product
        finished_products = [n for n in G.nodes() if G.nodes[n].get("type") == "Finished Product"]
        if finished_products:
            target_batch_id = finished_products[0]
        else:
            return tree
    
    # Add the target batch as root
    target_data = G.nodes[target_batch_id]
    tree.add_node(target_batch_id, **target_data, level=0, is_root=True)
    
    # Find all raw materials that go into this product (directly or through intermediates)
    raw_materials = find_all_raw_materials(G, target_batch_id)
    
    # Group raw materials by type for better organization
    material_groups = defaultdict(list)
    for rm in raw_materials:
        rm_data = G.nodes[rm]
        material_name = rm_data.get("material", "Unknown")
        
        # Categorize by material type
        if "API" in str(material_name).upper():
            group = "API"
        elif any(x in str(material_name).upper() for x in ["EXCIPIENT", "FILLER", "BINDER"]):
            group = "Excipient"
        elif any(x in str(material_name).upper() for x in ["SOLVENT", "WATER"]):
            group = "Solvent"
        else:
            group = "Other"
        
        material_groups[group].append(rm)
    
    # Add raw materials to tree
    level = 1
    for group_name, materials in material_groups.items():
        # Add group node (optional, can comment out for simpler view)
        group_node_id = f"GROUP-{group_name}"
        tree.add_node(group_node_id, 
                     material=group_name, 
                     type="Material Group",
                     level=level,
                     is_group=True)
        
        # Connect group to target
        tree.add_edge(group_node_id, target_batch_id, 
                     relationship=f"{group_name} Group",
                     color="#90CAF9")
        
        # Add individual materials under group
        for i, rm in enumerate(materials):
            rm_data = G.nodes[rm]
            tree.add_node(rm, **rm_data, level=level + 1, is_leaf=True)
            tree.add_edge(rm, group_node_id, 
                         relationship="belongs_to",
                         quantity=rm_data.get("quantity", ""),
                         unit=rm_data.get("unit", ""))
        
        level += 2
    
    # If no groups were created (simpler view), add materials directly
    if tree.number_of_nodes() == 1:  # Only root exists
        level = 1
        for rm in raw_materials:
            rm_data = G.nodes[rm]
            tree.add_node(rm, **rm_data, level=level, is_leaf=True)
            tree.add_edge(rm, target_batch_id, 
                         relationship="used_in",
                         quantity=rm_data.get("quantity", ""),
                         unit=rm_data.get("unit", ""))
    
    return tree

def find_all_raw_materials(G, node):
    """Find all raw material ancestors of a node, skipping intermediates"""
    raw_materials = set()
    visited = set()
    
    def dfs(current):
        if current in visited:
            return
        visited.add(current)
        
        for predecessor in G.predecessors(current):
            pred_data = G.nodes[predecessor]
            pred_type = pred_data.get("type", "Unknown")
            
            if pred_type == "Raw Material":
                raw_materials.add(predecessor)
            else:
                # Continue DFS for non-raw materials
                dfs(predecessor)
    
    dfs(node)
    return list(raw_materials)

def get_pharma_node_styling(node_data, node_id, target_batch_id, is_highlighted):
    """Get pharmaceutical professional styling for nodes"""
    
    node_type = node_data.get("type", "Unknown")
    material = str(node_data.get("material", "")).upper()
    is_root = node_data.get("is_root", False)
    is_group = node_data.get("is_group", False)
    is_leaf = node_data.get("is_leaf", False)
    is_target = str(node_id) == str(target_batch_id)
    
    # Pharma Color Scheme
    pharma_colors = {
        "Finished Product": {
            "Tablet": {"color": "#00c853", "border": "#1b5e20"},
            "Capsule": {"color": "#ff4081", "border": "#c51162"},
            "Injection": {"color": "#2962ff", "border": "#0039cb"},
            "default": {"color": "#00bfa5", "border": "#00796b"}
        },
        "Raw Material": {
            "API": {"color": "#1e88e5", "border": "#0d47a1"},
            "Excipient": {"color": "#43a047", "border": "#1b5e20"},
            "Solvent": {"color": "#5e35b1", "border": "#311b92"},
            "default": {"color": "#78909c", "border": "#37474f"}
        },
        "Material Group": {
            "default": {"color": "#FFE082", "border": "#FFB300"}
        }
    }
    
    # Determine specific type
    specific_type = "default"
    if is_group:
        node_type = "Material Group"
        if "API" in str(node_data.get("material", "")):
            specific_type = "API"
        elif "Excipient" in str(node_data.get("material", "")):
            specific_type = "Excipient"
        elif "Solvent" in str(node_data.get("material", "")):
            specific_type = "Solvent"
    elif "API" in material:
        specific_type = "API"
        node_type = "Raw Material"
    elif any(x in material for x in ["EXCIPIENT", "FILLER", "BINDER", "DILUENT"]):
        specific_type = "Excipient"
        node_type = "Raw Material"
    elif any(x in material for x in ["SOLVENT", "WATER", "ETHANOL", "ISOPROPYL"]):
        specific_type = "Solvent"
        node_type = "Raw Material"
    elif "TABLET" in material or "TAB" in str(node_id).upper():
        specific_type = "Tablet"
        node_type = "Finished Product"
    elif "CAPSULE" in material or "CAP" in str(node_id).upper():
        specific_type = "Capsule"
        node_type = "Finished Product"
    
    # Get colors
    color_info = pharma_colors.get(node_type, {}).get(specific_type, 
                    pharma_colors.get(node_type, {}).get("default", 
                    {"color": "#607d8b", "border": "#37474f"}))
    
    # Shapes based on node role
    if is_root or is_target:
        shape = "star"
    elif is_group:
        shape = "hexagon"
    elif node_type == "Finished Product":
        shape = "diamond"
    elif specific_type == "API":
        shape = "triangle"
    elif specific_type == "Excipient":
        shape = "square"
    elif specific_type == "Solvent":
        shape = "ellipse"
    else:
        shape = "circle"
    
    # Sizes based on node importance
    if is_root or is_target:
        size = 50
        border_width = 4
        font_size = 16
        font_color = "#d84315"
        bold = True
        shadow = True
    elif is_group:
        size = 40
        border_width = 3
        font_size = 14
        font_color = color_info["border"]
        bold = True
        shadow = True
    elif node_type == "Finished Product":
        size = 45
        border_width = 3
        font_size = 14
        font_color = color_info["border"]
        bold = True
        shadow = True
    else:  # Raw materials
        size = 35
        border_width = 2
        font_size = 12
        font_color = "#455a64"
        bold = False
        shadow = False
    
    # Create label
    if is_group:
        label = f"📦 {node_data.get('material', 'Group')}"
    else:
        label = format_batch_label(node_id, node_data.get("material", ""))
    
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

def format_batch_label(batch_id, material):
    """Format batch labels for tree display"""
    batch_str = str(batch_id)
    material_str = str(material) if material else "Unknown"
    
    # Get batch number
    numbers = re.findall(r'\d+', batch_str)
    batch_num = numbers[0] if numbers else batch_str[-4:]
    
    # Get batch type prefix
    if batch_str.startswith("RM-"):
        prefix = "RM"
        icon = "🧪"
    elif batch_str.startswith("FP-"):
        prefix = "FP"
        icon = "💊"
    else:
        prefix = batch_str.split('-')[0] if '-' in batch_str else "BT"
        icon = "📦"
    
    # Shorten material
    material_words = material_str.split()
    if len(material_words) > 2:
        material_short = ' '.join(material_words[:2])
    else:
        material_short = material_str
    
    return f"{icon} {prefix}-{batch_num}\n{material_short[:12]}"

def get_tree_edge_styling(u, v, edge_data, target_batch_id):
    """Get tree edge styling for hierarchical display"""
    relationship = str(edge_data.get("relationship", ""))
    quantity = edge_data.get("quantity", "")
    unit = edge_data.get("unit", "")
    
    # Tree edge styling
    if "GROUP" in u:
        color = "#90CAF9"  # Light blue for group edges
        width = 2
        opacity = 0.8
        dashes = [5, 5]
        font_color = "#1E88E5"
    elif relationship == "used_in" or relationship == "belongs_to":
        color = "#81C784"  # Green for material flow
        width = 3
        opacity = 0.9
        dashes = False
        font_color = "#2E7D32"
    else:
        color = "#BDBDBD"  # Gray for others
        width = 2
        opacity = 0.6
        dashes = True
        font_color = "#757575"
    
    # Format edge label
    label = ""
    if quantity and str(quantity).strip():
        try:
            qty_num = float(quantity)
            if qty_num >= 1000:
                formatted_qty = f"{qty_num/1000:.1f}k"
            elif qty_num == int(qty_num):
                formatted_qty = str(int(qty_num))
            else:
                formatted_qty = f"{qty_num:.1f}"
            
            if unit:
                label = f"{formatted_qty} {unit}"
            else:
                label = formatted_qty
        except:
            label = str(quantity)
    
    return {
        "label": label,
        "color": color,
        "width": width,
        "arrows": "to",
        "opacity": opacity,
        "dashes": dashes,
        "font": {
            "size": 10,
            "color": font_color,
            "align": "middle",
            "strokeWidth": 0
        },
        "length": 150
    }

def generate_pharma_tooltip(node_data, node_id):
    """Generate professional pharmaceutical tooltip"""
    batch_label = format_batch_label(node_id, node_data.get("material", ""))
    
    tooltip = f"""
    <div style="padding: 12px; font-family: 'Arial', sans-serif; max-width: 300px; background: white; border-radius: 8px; box-shadow: 0 6px 24px rgba(0,0,0,0.15); border-left: 4px solid #1e88e5;">
        <div style="font-weight: 700; font-size: 14px; margin-bottom: 8px; color: #1a237e; border-bottom: 2px solid #e8eaf6; padding-bottom: 6px;">
            {batch_label}
        </div>
        
        <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
    """
    
    fields = [
        ("📦", "Material", node_data.get("material", "")),
        ("🏷️", "Type", node_data.get("type", "")),
        ("⚖️", "Quantity", node_data.get("quantity", "")),
        ("📊", "Status", node_data.get("status", "")),
        ("✅", "Quality", node_data.get("quality", ""))
    ]
    
    for icon, label, value in fields:
        if value and str(value).strip() and str(value).lower() != "nan":
            tooltip += f"""
            <tr>
                <td style="padding: 4px 0; color: #546e7a; font-weight: 500; width: 40%;">{icon} {label}:</td>
                <td style="padding: 4px 0; color: #1a3c6e; font-weight: 600; text-align: right;">{value}</td>
            </tr>
            """
    
    tooltip += """
        </table>
        
        <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #f5f5f5; font-size: 11px; color: #78909c;">
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span style="margin-right: 6px;">📋</span>
                <span>GMP Batch Record</span>
            </div>
        </div>
    </div>
    """
    return tooltip

def generate_batch_tree_legend(target_batch_id, tree_G):
    """Generate legend for batch tree view"""
    
    if not target_batch_id or target_batch_id not in tree_G:
        return ""
    
    target_data = tree_G.nodes[target_batch_id]
    material_name = target_data.get("material", "Unknown Product")
    
    # Count nodes by type
    node_count = tree_G.number_of_nodes()
    edge_count = tree_G.number_of_edges()
    
    # Count raw materials
    raw_materials = [n for n in tree_G.nodes() 
                    if tree_G.nodes[n].get("type") == "Raw Material"]
    rm_count = len(raw_materials)
    
    # Count groups
    groups = [n for n in tree_G.nodes() 
             if tree_G.nodes[n].get("is_group", False)]
    group_count = len(groups)
    
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
            <div style="font-size: 24px; margin-right: 10px; color: #1e88e5;">🌳</div>
            <div>
                <div style="font-weight: 800; font-size: 15px; color: #1a3c6e; letter-spacing: 0.5px;">BATCH TREE VIEW</div>
                <div style="font-size: 11px; color: #5d7fa3; margin-top: 2px;">Top-Down Genealogy</div>
            </div>
        </div>
        
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 12px; border-radius: 8px; margin-bottom: 16px; border-left: 4px solid #1e88e5;">
            <div style="font-weight: 700; color: #0d47a1; font-size: 13px;">🎯 ROOT BATCH</div>
            <div style="font-family: monospace; background: white; padding: 6px; border-radius: 4px; margin-top: 6px; border: 1px solid #bbdefb;">
                <code style="color: #1a3c6e;">{target_batch_id}</code>
            </div>
            <div style="font-size: 11px; color: #1565c0; margin-top: 6px;">
                {material_name}
            </div>
            <div style="font-size: 10px; color: #5d7fa3; margin-top: 4px;">
                Tree: {node_count} nodes • {edge_count} edges • {rm_count} raw materials
            </div>
        </div>
        
        <div style="margin-bottom: 16px;">
            <div style="font-weight: 700; color: #37474f; font-size: 12px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;">📊 TREE STRUCTURE</div>
            
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="display: flex; align-items: center; padding: 8px; background: rgba(0, 200, 83, 0.08); border-radius: 6px; border-left: 3px solid #00c853;">
                    <div style="width: 14px; height: 14px; background: #00c853; border-radius: 50% 50% 0 50%; transform: rotate(45deg); margin-right: 10px;"></div>
                    <div>
                        <div style="font-weight: 600; font-size: 11.5px; color: #2e7d32;">Root Node</div>
                        <div style="font-size: 10px; color: #5d7fa3;">Finished Product (Top)</div>
                    </div>
                </div>
                
                {f'<div style="display: flex; align-items: center; padding: 8px; background: rgba(255, 224, 130, 0.08); border-radius: 6px; border-left: 3px solid #FFB300;">
                    <div style="width: 14px; height: 14px; background: #FFB300; border-radius: 0 50% 50% 50%; transform: rotate(45deg); margin-right: 10px;"></div>
                    <div>
                        <div style="font-weight: 600; font-size: 11.5px; color: #FF8F00;">Material Groups</div>
                        <div style="font-size: 10px; color: #5d7fa3;">Grouped by type ({group_count} groups)</div>
                    </div>
                </div>' if group_count > 0 else ''}
                
                <div style="display: flex; align-items: center; padding: 8px; background: rgba(30, 136, 229, 0.08); border-radius: 6px; border-left: 3px solid #1e88e5;">
                    <div style="width: 14px; height: 14px; background: #1e88e5; border-radius: 50%; margin-right: 10px;"></div>
                    <div>
                        <div style="font-weight: 600; font-size: 11.5px; color: #1565c0;">Leaf Nodes</div>
                        <div style="font-size: 10px; color: #5d7fa3;">Raw Materials (Bottom)</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 16px;">
            <div style="font-weight: 700; color: #37474f; font-size: 12px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">🔗 FLOW DIRECTION</div>
            
            <div style="display: flex; flex-direction: column; align-items: center; padding: 12px; background: #f5f5f5; border-radius: 6px; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="font-size: 18px; color: #00c853;">⬇️</div>
                    <div style="margin-left: 8px;">
                        <div style="font-weight: 600; font-size: 11.5px; color: #2e7d32;">Top to Bottom Flow</div>
                        <div style="font-size: 10px; color: #5d7fa3;">Product → Materials</div>
                    </div>
                </div>
                <div style="width: 100%; height: 2px; background: linear-gradient(to right, #00c853, #1e88e5); margin: 8px 0;"></div>
                <div style="font-size: 10px; color: #757575; text-align: center;">
                    Vertical hierarchy shows genealogy
                </div>
            </div>
        </div>
        
        <div style="padding-top: 12px; border-top: 1px solid #eceff1;">
            <div style="font-size: 11px; color: #5d7fa3; line-height: 1.5;">
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <span style="margin-right: 6px; color: #1e88e5;">👆</span>
                    <span><b>Hover</b> over nodes for details</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <span style="margin-right: 6px; color: #1e88e5;">🖱️</span>
                    <span><b>Drag</b> to rearrange layout</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <span style="margin-right: 6px; color: #1e88e5;">🔍</span>
                    <span><b>Scroll</b> to zoom in/out</span>
                </div>
            </div>
            <div style="margin-top: 10px; font-size: 10px; color: #90a4ae; text-align: center; font-style: italic;">
                Pharmaceutical Batch Genealogy Tree
            </div>
        </div>
    </div>
    """
