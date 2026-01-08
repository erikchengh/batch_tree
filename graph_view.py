from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx
import tempfile
import os

def render_genealogy_graph(G, target_batch_id=None, highlight_upstream=True, highlight_downstream=True):
    """
    Render an interactive batch genealogy graph
    
    Args:
        G: NetworkX graph of batch genealogy
        target_batch_id: Batch to focus on (None for full graph)
        highlight_upstream: Highlight raw materials feeding into target
        highlight_downstream: Highlight products using the target
    """
    
    # Create network
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#2d3436"
    )
    
    # Configure physics for better layout
    net.toggle_physics(True)
    net.barnes_hut(
        gravity=-2000,
        central_gravity=0.3,
        spring_length=150,
        spring_strength=0.05,
        damping=0.09,
        overlap=1
    )
    
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
    
    # Add nodes with styling
    for node_id, node_data in G.nodes(data=True):
        opacity = 1.0
        border_width = 2
        
        # Highlight target and related nodes
        if highlight_nodes:
            if node_id in highlight_nodes:
                border_width = 4
            else:
                opacity = 0.3
        
        # Add the node
        net.add_node(
            node_id,
            label=node_data["label"],
            color=node_data["color"],
            shape=node_data["shape"],
            size=node_data["size"],
            title=generate_node_tooltip(node_data),
            opacity=opacity,
            borderWidth=border_width,
            borderWidthSelected=border_width * 2,
            borderColor="#2c3e50",
            font={
                "size": node_data["size"] / 1.5,
                "face": "Arial",
                "color": "#2d3436",
                "strokeWidth": 0,
                "strokeColor": "#ffffff"
            },
            shadow={
                "enabled": True,
                "color": "rgba(0,0,0,0.1)",
                "size": 5,
                "x": 2,
                "y": 2
            }
        )
    
    # Add edges with styling
    for u, v, edge_data in G.edges(data=True):
        edge_opacity = 0.7
        edge_width = 2
        
        # Highlight edges connected to target
        if highlight_nodes and (u in highlight_nodes or v in highlight_nodes):
            edge_opacity = 1.0
            edge_width = 3
        
        net.add_edge(
            u, v,
            label=edge_data["label"],
            color=edge_data["color"],
            width=edge_width,
            arrows="to",
            opacity=edge_opacity,
            smooth={
                "type": "cubicBezier",
                "roundness": 0.3
            },
            font={
                "size": 11,
                "align": "middle",
                "color": "#7f8c8d"
            }
        )
    
    # Configure layout options
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "solver": "barnesHut",
        "barnesHut": {
          "gravitationalConstant": -2000,
          "centralGravity": 0.3,
          "springLength": 150,
          "springConstant": 0.05,
          "damping": 0.09,
          "avoidOverlap": 1
        },
        "stabilization": {
          "enabled": true,
          "iterations": 1000,
          "updateInterval": 100,
          "onlyDynamicEdges": false,
          "fit": true
        },
        "timestep": 0.5
      },
      "interaction": {
        "dragNodes": true,
        "dragView": true,
        "zoomView": true,
        "hover": true,
        "tooltipDelay": 100,
        "multiselect": true,
        "navigationButtons": true
      },
      "edges": {
        "smooth": {
          "type": "cubicBezier",
          "roundness": 0.3
        },
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 0.8
          }
        }
      }
    }
    """)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp:
        net.save_graph(tmp.name)
        tmp_path = tmp.name
    
    # Read and inject custom CSS/legend
    with open(tmp_path, 'r') as f:
        html_content = f.read()
    
    # Add legend and custom styling
    legend_html = generate_legend_html()
    html_content = html_content.replace(
        '</body>',
        f'{legend_html}\n</body>'
    )
    
    # Write back
    with open(tmp_path, 'w') as f:
        f.write(html_content)
    
    # Render in Streamlit
    with open(tmp_path, 'r') as f:
        components.html(f.read(), height=800, scrolling=False)
    
    # Clean up
    os.unlink(tmp_path)

def generate_node_tooltip(node_data):
    """Generate HTML tooltip for node"""
    tooltip = f"""
    <div style="padding: 10px; font-family: Arial; max-width: 300px;">
        <div style="font-weight: bold; font-size: 14px; margin-bottom: 5px; color: {node_data['color']};">
            {node_data['label'].split('\\n')[0]}
        </div>
        <div style="font-size: 12px; margin-bottom: 3px;">
            <b>Material:</b> {node_data['material']}
        </div>
        <div style="font-size: 12px; margin-bottom: 3px;">
            <b>Type:</b> {node_data['type']}
        </div>
        <div style="font-size: 12px; margin-bottom: 3px;">
            <b>Quantity:</b> {node_data['quantity']}
        </div>
    """
    
    if node_data.get('product'):
        tooltip += f"""
        <div style="font-size: 12px; margin-bottom: 3px;">
            <b>Product:</b> {node_data['product']}
        </div>
        """
    
    if node_data.get('status'):
        tooltip += f"""
        <div style="font-size: 12px; margin-bottom: 3px;">
            <b>Status:</b> {node_data['status']}
        </div>
        """
    
    if node_data.get('quality'):
        tooltip += f"""
        <div style="font-size: 12px; margin-bottom: 3px;">
            <b>Quality:</b> {node_data['quality']}
        </div>
        """
    
    tooltip += "</div>"
    return tooltip

def generate_legend_html():
    """Generate HTML legend for the graph"""
    return """
    <div style="
        position: absolute;
        top: 15px;
        right: 15px;
        padding: 15px;
        font-family: Arial, sans-serif;
        font-size: 12px;
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 8px;
        border: 1px solid #dfe6e9;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        max-width: 220px;
    ">
        <div style="font-weight: bold; margin-bottom: 10px; font-size: 14px; color: #2d3436;">
            📊 Batch Genealogy Legend
        </div>
        
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
        
        <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #dfe6e9;">
            <div style="font-weight: bold; margin-bottom: 5px; color: #636e72; font-size: 11px;">EDGES:</div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 20px; height: 2px; background-color: #e74c3c; margin-right: 8px;"></div>
                <span>Material Consumption</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 20px; height: 2px; background-color: #3498db; margin-right: 8px;"></div>
                <span>Process Sequence</span>
            </div>
        </div>
        
        <div style="margin-top: 10px; font-size: 11px; color: #636e72;">
            🔸 Click nodes for details<br>
            🔸 Drag to rearrange layout<br>
            🔸 Scroll to zoom in/out
        </div>
    </div>
    """
