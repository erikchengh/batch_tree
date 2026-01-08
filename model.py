import pandas as pd
import networkx as nx
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample pharmaceutical batch data for demonstration"""
    
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
    ]
    
    # Sample intermediates
    intermediates = [
        {"batch_id": "INT-BLEND-001", "type": "Intermediate", "material": "Paracetamol Blend", "quantity": 150, "unit": "kg",
         "status": "In Progress", "quality": "A", "product": "Paracetamol 500mg"},
        {"batch_id": "INT-GRAN-001", "type": "Intermediate", "material": "Wet Granulation", "quantity": 160, "unit": "kg",
         "status": "In Progress", "quality": "A", "product": "Paracetamol 500mg"},
        {"batch_id": "INT-BLEND-002", "type": "Intermediate", "material": "Antibiotic Blend", "quantity": 120, "unit": "kg",
         "status": "In Progress", "quality": "A", "product": "Antibiotic 250mg"},
        {"batch_id": "INT-SOL-001", "type": "Intermediate", "material": "Coating Solution", "quantity": 80, "unit": "L",
         "status": "Ready", "quality": "A", "product": "Film Coating"},
    ]
    
    # Sample finished products
    finished_products = [
        {"batch_id": "FP-TAB-001", "type": "Finished Product", "material": "Paracetamol 500mg Tablets", "quantity": 100000, "unit": "tablets",
         "status": "Released", "quality": "A", "product": "Paracetamol 500mg", "expiry_date": "2025-12-31"},
        {"batch_id": "FP-TAB-002", "type": "Finished Product", "material": "Paracetamol 500mg Tablets", "quantity": 150000, "unit": "tablets",
         "status": "Released", "quality": "A", "product": "Paracetamol 500mg", "expiry_date": "2025-12-31"},
        {"batch_id": "FP-TAB-003", "type": "Finished Product", "material": "Antibiotic 250mg Tablets", "quantity": 80000, "unit": "tablets",
         "status": "Released", "quality": "A", "product": "Antibiotic 250mg", "expiry_date": "2025-10-31"},
        {"batch_id": "FP-CAP-001", "type": "Finished Product", "material": "Vitamin C 500mg Capsules", "quantity": 50000, "unit": "capsules",
         "status": "Released", "quality": "A", "product": "Vitamin C 500mg", "expiry_date": "2025-09-30"},
    ]
    
    # Combine all data
    all_batches = raw_materials + intermediates + finished_products
    
    # Convert to DataFrame
    df = pd.DataFrame(all_batches)
    
    # Add manufacturing dates
    start_date = datetime(2024, 1, 1)
    for i in range(len(df)):
        df.loc[i, 'manufacturing_date'] = (start_date + timedelta(days=i*7)).strftime('%Y-%m-%d')
    
    return df

def build_batch_genealogy_graph():
    """
    Build a pharmaceutical batch genealogy graph
    
    Returns:
        G: NetworkX DiGraph with batch genealogy
        data: DataFrame containing all batch data
    """
    
    # Create or load your data
    data = create_sample_data()  # Replace with your actual data loading
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes with attributes
    for _, row in data.iterrows():
        node_attrs = row.to_dict()
        # Remove batch_id from attributes (it's the node identifier)
        batch_id = node_attrs.pop('batch_id')
        G.add_node(batch_id, **node_attrs)
    
    # Define the relationships (edges) between batches
    # This is where you define how materials flow through the process
    
    # Raw Materials -> Intermediates (consumed_by relationships)
    raw_to_intermediate = [
        ("RM-API-001", "INT-BLEND-001", {"relationship": "consumed_by", "quantity": 50, "unit": "kg"}),
        ("RM-EXC-001", "INT-BLEND-001", {"relationship": "consumed_by", "quantity": 80, "unit": "kg"}),
        ("RM-EXC-002", "INT-BLEND-001", {"relationship": "consumed_by", "quantity": 20, "unit": "kg"}),
        ("RM-EXC-003", "INT-BLEND-001", {"relationship": "consumed_by", "quantity": 2, "unit": "kg"}),
        ("RM-SOL-001", "INT-BLEND-001", {"relationship": "consumed_by", "quantity": 40, "unit": "L"}),
        ("RM-API-001", "INT-BLEND-002", {"relationship": "consumed_by", "quantity": 40, "unit": "kg"}),
        ("RM-EXC-001", "INT-BLEND-002", {"relationship": "consumed_by", "quantity": 70, "unit": "kg"}),
        ("RM-EXC-002", "INT-BLEND-002", {"relationship": "consumed_by", "quantity": 15, "unit": "kg"}),
    ]
    
    # Intermediates -> Other Intermediates (produces relationships)
    intermediate_to_intermediate = [
        ("INT-BLEND-001", "INT-GRAN-001", {"relationship": "produces", "quantity": 150, "unit": "kg"}),
    ]
    
    # Intermediates -> Finished Products (produces relationships)
    intermediate_to_finished = [
        ("INT-GRAN-001", "FP-TAB-001", {"relationship": "produces", "quantity": 100000, "unit": "tablets"}),
        ("INT-GRAN-001", "FP-TAB-002", {"relationship": "produces", "quantity": 150000, "unit": "tablets"}),
        ("INT-BLEND-002", "FP-TAB-003", {"relationship": "produces", "quantity": 80000, "unit": "tablets"}),
        ("INT-SOL-001", "FP-TAB-001", {"relationship": "coated_with", "quantity": 20, "unit": "L"}),
        ("INT-SOL-001", "FP-TAB-002", {"relationship": "coated_with", "quantity": 30, "unit": "L"}),
        ("INT-SOL-001", "FP-TAB-003", {"relationship": "coated_with", "quantity": 15, "unit": "L"}),
    ]
    
    # Add all edges to the graph
    all_edges = raw_to_intermediate + intermediate_to_intermediate + intermediate_to_finished
    
    for source, target, attrs in all_edges:
        G.add_edge(source, target, **attrs)
    
    # Add some additional random relationships for complexity
    additional_relationships = [
        ("RM-API-001", "INT-SOL-001", {"relationship": "consumed_by", "quantity": 5, "unit": "kg"}),
        ("RM-SOL-001", "INT-SOL-001", {"relationship": "consumed_by", "quantity": 75, "unit": "L"}),
        ("RM-EXC-001", "FP-CAP-001", {"relationship": "consumed_by", "quantity": 30, "unit": "kg"}),
    ]
    
    for source, target, attrs in additional_relationships:
        if source in G.nodes() and target in G.nodes():
            G.add_edge(source, target, **attrs)
    
    # Calculate some statistics for the user
    print(f"✅ Graph built successfully with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Print sample nodes for debugging
    print("\nSample nodes:")
    for i, node in enumerate(list(G.nodes())[:5]):
        print(f"  {node}: {G.nodes[node].get('type', 'Unknown')} - {G.nodes[node].get('material', 'No material')}")
    
    return G, data

def get_bom_list(batch_id):
    """
    Get Bill of Materials for a specific batch
    
    Args:
        batch_id: ID of the batch
        
    Returns:
        DataFrame with BOM information
    """
    
    # Create empty DataFrame with appropriate columns
    bom_columns = ["material", "batch_id", "quantity", "unit", "type", "status"]
    bom_data = []
    
    # This function would typically query the graph to find upstream materials
    # For now, return a sample BOM based on the batch_id
    
    sample_boms = {
        "FP-TAB-001": [
            {"material": "Paracetamol API", "batch_id": "RM-API-001", "quantity": 25, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Microcrystalline Cellulose", "batch_id": "RM-EXC-001", "quantity": 40, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Croscarmellose Sodium", "batch_id": "RM-EXC-002", "quantity": 10, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Magnesium Stearate", "batch_id": "RM-EXC-003", "quantity": 1, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Purified Water", "batch_id": "RM-SOL-001", "quantity": 20, "unit": "L", "type": "Raw Material", "status": "Approved"},
        ],
        "FP-TAB-002": [
            {"material": "Paracetamol API", "batch_id": "RM-API-001", "quantity": 37.5, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Microcrystalline Cellulose", "batch_id": "RM-EXC-001", "quantity": 60, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Croscarmellose Sodium", "batch_id": "RM-EXC-002", "quantity": 15, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Magnesium Stearate", "batch_id": "RM-EXC-003", "quantity": 1.5, "unit": "kg", "type": "Raw Material", "status": "Approved"},
        ],
        "FP-TAB-003": [
            {"material": "Antibiotic API", "batch_id": "RM-API-001", "quantity": 20, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Microcrystalline Cellulose", "batch_id": "RM-EXC-001", "quantity": 35, "unit": "kg", "type": "Raw Material", "status": "Approved"},
            {"material": "Croscarmellose Sodium", "batch_id": "RM-EXC-002", "quantity": 7.5, "unit": "kg", "type": "Raw Material", "status": "Approved"},
        ],
    }
    
    if batch_id in sample_boms:
        bom_data = sample_boms[batch_id]
    
    return pd.DataFrame(bom_data)

def get_product_list():
    """
    Get list of all finished products
    
    Returns:
        DataFrame with product information
    """
    
    # This would typically query a database or the graph
    # For now, return a sample product list
    
    products = [
        {"product_name": "Paracetamol 500mg", "dosage_form": "Tablet", "strength": "500mg", "therapeutic_category": "Analgesic"},
        {"product_name": "Antibiotic 250mg", "dosage_form": "Tablet", "strength": "250mg", "therapeutic_category": "Antibiotic"},
        {"product_name": "Vitamin C 500mg", "dosage_form": "Capsule", "strength": "500mg", "therapeutic_category": "Vitamin"},
    ]
    
    return pd.DataFrame(products)

def analyze_graph(G):
    """
    Analyze the graph and return statistics
    
    Args:
        G: NetworkX graph
        
    Returns:
        Dictionary with graph statistics
    """
    
    stats = {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "raw_materials": len([n for n in G.nodes() if G.nodes[n].get("type") == "Raw Material"]),
        "intermediates": len([n for n in G.nodes() if G.nodes[n].get("type") == "Intermediate"]),
        "finished_products": len([n for n in G.nodes() if G.nodes[n].get("type") == "Finished Product"]),
        "is_connected": nx.is_weakly_connected(G),
    }
    
    return stats

if __name__ == "__main__":
    # Test the functions
    print("Testing model functions...")
    
    # Build graph
    G, data = build_batch_genealogy_graph()
    
    # Analyze graph
    stats = analyze_graph(G)
    print(f"\nGraph Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get BOM for a sample product
    print(f"\nBOM for FP-TAB-001:")
    bom = get_bom_list("FP-TAB-001")
    print(bom)
    
    # Get product list
    print(f"\nProduct List:")
    products = get_product_list()
    print(products)
    
    print("\n✅ Model test completed successfully!")
