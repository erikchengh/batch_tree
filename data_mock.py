def load_mock_batch(batch_id):
    """Real batch genealogy data with material consumption/production relationships"""
    
    # Mock database of batches and their genealogy
    batch_db = {
        "B001": {
            "batch": {
                "id": "B001",
                "product": "Tablet_A",
                "status": "Completed",
                "manufacturing_date": "2026-01-07",
                "quantity": "100,000 tablets",
                "lot_number": "LOT20260107A"
            },
            # Material CONSUMPTION (Bill of Materials)
            "consumes": [
                {
                    "material_batch": "API-2025-12-15",
                    "material_name": "Active Pharmaceutical Ingredient",
                    "quantity": "500 kg",
                    "specification": "API-001-SPEC",
                    "supplier": "Supplier_A",
                    "type": "raw"
                },
                {
                    "material_batch": "EXC-2026-01-02",
                    "material_name": "Excipient Blend",
                    "quantity": "950 kg",
                    "specification": "EXC-002-SPEC", 
                    "supplier": "Supplier_B",
                    "type": "intermediate"
                },
                {
                    "material_batch": "COA-2025-11-30",
                    "material_name": "Coating Solution",
                    "quantity": "200 L",
                    "specification": "COA-003-SPEC",
                    "supplier": "Supplier_C",
                    "type": "raw"
                }
            ],
            # Material PRODUCTION (what this batch produces)
            "produces": [
                {
                    "product_batch": "FIN-2026-01-10",
                    "product_name": "Finished Tablets",
                    "quantity": "100,000 bottles",
                    "specification": "FIN-001-SPEC"
                }
            ],
            # Parent batches (what batches were used to make this)
            "parents": ["API-2025-12-15", "EXC-2026-01-02"],
            # Child batches (what batches were produced from this)
            "children": ["FIN-2026-01-10"]
        },
        "API-2025-12-15": {
            "batch": {
                "id": "API-2025-12-15",
                "product": "Active Pharmaceutical Ingredient",
                "status": "Completed",
                "manufacturing_date": "2025-12-15",
                "quantity": "1000 kg",
                "lot_number": "LOT20251215API"
            },
            "consumes": [
                {
                    "material_batch": "RAW-001",
                    "material_name": "Chemical Precursor A",
                    "quantity": "1200 kg",
                    "type": "raw"
                },
                {
                    "material_batch": "RAW-002", 
                    "material_name": "Solvent B",
                    "quantity": "5000 L",
                    "type": "raw"
                }
            ],
            "produces": [
                {
                    "product_batch": "API-2025-12-15",
                    "product_name": "Active Pharmaceutical Ingredient",
                    "quantity": "1000 kg"
                }
            ],
            "parents": ["RAW-001", "RAW-002"],
            "children": ["B001", "B002"]  # Used in multiple final batches
        },
        "EXC-2026-01-02": {
            "batch": {
                "id": "EXC-2026-01-02",
                "product": "Excipient Blend",
                "status": "Completed",
                "manufacturing_date": "2026-01-02",
                "quantity": "2000 kg",
                "lot_number": "LOT20260102EXC"
            },
            "consumes": [
                {
                    "material_batch": "MCC-2025-12-20",
                    "material_name": "Microcrystalline Cellulose",
                    "quantity": "800 kg",
                    "type": "raw"
                },
                {
                    "material_batch": "LAC-2025-12-22",
                    "material_name": "Lactose Monohydrate",
                    "quantity": "700 kg", 
                    "type": "raw"
                },
                {
                    "material_batch": "MGS-2025-12-18",
                    "material_name": "Magnesium Stearate",
                    "quantity": "500 kg",
                    "type": "raw"
                }
            ],
            "produces": [
                {
                    "product_batch": "EXC-2026-01-02",
                    "product_name": "Excipient Blend",
                    "quantity": "2000 kg"
                }
            ],
            "parents": ["MCC-2025-12-20", "LAC-2025-12-22", "MGS-2025-12-18"],
            "children": ["B001", "B003"]
        },
        "FIN-2026-01-10": {
            "batch": {
                "id": "FIN-2026-01-10",
                "product": "Finished Tablets",
                "status": "Released",
                "manufacturing_date": "2026-01-10",
                "quantity": "100,000 bottles",
                "lot_number": "LOT20260110FIN"
            },
            "consumes": [
                {
                    "material_batch": "B001",
                    "material_name": "Tablet Cores",
                    "quantity": "100,000 tablets",
                    "type": "intermediate"
                },
                {
                    "material_batch": "PKG-2026-01-09",
                    "material_name": "Packaging Material",
                    "quantity": "100,000 units",
                    "type": "packaging"
                }
            ],
            "produces": [
                {
                    "product_batch": "FIN-2026-01-10",
                    "product_name": "Finished Product",
                    "quantity": "100,000 bottles",
                    "customer": "Hospital Chain XYZ",
                    "expiry_date": "2027-07-10"
                }
            ],
            "parents": ["B001", "PKG-2026-01-09"],
            "children": []  # Final product, no further children
        }
    }
    
    # Return the specific batch or all if batch_id is "ALL"
    if batch_id == "ALL":
        return list(batch_db.values())
    else:
        return batch_db.get(batch_id, batch_db["B001"])
