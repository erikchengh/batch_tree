import networkx as nx
import pandas as pd
from data_mock import generate_batch_data

def build_batch_genealogy_graph():
    """Build a directed graph of batch genealogy relationships"""
    data = generate_batch_data()
    G = nx.DiGraph()
    
    # Add all batches as nodes
    for _, batch in data["batches"].iterrows():
        # Determine batch type
        batch_id = str(batch["batch_id"])  # Ensure it's a string
        batch_type = (
            "Raw Material" if batch_id.startswith("RM-") else
            "Intermediate" if batch_id.startswith("INT-") else
            "Finished Product" if batch_id.startswith("FP-") else
            "Unknown"
        )
        
        # Node styling based on batch type
        color = {
            "Raw Material": "#3498db",      # Blue
            "Intermediate": "#9b59b6",      # Purple
            "Finished Product": "#2ecc71",   # Green
            "Unknown": "#95a5a6"            # Gray
        }.get(batch_type, "#95a5a6")
        
        shape = {
            "Raw Material": "ellipse",
            "Intermediate": "box",
            "Finished Product": "star",
            "Unknown": "circle"
        }.get(batch_type, "circle")
        
        size = {
            "Raw Material": 25,
            "Intermediate": 30,
            "Finished Product": 35,
            "Unknown": 20
        }.get(batch_type, 20)
        
        # Create label (show batch ID and material name)
        material = str(batch.get("material", "Unknown"))
        label = f"{batch_id}\n{material[:20]}{'...' if len(material) > 20 else ''}"
        
        G.add_node(
            batch_id,
            label=label,
            type=batch_type,
            material=material,
            product=str(batch.get("product", "")),
            quantity=f"{batch.get('quantity', 'N/A')} {batch.get('unit', '')}",
            status=str(batch.get("status", "")),
            quality=str(batch.get("quality", "")),
            color=color,
            shape=shape,
            size=size,
            batch_id=batch_id  # Also store as attribute for reference
        )
    
    # Add genealogy relationships as edges
    for _, rel in data["genealogy"].iterrows():
        parent = str(rel["parent_batch"])
        child = str(rel["child_batch"])
        
        # Only add edge if both nodes exist
        if parent in G.nodes and child in G.nodes:
            edge_label = str(rel["relationship"])
            if pd.notna(rel.get("quantity")):
                edge_label += f"\n{rel['quantity']} {rel.get('unit', '')}"
            
            # Edge styling based on relationship type
            edge_color = {
                "consumed_by": "#e74c3c",    # Red
                "precedes": "#3498db",       # Blue
                "coated_with": "#f39c12",    # Orange
            }.get(str(rel["relationship"]), "#95a5a6")
            
            G.add_edge(
                parent,
                child,
                label=edge_label,
                relationship=str(rel["relationship"]),
                quantity=rel.get("quantity"),
                unit=rel.get("unit"),
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
                "Batch ID": str(item["parent_batch"]),
                "Material": str(batch_info["material"]),
                "Quantity": item["quantity"],
                "Unit": str(item["unit"]),
                "Type": (
                    "Raw Material" if str(item["parent_batch"]).startswith("RM-") else
                    "Intermediate" if str(item["parent_batch"]).startswith("INT-") else
                    "Component"
                ),
                "Status": str(batch_info.get("quality", "N/A"))
            })
    
    return pd.DataFrame(bom_list)

def get_product_list():
    """Get list of all finished products"""
    data = generate_batch_data()
    finished_df = data["finished"].copy()
    
    # Ensure batch_id is string
    finished_df["batch_id"] = finished_df["batch_id"].astype(str)
    
    return finished_df[["batch_id", "material", "quantity", "unit", "manufacturing_date", "expiry"]]
