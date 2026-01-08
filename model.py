import networkx as nx
from data_mock import load_mock_batch
 
def build_batch_genealogy_graph(target_batch_id, depth=2):
    """
    Build a genealogy graph showing material flow
    depth: How many levels up/down to traverse (0=current only, 1=immediate parents/children, etc.)
    """
    G = nx.DiGraph()
    
    def add_batch_to_graph(batch_id, current_depth, direction="both"):
        """Recursively add batch and its relationships to graph"""
        if current_depth < 0:
            return
            
        batch_data = load_mock_batch(batch_id)
        if not batch_data:
            return
            
        # Add batch node
        batch_info = batch_data["batch"]
        G.add_node(
            batch_id,
            label=f"{batch_info['product']}\n({batch_id})",
            type="batch",
            product=batch_info["product"],
            status=batch_info["status"],
            quantity=batch_info["quantity"],
            date=batch_info.get("manufacturing_date", ""),
            lot=batch_info.get("lot_number", ""),
            level=current_depth
        )
        
        # Add CONSUMED materials (Bill of Materials - what goes IN)
        if "consumes" in batch_data and direction in ["both", "up"]:
            for material in batch_data["consumes"]:
                material_id = material["material_batch"]
                material_name = material["material_name"]
                
                # Add material node
                G.add_node(
                    material_id,
                    label=f"{material_name}\n({material_id})",
                    type="material",
                    material_type=material.get("type", "raw"),
                    quantity=material["quantity"],
                    specification=material.get("specification", ""),
                    supplier=material.get("supplier", ""),
                    level=current_depth + 1
                )
                
                # Add edge: material → batch (material is CONSUMED BY batch)
                G.add_edge(
                    material_id,
                    batch_id,
                    relationship="consumed_by",
                    quantity=material["quantity"],
                    material_type=material.get("type", "raw")
                )
                
                # Recursively add parent batches of this material
                if material_id in ["API-2025-12-15", "EXC-2026-01-02"]:  # Check if it's a batch itself
                    add_batch_to_graph(material_id, current_depth - 1, direction="up")
        
        # Add PRODUCED products (what comes OUT)
        if "produces" in batch_data and direction in ["both", "down"]:
            for product in batch_data["produces"]:
                product_id = product["product_batch"]
                if product_id != batch_id:  # Avoid self-reference
                    product_name = product["product_name"]
                    
                    # Add product node
                    G.add_node(
                        product_id,
                        label=f"{product_name}\n({product_id})",
                        type="product",
                        quantity=product["quantity"],
                        customer=product.get("customer", ""),
                        expiry=product.get("expiry_date", ""),
                        level=current_depth - 1
                    )
                    
                    # Add edge: batch → product (batch PRODUCES product)
                    G.add_edge(
                        batch_id,
                        product_id,
                        relationship="produces",
                        quantity=product["quantity"]
                    )
                    
                    # Recursively add child batches
                    add_batch_to_graph(product_id, current_depth - 1, direction="down")
    
    # Start building from target batch
    add_batch_to_graph(target_batch_id, depth, direction="both")
    
    return G
 
def get_bom_list(batch_id):
    """Get complete Bill of Materials for a batch"""
    batch_data = load_mock_batch(batch_id)
    if not batch_data:
        return []
    
    bom = []
    
    def extract_bom(batch_id, level=0):
        batch_data = load_mock_batch(batch_id)
        if not batch_data or "consumes" not in batch_data:
            return
            
        for material in batch_data["consumes"]:
            bom.append({
                "level": level,
                "batch_id": batch_id,
                "material_batch": material["material_batch"],
                "material_name": material["material_name"],
                "quantity": material["quantity"],
                "type": material.get("type", "raw"),
                "specification": material.get("specification", ""),
                "supplier": material.get("supplier", "")
            })
            
            # If material is itself a batch, get its BOM
            if material["material_batch"] in ["API-2025-12-15", "EXC-2026-01-02"]:
                extract_bom(material["material_batch"], level + 1)
    
    extract_bom(batch_id)
    return bom
 
def get_product_genealogy(batch_id, direction="down"):
    """Get all products made from this batch (downstream) or batches that made it (upstream)"""
    genealogy = []
    
    def trace_genealogy(current_id, current_direction, level=0, visited=None):
        if visited is None:
            visited = set()
            
        if current_id in visited:
            return
        visited.add(current_id)
        
        batch_data = load_mock_batch(current_id)
        if not batch_data:
            return
            
        genealogy.append({
            "level": level,
            "batch_id": current_id,
            "product": batch_data["batch"]["product"],
            "quantity": batch_data["batch"]["quantity"],
            "status": batch_data["batch"]["status"],
            "date": batch_data["batch"].get("manufacturing_date", "")
        })
        
        # Trace upstream (what made this)
        if current_direction == "up" and "parents" in batch_data:
            for parent in batch_data["parents"]:
                trace_genealogy(parent, "up", level + 1, visited)
        
        # Trace downstream (what this made)
        elif current_direction == "down" and "children" in batch_data:
            for child in batch_data["children"]:
                trace_genealogy(child, "down", level + 1, visited)
    
    trace_genealogy(batch_id, direction)
    return genealogy
