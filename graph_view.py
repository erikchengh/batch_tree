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

from pyvis.network import Network
import streamlit.components.v1 as components

def render_graph(G, selected_node=None):
    net = Network(
        height="600px",
        width="100%",
        directed=True
    )

    for node_id, data in G.nodes(data=True):
        color = "lightblue"

        if data["type"] == "Batch":
            color = "orange"
        elif data["type"] == "Phase":
            color = "lightgreen"
        elif data["type"] == "PI":
            color = "red" if data.get("result") == "FAIL" else "lightblue"
        elif data["type"] == "Material":
            color = "gray"

        if node_id == selected_node:
            color = "yellow"

        tooltip = "<br>".join(f"{k}: {v}" for k, v in data.items())

        net.add_node(
            node_id,
            label=data["label"],
            color=color,
            title=tooltip
        )

    for u, v, data in G.edges(data=True):
        net.add_edge(
            u,
            v,
            label=data["relationship"]
        )

    net.save_graph("batch_tree.html")
    components.html(
        open("batch_tree.html", "r").read(),
        height=650
    )



