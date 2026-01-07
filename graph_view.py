from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx
import json

def render_graph(G, selected_node=None, deviation_only=False, trace_mode="None"):
    net = Network(height="700px", width="100%", directed=True, bgcolor="#f7f7f7", font_color="#2c3e50")
    net.toggle_physics(True)
    net.barnes_hut(gravity=-20000, central_gravity=0.3, spring_length=200, spring_strength=0.05, damping=0.09)

    # Material genealogy / trace
    highlight_set = set()
    if selected_node:
        if trace_mode=="MaterialGenealogy" and G.nodes[selected_node]["type"]=="Material":
            highlight_set.add(selected_node)
            highlight_set.update(nx.ancestors(G, selected_node))
            highlight_set.update(nx.descendants(G, selected_node))
        elif trace_mode!="None":
            highlight_set.add(selected_node)
            if trace_mode in ["Backward","Bidirectional"]:
                highlight_set.update(nx.ancestors(G, selected_node))
            if trace_mode in ["Forward","Bidirectional"]:
                highlight_set.update(nx.descendants(G, selected_node))

    # Nodes
    for node_id, data in G.nodes(data=True):
        opacity = 1.0
        if deviation_only and data.get("result")!="FAIL": opacity=0.1
        if highlight_set and node_id not in highlight_set: opacity=0.1

        shape,size,color="dot",20,"#3498db"
        if data["type"]=="Batch": shape,size,color="star",50,"#f39c12"
        elif data["type"]=="Phase": shape,size,color="triangle",35,"#2ecc71"
        elif data["type"]=="PI": shape,size,color="box",30,"#e74c3c" if data.get("result")=="FAIL" else "#9b59b6"
        elif data["type"]=="Material": shape,size,color="ellipse",25,"#34495e"
        if node_id==selected_node: shape,size,color="diamond",45,"#f1c40f"

        tooltip_lines=[f"<b>{data['label']}</b>", f"Type: {data['type']}"]
        for k in ["parameters","limits","timestamp","deviation"]:
            if k in data and data[k]: tooltip_lines.append(f"{k}: {json.dumps(data[k])}")
        tooltip_html="<br>".join(tooltip_lines)

        net.add_node(node_id,label=data["label"],shape=shape,size=size,color=color,opacity=opacity,title=tooltip_html)

    # Edges
    for u,v,data_edge in G.edges(data=True):
        edge_color,width,arrows="#bdc3c7",2,"to"
        if highlight_set and u in highlight_set and v in highlight_set:
            edge_color,width="#2c3e50",4
        net.add_edge(u,v,label=data_edge["relationship"],color=edge_color,width=width,arrows=arrows)

    # Hierarchical layout
    net.set_options("""
    var options = {
      "layout": { "hierarchical": { "enabled": true, "levelSeparation": 120, "nodeSpacing": 150, "treeSpacing": 200, "direction": "UD", "sortMethod": "hubsize" } },
      "physics": { "enabled": false }
    }
    """)

    # Legend
    legend_html="""
    <div style="padding:10px; font-size:12px; background-color:#ecf0f1; border-radius:5px; border:1px solid #bdc3c7">
    <b>Legend:</b><br>
    ⭐ Batch | 🔺 Phase | ▢ PI | 📦 Material<br>
    ✅ PASS | ❌ FAIL | 💛 Selected<br>
    Arrows = Flow / Sequence
    </div>
    """
    net.add_node("LegendNode",label="",x=-5000,y=-5000,physics=False,shape="html",title=legend_html)
    net.save_graph("batch_tree.html")
    components.html(open("batch_tree.html","r").read(),height=700)
