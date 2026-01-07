import networkx as nx

def build_batch_graph(data):
    G = nx.DiGraph()

    # 1. Batch Node
    batch = data["batch"]
    G.add_node(
        batch["id"],
        label=f"Batch {batch['id']}",
        type="Batch",
        product=batch["product"],
        status=batch["status"]
    )

    # 2. Phases & Hierarchy
    previous_phase_id = None
    
    for phase in data["phases"]:
        G.add_node(phase["id"], label=phase["name"], type="Phase")
        # Hierarchy: Batch -> Phase
        G.add_edge(batch["id"], phase["id"], relationship="has_phase")
        
        # Sequence: Phase -> Phase (Optional, but helps visual flow)
        if previous_phase_id:
             G.add_edge(previous_phase_id, phase["id"], relationship="next_phase")
        previous_phase_id = phase["id"]

    # 3. Process Instructions (PIs) & Sequence
    previous_pi_id = None
    
    for pi in data["pis"]:
        G.add_node(
            pi["id"],
            label=pi["name"],
            type="PI",
            result=pi["result"]
        )
        # Hierarchy: Phase -> PI
        G.add_edge(pi["phase"], pi["id"], relationship="has_pi")
        
        # Sequence: PI -> PI (The "Time" dimension)
        if previous_pi_id:
            G.add_edge(previous_pi_id, pi["id"], relationship="next_step")
        previous_pi_id = pi["id"]

    # 4. Materials (The "Flow" dimension)
    # Consumed: Material -> PI
    # Produced: PI -> Material
    for mat in data["materials"]:
        mat_id = f"M_{mat['name'].replace(' ', '_')}"
        G.add_node(mat_id, label=mat["name"], type="Material")
        
        if mat["type"] == "consumed":
            G.add_edge(mat_id, mat["pi"], relationship="consumed_by")
        elif mat["type"] == "produced":
            G.add_edge(mat["pi"], mat_id, relationship="produced")

    return G
    
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

# import networkx as nx

# def build_batch_graph(data):
#     G = nx.DiGraph()

#     # Batch
#     batch = data["batch"]
#     G.add_node(
#         batch["id"],
#         label=f"Batch {batch['id']}",
#         type="Batch",
#         product=batch["product"],
#         status=batch["status"]
#     )

#     # Phases
#     for phase in data["phases"]:
#         G.add_node(
#             phase["id"],
#             label=phase["name"],
#             type="Phase"
#         )
#         G.add_edge(
#             batch["id"],
#             phase["id"],
#             relationship="has_phase"
#         )

#     # Process Instructions
#     for pi in data["pis"]:
#         G.add_node(
#             pi["id"],
#             label=pi["name"],
#             type="PI",
#             result=pi["result"]
#         )
#         G.add_edge(
#             pi["phase"],
#             pi["id"],
#             relationship="has_pi"
#         )

#     # Materials
#     for mat in data["materials"]:
#         mat_id = f"M_{mat['name'].replace(' ', '_')}"
#         G.add_node(
#             mat_id,
#             label=mat["name"],
#             type="Material"
#         )
#         G.add_edge(
#             mat["pi"],
#             mat_id,
#             relationship=mat["type"]
#         )

#     return G


