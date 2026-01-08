import pandas as pd
import networkx as nx
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample pharmaceutical batch data for tree demonstration"""
    
    # Sample raw materials
    raw_materials = [
        {"batch_id": "RM-API-001", "type": "Raw Material", "material": "Paracetamol API", "quantity": 100, "unit": "kg", 
         "status": "Approved", "quality": "A", "lot": "LOT-API-2024-001", "manufacturer": "API Corp"},
        {"batch_id": "RM-EXC-001", "type": "Raw Material", "material": "Microcrystalline Cellulose", "quantity": 200, "unit": "kg", 
         "status": "Approved", "quality": "A", "lot": "LOT-EXC-2024-001", "manufacturer": "Excipient Co"},
        {"batch_id": "RM-EXC-002", "type": "Raw Material", "material": "Croscarmellose Sodium", "quantity": 50, "unit": "kg", 
         "status": "Approved", "quality": "A", "lot": "LOT-EXC-2024-002", "manufacturer": "Excipient Co"},
        {"batch_id": "RM-EXC-003", "type": "Raw Material", "material": "Magnesium Stearate", "quantity": 10, "unit": "kg", 
         "status": "Approved", "quality": "A", "lot": "LOT-EXC-2024-003", "manufacturer": "Excipient Co"},
        {"batch_id": "RM-SOL-001", "type": "Raw Material", "material": "Purified Water", "quantity": 500, "unit": "L", 
         "status": "Approved", "quality": "A", "lot": "LOT-SOL-2024-001", "manufacturer": "Water Co"},
        {"batch_id": "RM-API-002", "type": "Raw Material", "material": "Amoxicillin API", "quantity": 80, "unit": "kg", 
         "status": "Approved", "quality": "A", "lot": "LOT-API-2024-002", "manufacturer": "API Corp"},
        {"batch_id": "RM-EXC-004", "type": "Raw Material", "material": "Lactose Monohydrate", "quantity": 150, "unit": "kg", 
         "status": "Approved", "quality": "A", "lot": "LOT-EXC-2024-004", "manufacturer": "Excipient Co"},
    ]
    
    # Sample finished products
    finished_products = [
        {"batch_id": "FP-TAB-001", "type": "Finished Product", "material": "Paracetamol 500mg Tablets", "quantity": 100000, "unit": "tablets",
         "status": "Released", "quality": "A", "product": "Paracetamol 500mg", "expiry_date": "2025-12-31"},
        {"batch_id": "FP-TAB-002", "type": "Finished Product", "material": "Paracetamol 500mg Tablets", "quantity": 150000, "unit": "tablets",
         "status": "Released", "quality": "A", "product": "Paracetamol 500mg", "expiry_date": "2025-12-31"},
        {"batch_id": "FP-TAB-003", "type": "Finished Product", "material": "Amoxicillin 250mg Tablets", "quantity": 80000, "unit": "tablets",
         "status": "Released", "quality": "A", "product": "Amoxicillin 250mg", "expiry_date": "2025-10-31"},
        {"batch_id": "FP-CAP-001", "type": "Finished Product", "material": "Vitamin C 500mg Capsules", "quantity": 50000, "unit": "capsules",
         "status": "Released", "quality": "A", "product": "Vitamin C 500mg", "expiry_date": "2025-09-30"},
    ]
    
    # Combine all data
    all_batches = raw_materials + finished_products
    
    # Convert to DataFrame
    df = pd.DataFrame(all_batches)
    
    # Add manufacturing dates
    start_date = datetime(2024, 1, 1)
    for i in range(len(df)):
        df.loc[i, 'manufacturing_date'] = (start_date + timedelta(days=i*7)).strftime('%Y-%m-%d')
    
    return df

def build_batch_genealogy_graph():
    """
    Build a pharmaceutical batch tree
    
    Returns:
        G: NetworkX DiGraph with batch genealogy
        data: DataFrame containing all batch data
    """
    
    # Create sample data
    data = create_sample_data()
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes with attributes
    for _, row in data.iterrows():
        node_attrs = row.to_dict()
        # Remove batch_id from attributes (it's the node identifier)
        batch_id = node_attrs.pop('batch_id')
        G.add_node(batch_id, **node_attrs)
    
    # Create tree structure: Raw Materials -> Finished Products
    # FP-TAB-001 uses RM-API-001, RM-EXC-001, RM-EXC-002, RM-EXC-003
    G.add_edge("RM-API-001", "FP-TAB-001", relationship="used_in", quantity=50, unit="kg")
    G.add_edge("RM-EXC-001", "FP-TAB-001", relationship="used_in", quantity=40, unit="kg")
    G.add_edge("RM-EXC-002", "FP-TAB-001", relationship="used_in", quantity=10, unit="kg")
    G.add_edge("RM-EXC-003", "FP-TAB-001", relationship="used_in", quantity=1, unit="kg")
    G.add_edge("RM-SOL-001", "FP-TAB-001", relationship="used_in", quantity=20, unit="L")
    
    # FP-TAB-002 uses RM-API-001, RM-EXC-001, RM-EXC-002, RM-EXC-003
    G.add_edge("RM-API-001", "FP-TAB-002", relationship="used_in", quantity=75, unit="kg")
    G.add_edge("RM-EXC-001", "FP-TAB-002", relationship="used_in", quantity=60, unit="kg")
    G.add_edge("RM-EXC-002", "FP-TAB-002", relationship="used_in", quantity=15, unit="kg")
    G.add_edge("RM-EXC-003", "FP-TAB-002", relationship="used_in", quantity=1.5, unit="kg")
    
    # FP-TAB-003 uses RM-API-002, RM-EXC-004, RM-EXC-002
    G.add_edge("RM-API-002", "FP-TAB-003", relationship="used_in", quantity=40, unit="kg")
    G.add_edge("RM-EXC-004", "FP-TAB-003", relationship="used_in", quantity=35, unit="kg")
    G.add_edge("RM-EXC-002", "FP-TAB-003", relationship="used_in", quantity=7.5, unit="kg")
    
    # FP-CAP-001 uses RM-API-001, RM-EXC-001
    G.add_edge("RM-API-001", "FP-CAP-001", relationship="used_in", quantity=25, unit="kg")
    G.add_edge("RM-EXC-001", "FP-CAP-001", relationship="used_in", quantity=30, unit="kg")
    
    print(f"✅ Tree built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    return G, data

def get_bom_list(batch_id):
    """
    Get Bill of Materials for a specific batch
    """
    bom_columns = ["material", "batch_id", "quantity", "unit", "type", "status"]
    bom_data = []
    
    sample_boms = {
        "FP-TAB-001": [
            {"material": "Paracetamol API", "batch_id": "RM-API-001", "quantity": 50, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Microcrystalline Cellulose", "batch_id": "RM-EXC-001", "quantity": 40, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Croscarmellose Sodium", "batch_id": "RM-EXC-002", "quantity": 10, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Magnesium Stearate", "batch_id": "RM-EXC-003", "quantity": 1, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Purified Water", "batch_id": "RM-SOL-001", "quantity": 20, "unit": "L", "type": "Raw Material", "status": "Approved"},
        ],
        "FP-TAB-002": [
            {"material": "Paracetamol API", "batch_id": "RM-API-001", "quantity": 75, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Microcrystalline Cellulose", "batch_id": "RM-EXC-001", "quantity": 60, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Croscarmellose Sodium", "batch_id": "RM-EXC-002", "quantity": 15, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Magnesium Stearate", "batch_id": "RM-EXC-003", "quantity": 1.5, "unit": "kg", "type": "Raw Material", "status": "Approved"},
        ],
        "FP-TAB-003": [
            {"material": "Amoxicillin API", "batch_id": "RM-API-002", "quantity": 40, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Lactose Monohydrate", "batch_id": "RM-EXC-004", "quantity": 35, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Croscarmellose Sodium", "batch_id": "RM-EXC-002", "quantity": 7.5, "unit": "kg", "type": "Raw Material", "status": "Approved"},
        ],
        "FP-CAP-001": [
            {"material": "Paracetamol API", "batch_id": "RM-API-001", "quantity": 25, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Microcrystalline Cellulose", "batch_id": "RM-EXC-001", "quantity": 30, "unit": "kg", "type": "Raw Material", "status": "Approved"},
        ]
    }
    
    if batch_id in sample_boms:
        bom_data = sample_boms[batch_id]
    
    return pd.DataFrame(bom_data)

def get_product_list():
    """
    Get list of all finished products
    """
    products = [
        {"product_name": "Paracetamol 500mg", "dosage_form": "Tablet", "strength": "500mg", "therapeutic_category": "Analgesic"},
        {"product_name": "Amoxicillin 250mg", "dosage_form": "Tablet", "strength": "250mg", "therapeutic_category": "Antibiotic"},
        {"product_name": "Vitamin C 500mg", "dosage_form": "Capsule", "strength": "500mg", "therapeutic_category": "Vitamin"},
    ]
    
    return pd.DataFrame(products)

def analyze_graph(G):
    """
    Analyze the graph and return statistics
    """
    stats = {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "raw_materials": len([n for n in G.nodes() if G.nodes[n].get("type") == "Raw Material"]),
        "finished_products": len([n for n in G.nodes() if G.nodes[n].get("type") == "Finished Product"]),
    }
    
    return stats
