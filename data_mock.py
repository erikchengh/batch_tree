import pandas as pd
from datetime import datetime, timedelta

def generate_batch_data():
    """Generate realistic pharmaceutical batch data with genealogy"""
    
    # Raw Material Batches
    raw_materials = [
        {"batch_id": "RM-API-001", "material": "Active API", "lot": "LOT-API-2024-01", 
         "quantity": 500.0, "unit": "kg", "supplier": "PharmaChem Inc.", 
         "received_date": "2024-01-15", "expiry": "2026-01-15", "quality": "Released"},
        {"batch_id": "RM-EXC-001", "material": "Microcrystalline Cellulose", "lot": "LOT-EXC-2024-02",
         "quantity": 1000.0, "unit": "kg", "supplier": "FMC BioPolymer", 
         "received_date": "2024-01-20", "expiry": "2025-07-20", "quality": "Released"},
        {"batch_id": "RM-LUB-001", "material": "Magnesium Stearate", "lot": "LOT-LUB-2024-01",
         "quantity": 50.0, "unit": "kg", "supplier": "Peter Greven", 
         "received_date": "2024-01-10", "expiry": "2025-10-10", "quality": "Released"},
        {"batch_id": "RM-DIS-001", "material": "Purified Water", "lot": "LOT-DIS-2024-01",
         "quantity": 2000.0, "unit": "L", "supplier": "Internal", 
         "received_date": "2024-01-05", "expiry": "2024-02-05", "quality": "Released"},
    ]
    
    # Intermediate Batches
    intermediate_batches = [
        {"batch_id": "INT-BLEND-001", "material": "Tablet Blend", "product": "Tablet_A",
         "quantity": 1450.0, "unit": "kg", "manufacturing_date": "2024-02-01",
         "status": "Completed", "quality": "Released",
         "consumes": [
             {"batch_id": "RM-API-001", "quantity": 500.0, "unit": "kg"},
             {"batch_id": "RM-EXC-001", "quantity": 950.0, "unit": "kg"}
         ]},
        {"batch_id": "INT-COAT-001", "material": "Coating Solution", "product": "Tablet_A",
         "quantity": 200.0, "unit": "L", "manufacturing_date": "2024-02-02",
         "status": "Completed", "quality": "Released",
         "consumes": [
             {"batch_id": "RM-DIS-001", "quantity": 180.0, "unit": "L"}
         ]},
    ]
    
    # Finished Product Batches
    finished_products = [
        {"batch_id": "FP-TAB-001", "material": "Tablet_A 500mg", "product": "Tablet_A",
         "quantity": 1000000, "unit": "tablets", "manufacturing_date": "2024-02-05",
         "expiry": "2026-02-05", "status": "Released", "quality": "Approved",
         "consumes": [
             {"batch_id": "INT-BLEND-001", "quantity": 1450.0, "unit": "kg"},
             {"batch_id": "RM-LUB-001", "quantity": 5.0, "unit": "kg"},
             {"batch_id": "INT-COAT-001", "quantity": 150.0, "unit": "L"}
         ]},
        {"batch_id": "FP-TAB-002", "material": "Tablet_A 500mg", "product": "Tablet_A",
         "quantity": 1500000, "unit": "tablets", "manufacturing_date": "2024-02-10",
         "expiry": "2026-02-10", "status": "Released", "quality": "Approved",
         "consumes": [
             {"batch_id": "RM-API-001", "quantity": 750.0, "unit": "kg"},
             {"batch_id": "RM-EXC-001", "quantity": 1425.0, "unit": "kg"},
             {"batch_id": "RM-LUB-001", "quantity": 7.5, "unit": "kg"}
         ]},
    ]
    
    # Batch Genealogy Relationships
    genealogy = []
    
    # Add consumption relationships
    for batch in intermediate_batches + finished_products:
        if "consumes" in batch:
            for consumed in batch["consumes"]:
                genealogy.append({
                    "parent_batch": consumed["batch_id"],
                    "child_batch": batch["batch_id"],
                    "relationship": "consumed_by",
                    "quantity": consumed["quantity"],
                    "unit": consumed["unit"]
                })
    
    # Add manufacturing sequence relationships
    genealogy.extend([
        {"parent_batch": "INT-BLEND-001", "child_batch": "FP-TAB-001", "relationship": "precedes", "quantity": None, "unit": None},
        {"parent_batch": "INT-COAT-001", "child_batch": "FP-TAB-001", "relationship": "coated_with", "quantity": None, "unit": None},
    ])
    
    # All batches combined
    all_batches = raw_materials + intermediate_batches + finished_products
    
    return {
        "batches": pd.DataFrame(all_batches),
        "genealogy": pd.DataFrame(genealogy),
        "raw_materials": pd.DataFrame(raw_materials),
        "intermediate": pd.DataFrame(intermediate_batches),
        "finished": pd.DataFrame(finished_products)
    }

def get_batch_details(batch_id):
    """Get detailed information about a specific batch"""
    data = generate_batch_data()
    
    # Find the batch
    batch_row = data["batches"][data["batches"]["batch_id"] == batch_id]
    if batch_row.empty:
        return None
    
    batch_info = batch_row.iloc[0].to_dict()
    
    # Find what this batch consumes
    consumes = data["genealogy"][data["genealogy"]["parent_batch"] == batch_id]
    
    # Find what batches consume this batch
    consumed_by = data["genealogy"][data["genealogy"]["child_batch"] == batch_id]
    
    return {
        "batch_info": batch_info,
        "consumes": consumes.to_dict('records'),  # What this batch consumes
        "consumed_by": consumed_by.to_dict('records'),  # What consumes this batch
        "batch_type": (
            "Raw Material" if batch_id.startswith("RM-") else
            "Intermediate" if batch_id.startswith("INT-") else
            "Finished Product"
        )
    }
