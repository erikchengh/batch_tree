import networkx as nx

def build_batch_graph(data):
    G = nx.DiGraph()

    # --- Batch Node ---
    batch = data["batch"]
    G.add_node(
        batch["id"],
        label=f"Batch {batch['id']}",
        type="Batch",
        product=batch["product"],
        status=batch["status"]
    )

    # --- Phases & Sequence ---
    previous_phase_id = None
    for phase in data["phases"]:
        G.add_node(phase["id"], label=phase["name"], type="Phase")
        G.add_edge(batch["id"], phase["id"], relationship="has_phase")
        if previous_phase_id:
            G.add_edge(previous_phase_id, phase["id"], relationship="next_phase")
        previous_phase_id = phase["id"]

    # --- PIs & Sequence ---
    previous_pi_id = None
    for pi in data["pis"]:
        G.add_node(pi["id"], label=pi["name"], type="PI", result=pi["result"])
        G.add_edge(pi["phase"], pi["id"], relationship="has_pi")
        if previous_pi_id:
            G.add_edge(previous_pi_id, pi["id"], relationship="next_step")
        previous_pi_id = pi["id"]

    # --- Materials & Flow ---
    for mat in data["materials"]:
        mat_id = f"M_{mat['name'].replace(' ', '_')}"
        G.add_node(mat_id, label=mat["name"], type="Material")
        if mat["type"] == "consumed":
            G.add_edge(mat_id, mat["pi"], relationship="consumed_by")
        elif mat["type"] == "produced":
            G.add_edge(mat["pi"], mat_id, relationship="produced")

    return G
