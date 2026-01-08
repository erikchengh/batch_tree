def render_graph(G, selected_node=None, deviation_only=False, trace_mode="None"):
    net = Network(
        height="700px", 
        width="100%", 
        directed=True,
        bgcolor="#ffffff",
        font_color="#2d3436"
    )
    
    net.toggle_physics(False)
    net.force_atlas_2based(
        gravity=-100,
        central_gravity=0.01,
        spring_length=200,
        spring_strength=0.05,
        damping=0.4,
        overlap=0
    )
    
    highlight_set = set()
    if selected_node:
        if trace_mode == "MaterialGenealogy" and G.nodes[selected_node].get("type") == "Material":
            highlight_set.add(selected_node)
            highlight_set.update(nx.ancestors(G, selected_node))
            highlight_set.update(nx.descendants(G, selected_node))
        elif trace_mode != "None":
            highlight_set.add(selected_node)
            if trace_mode in ["Backward", "Bidirectional"]:
                highlight_set.update(nx.ancestors(G, selected_node))
            if trace_mode in ["Forward", "Bidirectional"]:
                highlight_set.update(nx.descendants(G, selected_node))
    
    for node_id, data in G.nodes(data=True):
        opacity = 1.0
        if deviation_only and data.get("result") != "FAIL":
            opacity = 0.3
        if highlight_set and node_id not in highlight_set:
            opacity = 0.3
        
        shape, size, color, border_color, border_width = "dot", 20, "#3498db", "#2c3e50", 2
        
        if data["type"] == "Batch":
            shape, size, color, border_color = "star", 35, "#f39c12", "#d68910"
        elif data["type"] == "Phase":
            shape, size, color, border_color = "triangle", 28, "#2ecc71", "#27ae60"
        elif data["type"] == "PI":
            if data.get("result") == "FAIL":
                shape, size, color, border_color = "box", 25, "#e74c3c", "#c0392b"
            else:
                shape, size, color, border_color = "box", 25, "#9b59b6", "#8e44ad"
        elif data["type"] == "Material":
            shape, size, color, border_color = "ellipse", 22, "#34495e", "#2c3e50"
        
        if node_id == selected_node:
            shape, size, color, border_color, border_width = "diamond", 35, "#f1c40f", "#f39c12", 3
        
        tooltip_lines = [f"<b>{data['label']}</b>", f"Type: {data['type']}"]
        if data.get("result"):
            tooltip_lines.append(f"Result: {data['result']}")
        for k in ["parameters", "limits", "timestamp", "deviation", "product", "status"]:
            if k in data and data[k]:
                if isinstance(data[k], dict):
                    tooltip_lines.append(f"{k}: {json.dumps(data[k], indent=2).replace('\"', '')}")
                else:
                    tooltip_lines.append(f"{k}: {data[k]}")
        tooltip_html = "<br>".join(tooltip_lines)
        
        net.add_node(
            node_id,
            label=data["label"],
            shape=shape,
            size=size,
            color=color,
            opacity=opacity,
            title=tooltip_html,
            borderWidth=border_width,
            borderWidthSelected=border_width * 2,
            borderColor=border_color,
            font={
                "size": 14,
                "face": "Arial",
                "color": "#2d3436",
                "strokeWidth": 0,
                "strokeColor": "#ffffff"
            },
            shadow={
                "enabled": True,
                "color": "rgba(0,0,0,0.15)",
                "size": 5,
                "x": 2,
                "y": 2
            }
        )
    
    for u, v, data_edge in G.edges(data=True):
        edge_color, width, arrows, dashes = "#95a5a6", 2, "to", False
        
        if highlight_set and u in highlight_set and v in highlight_set:
            edge_color, width = "#2c3e50", 4
        
        rel = data_edge.get("relationship", "")
        if rel == "has_phase":
            edge_color, dashes = "#3498db", False
        elif rel == "has_pi":
            edge_color, dashes = "#9b59b6", [5, 5]
        elif rel == "next_phase" or rel == "next_step":
            edge_color, width = "#2ecc71", 3
        elif rel == "consumed_by":
            edge_color, dashes = "#e74c3c", [10, 5]
        elif rel == "produced":
            edge_color, dashes = "#f39c12", [5, 10]
        
        net.add_edge(
            u, v,
            label=data_edge["relationship"],
            color=edge_color,
            width=width,
            arrows=arrows,
            dashes=dashes,
            font={
                "size": 12,
                "align": "middle"
            },
            smooth={
                "type": "cubicBezier",
                "roundness": 0.4
            }
        )
    
    net.set_options("""
    var options = {
      "nodes": {
        "scaling": {
          "min": 10,
          "max": 50,
          "label": {
            "enabled": true,
            "min": 12,
            "max": 20
          }
        }
      },
      "edges": {
        "smooth": {
          "type": "cubicBezier",
          "forceDirection": "horizontal",
          "roundness": 0.4
        },
        "font": {
          "size": 12,
          "align": "middle"
        }
      },
      "physics": {
        "enabled": true,
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
          "gravitationalConstant": -100,
          "centralGravity": 0.01,
          "springLength": 200,
          "springConstant": 0.05,
          "damping": 0.4,
          "avoidOverlap": 1
        },
        "stabilization": {
          "enabled": true,
          "iterations": 500,
          "updateInterval": 25,
          "fit": true
        },
        "timestep": 0.5,
        "adaptiveTimestep": true
      },
      "layout": {
        "improvedLayout": true,
        "hierarchical": {
          "enabled": false
        }
      },
      "interaction": {
        "dragNodes": true,
        "dragView": true,
        "zoomView": true,
        "hover": true,
        "tooltipDelay": 200,
        "multiselect": true
      }
    }
    """)
    
    # FIXED LEGEND HTML WITH CLOSING QUOTES
    legend_html = """
    <div style="
        position: absolute; 
        top: 10px; 
        right: 10px; 
        padding: 12px 15px; 
        font-size: 13px; 
        background-color: rgba(255,255,255,0.95); 
        border-radius: 8px; 
        border: 1px solid #dfe6e9; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        z-index: 1000;
        max-width: 250px;
    ">
        <div style="font-weight: bold; margin-bottom: 8px; color: #2d3436; font-size: 14px;">📊 Legend</div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <div style="width: 12px; height: 12px; background-color: #f39c12; border-radius: 2px; margin-right: 8px;"></div>
            <span>Batch</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <div style="width: 12px; height: 12px; background-color: #2ecc71; border-radius: 2px; margin-right: 8px;"></div>
            <span>Phase</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <div style="width: 12px; height: 12px; background-color: #9b59b6; border-radius: 2px; margin-right: 8px;"></div>
            <span>PI (PASS)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <div style="width: 12px; height: 12px; background-color: #e74c3c; border-radius: 2px; margin-right: 8px;"></div>
            <span>PI (FAIL)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <div style="width: 12px; height: 12px; background-color: #34495e; border-radius: 2px; margin-right: 8px;"></div>
            <span>Material</span>
        </div>
        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #dfe6e9; font-size: 12px; color: #636e72;">
            🔸 Click nodes for details<br>
            🔸 Drag to rearrange<br>
            🔸 Scroll to zoom
        </div>
    </div>
    """
    
    net.save_graph("batch_tree.html")
    
    with open("batch_tree.html", "r") as f:
        html_content = f.read()
    
    html_content = html_content.replace('</body>', f'{legend_html}</body>')
    
    with open("batch_tree.html", "w") as f:
        f.write(html_content)
    
    components.html(open("batch_tree.html", "r").read(), height=750, scrolling=False)
