import streamlit as st
import pandas as pd
from model import build_batch_genealogy_graph, get_bom_list, get_product_list, analyze_graph
from graph_view import render_genealogy_graph

# Page configuration
st.set_page_config(
    page_title="Pharma Batch Genealogy System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1a3c6e;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #5d7fa3;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton button {
        background-color: #1e88e5;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏭 Pharmaceutical Batch Genealogy System</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional Batch Tree Visualization for Pharma Manufacturing</p>', unsafe_allow_html=True)

# Initialize session state
if 'graph_loaded' not in st.session_state:
    st.session_state.graph_loaded = False
if 'G' not in st.session_state:
    st.session_state.G = None
if 'data' not in st.session_state:
    st.session_state.data = None

# Main container
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Load & Visualize Batch Tree", use_container_width=True, type="primary"):
            with st.spinner("🌱 Building pharmaceutical batch tree..."):
                try:
                    G, data = build_batch_genealogy_graph()
                    st.session_state.G = G
                    st.session_state.data = data
                    st.session_state.graph_loaded = True
                    st.success("✅ Batch tree loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.graph_loaded = False

# Main app logic
if st.session_state.graph_loaded and st.session_state.G is not None:
    G = st.session_state.G
    data = st.session_state.data
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Tree Statistics")
        
        # Show graph stats
        stats = analyze_graph(G)
        st.metric("Total Batches", stats["total_nodes"])
        st.metric("Total Connections", stats["total_edges"])
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Raw Materials", stats["raw_materials"])
        with col_b:
            st.metric("Finished Products", stats["finished_products"])
        
        st.divider()
        
        st.markdown("### 🔍 Batch Selection")
        
        # Get nodes that are finished products
        finished_products = [n for n in G.nodes() if G.nodes[n].get("type") == "Finished Product"]
        
        if finished_products:
            selected_batch = st.selectbox(
                "Select Target Product",
                options=finished_products,
                index=0,
                help="Select a finished product to view its material genealogy"
            )
        else:
            selected_batch = None
            st.warning("No finished product batches found")
        
        st.divider()
        
        st.markdown("### 🎨 Tree Options")
        tree_style = st.radio(
            "Tree Display Style",
            ["standard", "compact", "detailed"],
            index=0,
            help="Choose how to display the tree structure"
        )
        
        st.divider()
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Refresh Tree", use_container_width=True):
            st.rerun()
        
        if st.button("📥 Export Tree Data", use_container_width=True):
            # Create download data
            import json
            tree_data = {
                "nodes": list(G.nodes(data=True)),
                "edges": list(G.edges(data=True))
            }
            st.download_button(
                label="Download JSON",
                data=json.dumps(tree_data, indent=2),
                file_name="batch_tree.json",
                mime="application/json"
            )
    
    # Main content area
    tab1, tab2 = st.tabs(["🌳 Batch Tree Visualization", "📋 Batch Details"])
    
    with tab1:
        st.markdown("### 📈 Material Genealogy Tree")
        
        if selected_batch:
            # Show selected batch info
            node_data = G.nodes[selected_batch]
            st.info(f"""
            **Selected Product:** `{selected_batch}`  
            **Material:** {node_data.get('material', 'Unknown')}  
            **Quantity:** {node_data.get('quantity', 'N/A')} {node_data.get('unit', '')}
            """)
            
            # Render the graph
            render_genealogy_graph(
                G, 
                target_batch_id=selected_batch,
                trace_mode="none"
            )
        else:
            st.info("👈 Select a batch from the sidebar to visualize its genealogy")
    
    with tab2:
        if selected_batch:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 📄 Batch Information")
                node_data = G.nodes[selected_batch]
                
                info_card = f"""
                <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #1e88e5; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="display: flex; align-items: center; margin-bottom: 15px;">
                        <span style="font-size: 24px; margin-right: 10px;">💊</span>
                        <div>
                            <div style="font-weight: 700; color: #1a3c6e; font-size: 16px;">{selected_batch}</div>
                            <div style="color: #5d7fa3; font-size: 14px;">{node_data.get('material', 'Unknown Material')}</div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 15px;">
                        <div style="background: #f8fafc; padding: 10px; border-radius: 6px;">
                            <div style="color: #64748b; font-size: 12px;">Type</div>
                            <div style="color: #1e293b; font-weight: 600; font-size: 14px;">{node_data.get('type', 'N/A')}</div>
                        </div>
                        
                        <div style="background: #f8fafc; padding: 10px; border-radius: 6px;">
                            <div style="color: #64748b; font-size: 12px;">Status</div>
                            <div style="color: #1e293b; font-weight: 600; font-size: 14px;">{node_data.get('status', 'N/A')}</div>
                        </div>
                        
                        <div style="background: #f8fafc; padding: 10px; border-radius: 6px;">
                            <div style="color: #64748b; font-size: 12px;">Quantity</div>
                            <div style="color: #1e293b; font-weight: 600; font-size: 14px;">{node_data.get('quantity', 'N/A')} {node_data.get('unit', '')}</div>
                        </div>
                        
                        <div style="background: #f8fafc; padding: 10px; border-radius: 6px;">
                            <div style="color: #64748b; font-size: 12px;">Quality</div>
                            <div style="color: #1e293b; font-weight: 600; font-size: 14px;">{node_data.get('quality', 'N/A')}</div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(info_card, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 📦 Bill of Materials")
                bom_df = get_bom_list(selected_batch)
                if not bom_df.empty:
                    # Style the DataFrame
                    st.dataframe(
                        bom_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "material": "Material",
                            "batch_id": "Batch ID",
                            "quantity": "Quantity",
                            "unit": "Unit",
                            "type": "Type",
                            "status": "Status"
                        }
                    )
                    
                    # Calculate total materials
                    total_qty = bom_df['quantity'].sum() if 'quantity' in bom_df.columns else 0
                    st.metric("Total Raw Materials Used", f"{len(bom_df)} items", f"{total_qty:.1f} total units")
                else:
                    st.info("No BOM data available for this batch")
            
            # Connected batches section
            st.markdown("#### 🔗 Connected Batches")
            col1, col2 = st.columns(2)
            
            with col1:
                # Predecessors (what went into this batch)
                predecessors = list(G.predecessors(selected_batch))
                if predecessors:
                    st.markdown("**Input Materials:**")
                    for pred in predecessors[:5]:  # Show first 5
                        pred_data = G.nodes[pred]
                        st.markdown(f"- `{pred}`: {pred_data.get('material', 'Unknown')}")
                    if len(predecessors) > 5:
                        st.caption(f"... and {len(predecessors) - 5} more")
                else:
                    st.info("No direct input materials")
            
            with col2:
                # Successors (what this batch produced)
                successors = list(G.successors(selected_batch))
                if successors:
                    st.markdown("**Output Products:**")
                    for succ in successors[:5]:  # Show first 5
                        succ_data = G.nodes[succ]
                        st.markdown(f"- `{succ}`: {succ_data.get('material', 'Unknown')}")
                    if len(successors) > 5:
                        st.caption(f"... and {len(successors) - 5} more")
                else:
                    st.info("No direct output products")
        
        else:
            st.info("👈 Select a batch from the sidebar to view details")
    
    # Footer information
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.expander("📋 All Batches"):
            batch_list = []
            for node in G.nodes():
                node_data = G.nodes[node]
                batch_list.append({
                    "Batch ID": node,
                    "Type": node_data.get('type', 'Unknown'),
                    "Material": node_data.get('material', 'Unknown'),
                    "Quantity": node_data.get('quantity', ''),
                    "Status": node_data.get('status', '')
                })
            st.dataframe(pd.DataFrame(batch_list), use_container_width=True)
    
    with col2:
        with st.expander("🔄 All Connections"):
            edge_list = []
            for u, v, data in G.edges(data=True):
                edge_list.append({
                    "From": u,
                    "To": v,
                    "Quantity": data.get('quantity', ''),
                    "Unit": data.get('unit', '')
                })
            st.dataframe(pd.DataFrame(edge_list), use_container_width=True)
    
    with col3:
        with st.expander("📊 Tree Analysis"):
            st.json(stats)
            
            # Show degree centrality
            if G.number_of_nodes() > 0:
                in_degrees = dict(G.in_degree())
                out_degrees = dict(G.out_degree())
                
                # Find most connected nodes
                if in_degrees:
                    most_inputs = max(in_degrees.items(), key=lambda x: x[1])
                    st.metric("Most Inputs", f"{most_inputs[0]}", f"{most_inputs[1]} connections")
                
                if out_degrees:
                    most_outputs = max(out_degrees.items(), key=lambda x: x[1])
                    st.metric("Most Outputs", f"{most_outputs[0]}", f"{most_outputs[1]} connections")

else:
    # Show welcome/loading screen
    with st.container():
        st.markdown("""
        ## 🌳 Welcome to Pharma Batch Tree
        
        This system visualizes pharmaceutical batch genealogy as a clean, professional tree structure.
        
        ### 🎯 Features:
        - **🌳 Tree Visualization**: See raw materials → finished products as a proper tree
        - **🧪 Pharma Icons**: Professional pharmaceutical icons (API 🧪, Excipients 📦, Tablets 💊)
        - **🔍 Interactive**: Hover for details, drag to rearrange, zoom in/out
        - **📊 Professional**: GMP-compliant styling with pharmaceutical color scheme
        
        ### 🚀 How to use:
        1. Click **"Load & Visualize Batch Tree"** above
        2. Select a finished product from the sidebar
        3. Explore the tree visualization in the main panel
        4. View batch details and Bill of Materials in the details tab
        
        ### 🏭 Sample Data Includes:
        - **Raw Materials**: API batches, excipients, solvents
        - **Finished Products**: Tablets, capsules with batch information
        - **Direct Connections**: Clear material flow without intermediate clutter
        
        Click the button above to load the demo and get started!
        """)
        
        # Show sample tree structure
        with st.expander("🌲 Sample Tree Structure"):
            st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/docs/images/tree_structure.png", 
                    caption="Example of tree visualization", use_column_width=True)
