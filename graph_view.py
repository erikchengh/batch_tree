from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx


def render_graph(G, selected_node=None, trace_mode="None"):
    net = Network(
        height="720px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#263238"
    )

    # -------------------------
    # PAS-X Hierarchical Layout
    # -------------------------
    net.set_options("""
    {
      "layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "UD",
          "sortMethod": "directed",
          "levelSeparation": 140,
          "nodeSpacing": 180,
          "treeSpacing": 220
        }
      },
      "physics": { "enabled": false },
      "edges": { "smooth": false }
    }
    """)

    # -------------------------
    # Trace Logic (Material / Process)
    # -------------------------
    highlight_nodes = set()

    if selected_node:
        highlight_nodes.add(selected_node)

        if trace_mode in ["Backward", "Bidirectional"]:
            highlight_nodes |= nx.ancestors(G, selected_node)

        if trace_mode in ["Forward", "Bidirectional"]:
            highlight_nodes |= nx.descendants(G, selected_node)

    # -------------------------
    # Node Rendering (Pharma Style)
    # -------------------------
    for node_id, data in G.nodes(data=True):

        opacity = 1.0
        if highlight_nodes and node_id not in highlight_nodes:
            opacity = 0.15

        # Default style
        shape = "box"
        size = 25
        color = {"background": "#eceff1", "border": "#607d8b"}

        if data["type"] == "Batch":
            color = {"background": "#e3f2fd", "border": "#1e88e5"}
            size = 35

        elif data["type"] == "Phase":
            color = {"background": "#ede7f6", "border": "#5e35b1"}

        elif data["type"] == "ProcessInstruction":
            if data.get("execution_result") == "FAIL":
                color = {"background": "#fdecea", "border": "#c62828"}
            else:
                color = {"background": "#e8f5e9", "border": "#2e7d32"}

        elif data["type"] == "MaterialLot":
            color = {"background": "#f1f8e9", "border": "#558b2f"}

        if node_id == selected_node:
            color["border"] = "#000000"
            size = 40

        net.add_node(
            node_id,
            label=data["label"],
            shape=shape,
            size=size,
            color=color,
            opacity=opacity
        )

    # -------------------------
    # Edges (Clean & Meaningful)
    # -------------------------
    for u, v, edge in G.edges(data=True):
        edge_color = "#90a4ae"
        width = 2

        if highlight_nodes and u in highlight_nodes and v in highlight_nodes:
            edge_color = "#263238"
            width = 4

        net.add_edge(
            u,
            v,
            arrows="to",
            color=edge_color,
            width=width,
            label=edge["relationship"]
        )

    net.save_graph("batch_tree.html")
    components.html(open("batch_tree.html").read(), height=750)
