from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx

def render_graph(G, selected_node=None, deviation_only=False, trace_mode="None"):
    # ---------- Network setup ----------
    net = Network(
        height="700px",
        width="100%",
        directed=True,
        bgcolor="#f7f7f7",  # Soft professional background
        font_color="#2c3e50"
    )

    net.barnes_hut(gravity=-20000, central_gravity=0.3, spring_length=200, spring_strength=0.05, damping=0.09)
    net.toggle_physics(True)

    # ---------- Trace calculation ----------
    highlight_set = set()
    if selected_node and trace_mode != "None":
        highlight_set.add(selected_node)
        if trace_mode in ["Backward", "Bidirectional"]:
            highlight_set.update(nx.ancestors(G, selected_node))
        if trace_mode in ["Forward", "Bidirectional"]:
            highlight_set.update(nx.descendants(G, selected_node))

    # ---------- Add nodes ----------
    for node_id, data in G.nodes(data=True):
        opacity = 1.0

        if deviation_only and data.get("result") != "FAIL":
            opacity = 0.1
        if trace_mode != "None" and node_id not in highlight_set:
            opacity = 0.1

        # Node shape & color
        shape = "dot"
        size = 20
        color = "#3498db"  # default

        if data["type"] == "Batch":
            color, size, shape = "#f39c12", 50, "star"
        elif data["type"] == "Phase":
            color, size, shape = "#2ecc71", 35, "triangle"
        elif data["type"] == "PI":
            color = "#e74c3c" if data.get("result") == "FAIL" else "#9b59b6"
            size = 30
            shap


# from pyvis.network import Network
# import streamlit.components.v1 as components
# import networkx as nx

# def render_graph(G, selected_node=None, deviation_only=False, trace_mode="None"):
#     # Modern white background, clean lines
#     net = Network(height="600px", width="100%", directed=True, bgcolor="#ffffff", font_color="#34495e")
#     net.toggle_physics(True)
    
#     # Trace Logic: Calculate the set of nodes to highlight
#     highlight_set = set()
#     if selected_node and trace_mode != "None":
#         highlight_set.add(selected_node)
#         if trace_mode in ["Backward", "Bidirectional"]:
#             highlight_set.update(nx.ancestors(G, selected_node))
#         if trace_mode in ["Forward", "Bidirectional"]:
#             highlight_set.update(nx.descendants(G, selected_node))
    
#     # Physics Options
#     net.set_options("""
#     {
#       "physics": {
#         "forceAtlas2Based": { "gravitationalConstant": -50, "springLength": 80, "springStrength": 0.08 },
#         "solver": "forceAtlas2Based"
#       }
#     }
#     """)

#     for node_id, data in G.nodes(data=True):
#         # Default visibility
#         opacity = 1.0
        
#         # 1. Handle Deviation Mode (Dim non-failures)
#         if deviation_only and data.get("result") != "FAIL":
#             opacity = 0.1
            
#         # 2. Handle Trace Mode (Dim nodes not in path)
#         if trace_mode != "None" and node_id not in highlight_set:
#             opacity = 0.1
            
#         # Node Styling
#         color = "#3498db"
#         size = 25
        
#         if data["type"] == "Batch":
#             color, size = "#f39c12", 35
#         elif data["type"] == "Phase":
#             color = "#2ecc71"
#         elif data["type"] == "PI":
#             color = "#e74c3c" if data.get("result") == "FAIL" else "#9b59b6"
#             size = 30
#         elif data["type"] == "Material":
#             color, size = "#34495e", 20 # Dark Grey for materials

#         if node_id == selected_node:
#             color, size = "#f1c40f", 45 # Yellow Selection

#         net.add_node(
#             node_id,
#             label=data["label"],
#             color=color,
#             size=size,
#             opacity=opacity,
#             title=f"Type: {data['type']}"
#         )

#     for u, v, data in G.edges(data=True):
#         # Edge Logic: Dim edges if they aren't part of the trace
#         edge_color = "#bdc3c7"
#         width = 1
        
#         if trace_mode != "None":
#             if u in highlight_set and v in highlight_set:
#                 edge_color = "#2c3e50" # Dark path
#                 width = 3
#             else:
#                 edge_color = "rgba(200,200,200,0.1)"

#         net.add_edge(u, v, label=data["relationship"], color=edge_color, width=width, arrows="to")

#     net.save_graph("batch_tree.html")
#     components.html(open("batch_tree.html", "r").read(), height=650)
    
# from pyvis.network import Network
# import streamlit.components.v1 as components

# def render_graph(G):
#     net = Network(height="600px", width="100%", directed=True)

#     for node, data in G.nodes(data=True):
#         color = "lightblue"

#         if data["type"] == "Batch":
#             color = "orange"
#         elif data["type"] == "Phase":
#             color = "lightgreen"
#         elif data["type"] == "PI":
#             color = "red" if data.get("result") == "FAIL" else "lightblue"
#         elif data["type"] == "Material":
#             color = "gray"

#         tooltip = "<br>".join(f"{k}: {v}" for k, v in data.items())

#         net.add_node(node, label=data["label"], color=color, title=tooltip)

#     for u, v, data in G.edges(data=True):
#         net.add_edge(u, v, label=data["relationship"])

#     net.save_graph("batch_tree.html")
#     components.html(open("batch_tree.html", "r").read(), height=650)

# from pyvis.network import Network
# import streamlit.components.v1 as components

# def render_graph(G, selected_node=None):
#     net = Network(
#         height="600px",
#         width="100%",
#         directed=True
#     )

#     for node_id, data in G.nodes(data=True):
#         color = "lightblue"

#         if data["type"] == "Batch":
#             color = "orange"
#         elif data["type"] == "Phase":
#             color = "lightgreen"
#         elif data["type"] == "PI":
#             color = "red" if data.get("result") == "FAIL" else "lightblue"
#         elif data["type"] == "Material":
#             color = "gray"

#         if node_id == selected_node:
#             color = "yellow"

#         tooltip = "<br>".join(f"{k}: {v}" for k, v in data.items())

#         net.add_node(
#             node_id,
#             label=data["label"],
#             color=color,
#             title=tooltip
#         )

#     for u, v, data in G.edges(data=True):
#         net.add_edge(
#             u,
#             v,
#             label=data["relationship"]
#         )

#     net.save_graph("batch_tree.html")
#     components.html(
#         open("batch_tree.html", "r").read(),
#         height=650
#     )



