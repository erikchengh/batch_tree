import networkx as nx

def build_batch_graph(data):
    G = nx.DiGraph()

    # Batch
    batch = data["batch"]
    G.add_node(batch["id"], label=f"Batch {batch['id']}", type="Batch",
               product=batch["product"], status=batch["status"])

    # Phases
    prev_phase = None
    for phase in data["phases"]:
        G.add_node(phase["id"], label=phase["name"], type="Phase")
        G.add_edge(batch["id"], phase["id"], relationship="has_phase")
        if prev_phase:
            G.add_edge(prev_phase, phase["id"], relationship="next_phase")
        prev_phase = phase["id"]

    # PIs
    prev_pi = None
    for pi in data["pis"]:
        G.add_node(pi["id"], label=pi["name"], type="PI", result=pi["result"],
                   parameters=pi.get("parameters"), limits=pi.get("limits"),
                   timestamp=pi.get("timestamp"), deviation=pi.get("deviation"))
        G.add_edge(pi["phase"], pi["id"], relationship="has_pi")
        if prev_pi:
            G.add_edge(prev_pi, pi["id"], relationship="next_step")
        prev_pi = pi["id"]

    # Materials
    for mat in data["materials"]:
        mat_id = f"M_{mat['name'].replace(' ','_')}"
        G.add_node(mat_id, label=mat["name"], type="Material")
        if mat["type"] == "consumed":
            G.add_edge(mat_id, mat["pi"], relationship="consumed_by")
        elif mat["type"] == "produced":
            G.add_edge(mat["pi"], mat_id, relationship="produced")

    return G
