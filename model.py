import pandas as pd
import networkx as nx
from datetime import datetime, timedelta

def create_sample_data():
    """Create professional pharmaceutical batch data"""
    
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
    ]
    
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
    
    all_batches = raw_materials + finished_products
    
    df = pd.DataFrame(all_batches)
    
    # Add dates
    start_date = datetime(2024, 1, 1)
    for i in range(len(df)):
        df.loc[i, 'manufacturing_date'] = (start_date + timedelta(days=i*7)).strftime('%Y-%m-%d')
    
    return df

def build_batch_genealogy_graph():
    """
    Build pharmaceutical batch tree with direct connections
    """
    data = create_sample_data()
    
    G = nx.DiGraph()
    
    # Add all nodes
    for _, row in data.iterrows():
        node_attrs = row.to_dict()
        batch_id = node_attrs.pop('batch_id')
        G.add_node(batch_id, **node_attrs)
    
    # Create DIRECT connections (skip intermediates)
    # FP-TAB-001 connections
    connections = [
        ("RM-API-001", "FP-TAB-001", 50, "kg"),
        ("RM-EXC-001", "FP-TAB-001", 40, "kg"),
        ("RM-EXC-002", "FP-TAB-001", 10, "kg"),
        ("RM-EXC-003", "FP-TAB-001", 1, "kg"),
        ("RM-SOL-001", "FP-TAB-001", 20, "L"),
        
        # FP-TAB-002 connections
        ("RM-API-001", "FP-TAB-002", 75, "kg"),
        ("RM-EXC-001", "FP-TAB-002", 60, "kg"),
        ("RM-EXC-002", "FP-TAB-002", 15, "kg"),
        ("RM-EXC-003", "FP-TAB-002", 1.5, "kg"),
        
        # FP-TAB-003 connections
        ("RM-API-002", "FP-TAB-003", 40, "kg"),
        ("RM-EXC-001", "FP-TAB-003", 35, "kg"),
        ("RM-EXC-002", "FP-TAB-003", 7.5, "kg"),
        
        # FP-CAP-001 connections
        ("RM-API-001", "FP-CAP-001", 25, "kg"),
        ("RM-EXC-001", "FP-CAP-001", 30, "kg"),
    ]
    
    for source, target, quantity, unit in connections:
        G.add_edge(source, target, 
                  relationship="used_in",
                  quantity=quantity,
                  unit=unit)
    
    print(f"✅ Built pharmaceutical tree with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    return G, data

def get_bom_list(batch_id):
    """Get Bill of Materials for a batch"""
    bom_data = []
    
    sample_boms = {
        "FP-TAB-001": [
            {"material": "Paracetamol API", "batch_id": "RM-API-001", "quantity": 50, "unit": "kg", "type": "Raw Material"},
            {"material": "Microcrystalline Cellulose", "batch_id": "RM-EXC-001", "quantity": 40, "unit": "kg", "type": "Raw Material"},
            {"material": "Croscarmellose Sodium", "batch_id": "RM-EXC-002", "quantity": 10, "unit": "kg", "type": "Raw Material"},
            {"material": "Magnesium Stearate", "batch_id": "RM-EXC-003", "quantity": 1, "unit": "kg", "type": "Raw Material"},
        ],
        "FP-TAB-002": [
            {"material": "Paracetamol API", "batch_id": "RM-API-001", "quantity": 75, "unit": "kg", "type": "Raw Material"},
            {"material": "Microcrystalline Cellulose", "batch_id": "RM-EXC-001", "quantity": 60, "unit": "kg", "type": "Raw Material"},
            {"material": "Croscarmellose Sodium", "batch_id": "RM-EXC-002", "quantity": 15, "unit": "kg", "type": "Raw Material"},
            {"material": "Magnesium Stearate", "batch_id": "RM-EXC-003", "quantity": 1.5, "unit": "kg", "type": "Raw Material"},
        ],
        "FP-TAB-003": [
            {"material": "Amoxicillin API", "batch_id": "RM-API-002", "quantity": 40, "unit": "kg", "type": "Raw Material"},
            {"material": "Microcrystalline Cellulose", "batch_id": "RM-EXC-001", "quantity": 35, "unit": "kg", "type": "Raw Material"},
            {"material": "Croscarmellose Sodium", "batch_id": "RM-EXC-002", "quantity": 7.5, "unit": "kg", "type": "Raw Material"},
        ]
    }
    
    if batch_id in sample_boms:
        bom_data = sample_boms[batch_id]
    
    return pd.DataFrame(bom_data)

def get_product_list():
    """Get list of products"""
    products = [
        {"product_name": "Paracetamol 500mg", "dosage_form": "Tablet", "strength": "500mg"},
        {"product_name": "Amoxicillin 250mg", "dosage_form": "Tablet", "strength": "250mg"},
        {"product_name": "Vitamin C 500mg", "dosage_form": "Capsule", "strength": "500mg"},
    ]
    return pd.DataFrame(products)

def analyze_graph(G):
    """Analyze graph statistics"""
    return {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "raw_materials": len([n for n in G.nodes() if G.nodes[n].get("type") == "Raw Material"]),
        "finished_products": len([n for n in G.nodes() if G.nodes[n].get("type") == "Finished Product"]),
    }
