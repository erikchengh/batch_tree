import networkx as nx
import pandas as pd
from data_mock import generate_batch_data

def build_batch_genealogy_graph(target_batch_id=None):
    """Build a directed graph of batch genealogy relationships"""
    data = generate_batch_data()
    G = nx.DiGraph()
    
    # Add all batches as nodes
    for _, batch in data["batches"].iterrows():
        batch_type = (
            "Raw Material" if batch["batch_id"].startswith("RM-") else
            "Intermediate" if batch["batch_id"].startswith("INT-") else
            "Finished Product"
        )
        
        # Node styling based on batch type
        color = {
            "Raw Material": "#3498db",      # Blue
            "Intermediate": "#9b59b6",      # Purple
            "Finished Product": "#2ecc71"   # Green
        }.get(batch_type, "#95a5a6")
        
        shape = {
            "Raw Material": "ellipse",
            "Intermediate": "box",
            "Finished Product": "star"
        }.get(batch_type, "circle")
        
        size = {
            "Raw Material": 20,
            "Intermediate": 25,
            "Finished Product": 35
        }.get(batch_type, 20)
        
        G.add_node(
            batch["batch_id"],
            label=f"{batch['batch_id']}\n{batch['material']}",
            type=batch_type,
            material=batch["material"],
            product=batch.get("product", ""),
            quantity=f"{batch['quantity']} {batch['unit']}",
            status=batch.get("status", ""),
            quality=batch.get("quality", ""),
            color=color,
            shape=shape,
            size=size
        )
    
    # Add genealogy relationships as edges
    for _, rel in data["genealogy"].iterrows():
        edge_label = rel["relationship"]
        if rel["quantity"]:
            edge_label += f"\n{rel['quantity']} {rel['unit']}"
        
        # Edge styling based on relationship type
        edge_color = {
            "consumed_by": "#e74c3c",    # Red
            "precedes": "#3498db",       # Blue
            "coated_with": "#f39c12",    # Orange
        }.get(rel["relationship"], "#95a5a6")
        
        G.add_edge(
            rel["parent_batch"],
            rel["child_batch"],
            label=edge_label,
            relationship=rel["relationship"],
            quantity=rel["quantity"],
            unit=rel["unit"],
            color=edge_color,
            width=2
        )
    
    return G, data

def get_bom_list(batch_id):
    """Get Bill of Materials for a specific batch"""
    data = generate_batch_data()
    
    # Find all materials consumed by this batch
    bom = data["genealogy"][data["genealogy"]["child_batch"] == batch_id]
    
    if bom.empty:
        return pd.DataFrame()  # Empty DataFrame
    
    # Get details of each consumed material
    bom_list = []
    for _, item in bom.iterrows():
        parent_batch = data["batches"][data["batches"]["batch_id"] == item["parent_batch"]]
        if not parent_batch.empty:
            batch_info = parent_batch.iloc[0]
            bom_list.append({
                "Batch ID": item["parent_batch"],
                "Material": batch_info["material"],
                "Quantity": item["quantity"],
                "Unit": item["unit"],
                "Type": (
                    "Raw Material" if item["parent_batch"].startswith("RM-") else
                    "Intermediate" if item["parent_batch"].startswith("INT-") else
                    "Component"
                ),
                "Status": batch_info.get("quality", "N/A")
            })
    
    return pd.DataFrame(bom_list)

def get_product_list():
    """Get list of all finished products"""
    data = generate_batch_data()
    return data["finished"][["batch_id", "material", "quantity", "unit", "manufacturing_date", "expiry"]]

# In build_batch_genealogy_graph function:
def build_batch_genealogy_graph():
    G = nx.DiGraph()
    
    # Add nodes like this:
    G.add_node(
        batch["batch_id"],
        label=f"{batch['batch_id']}\n{batch['material']}",  # REQUIRED
        type=batch_type,  # REQUIRED: "Raw Material", "Intermediate", or "Finished Product"
        material=batch["material"],
        product=batch.get("product", ""),
        quantity=f"{batch['quantity']} {batch['unit']}",
        status=batch.get("status", ""),
        quality=batch.get("quality", ""),
        color=color,        # REQUIRED for coloring
        shape=shape,        # REQUIRED: "ellipse", "box", or "star"
        size=size           # REQUIRED: 20, 25, or 35
    )
    
    return G, data
