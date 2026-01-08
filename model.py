import networkx as nx


def build_batch_graph(data):
    G = nx.DiGraph()

    # -------------------------
    # Batch (Process Segment Instance)
    # -------------------------
    batch = data["batch"]
    batch_label = (
        f"BATCH: {batch['id']}\n"
        f"PRODUCT: {batch['product']}\n"
        f"STATUS: {batch['status']}"
    )

    G.add_node(
        batch["id"],
        label=batch_label,
        type="Batch",
        isa95_class="ProcessSegmentInstance",
        status=batch["status"]
    )

    # -------------------------
    # Phases (Operations)
    # -------------------------
    previous_phase = None
    for phase in data["phases"]:
        phase_label = (
            f"PHASE {phase['id']}\n"
            f"{phase['name']}"
        )

        G.add_node(
            phase["id"],
            label=phase_label,
            type="Phase",
            isa95_class="Operation"
        )

        G.add_edge(batch["id"], phase["id"], relationship="executes")

        if previous_phase:
            G.add_edge(previous_phase, phase["id"], relationship="operation_sequence")

        previous_phase = phase["id"]

    # -------------------------
    # Process Instructions (PIs)
    # -------------------------
    previous_pi = None
    for pi in data["pis"]:
        pi_label = (
            f"PI {pi['id']}\n"
            f"{pi['name']}\n"
            f"RESULT: {pi['result']}"
        )

        G.add_node(
            pi["id"],
            label=pi_label,
            type="ProcessInstruction",
            isa95_class="ProcessSegmentInstance",
            execution_result=pi["result"],
            timestamp=pi.get("timestamp"),
            deviation=pi.get("deviation")
        )

        G.add_edge(pi["phase"], pi["id"], relationship="contains")

        if previous_pi:
            G.add_edge(previous_pi, pi["id"], relationship="execution_sequence")

        previous_pi = pi["id"]

    # -------------------------
    # Materials (Material Lots)
    # -------------------------
    for mat in data["materials"]:
        material_id = f"M_{mat['name'].replace(' ', '_')}"
        material_label = (
            f"MATERIAL LOT\n"
            f"{mat['name']}"
        )

        G.add_node(
            material_id,
            label=material_label,
            type="MaterialLot",
            isa95_class="MaterialLot"
        )

        if mat["type"] == "consumed":
            G.add_edge(material_id, mat["pi"], relationship="consumed_by")

        elif mat["type"] == "produced":
            G.add_edge(mat["pi"], material_id, relationship="produces")

    return G
