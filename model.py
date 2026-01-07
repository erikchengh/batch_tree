# import networkx as nx

# def build_batch_graph(data):
#     G = nx.DiGraph()

#     # Batch
#     batch = data["batch"]
#     G.add_node(
#         batch["id"],
#         label=f'Batch {batch["id"]}',
#         type="Batch",
#         status=batch["status"],
#         product=batch["product"]
#     )

#     # Phases
#     for p in data["phases"]:
#         G.add_node(p["id"], label=p["name"], type="Phase")
#         G.add_edge(batch["id"], p["id"], relationship="has_phase")

#     # PIs
#     for pi in data["pis"]:
#         G.add_node(
#             pi["id"],
#             label=pi["name"],
#             type="PI",
#             result=pi["result"]
#         )
#         G.add_edge(pi["phase"], pi["id"], relationship="has_pi")

#     # Materials
#     for m in data["materials"]:
#         mat_id = f'M_{m["name"].replace(" ", "_")}'
#         G.add_node(mat_id, label=m["name"], type="Material")
#         G.add_edge(m["pi"], mat_id, relationship=m["type"])

#     return G

import networkx as nx

def build_batch_graph(data):
    G = nx.DiGraph()

    # Batch
    batch = data["batch"]
    G.add_node(
        batch["id"],
        label=f"Batch {batch['id']}",
        type="Batch",
        product=batch["product"],
        status=batch["status"]
    )

    # Phases
    for phase in data["phases"]:
        G.add_node(
            phase["id"],
            label=phase["name"],
            type="Phase"
        )
        G.add_edge(
            batch["id"],
            phase["id"],
            relationship="has_phase"
        )

    # Process Instructions
    for pi in data["pis"]:
        G.add_node(
            pi["id"],
            label=pi["name"],
            type="PI",
            result=pi["result"]
        )
        G.add_edge(
            pi["phase"],
            pi["id"],
            relationship="has_pi"
        )

    # Materials
    for mat in data["materials"]:
        mat_id = f"M_{mat['name'].replace(' ', '_')}"
        G.add_node(
            mat_id,
            label=mat["name"],
            type="Material"
        )
        G.add_edge(
            mat["pi"],
            mat_id,
            relationship=mat["type"]
        )

    return G


