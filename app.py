# FitMatrix - app.py

# Imports
import pandas as pd
import streamlit as st

from core.models import Block, Process
from core.algorithms import first_fit, best_fit, worst_fit
from components.visualizer import render_memory_strip
from components.metrics import get_process_status_table, get_comparison_summary

# Configure Page Layout
st.set_page_config(
    page_title="FitMatrix - Contiguous Memory Allocation Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("FitMatrix: Contiguous Memory Allocation Simulator")
st.caption("Visualizing and comparing First-Fit, Best-Fit, and Worst-Fit dynamic partition allocation strategies.")

# Sidebar Controls
st.sidebar.header("Configuration Panel")

view_mode = st.sidebar.radio(
    "Select View Mode",
    ["Compare All", "First-Fit", "Best-Fit", "Worst-Fit"]
)

# Standard Textbook Preset Values
default_blocks = "100, 500, 200, 300, 600"
default_processes = "212, 417, 112, 426"

st.sidebar.subheader("Partition & Request Settings")
block_input = st.sidebar.text_input("Memory Block Sizes (KB, comma-separated)", default_blocks)
proc_input = st.sidebar.text_input("Process Sizes (KB, comma-separated)", default_processes)

# Input Parsing & Validation
try:
    block_sizes = [int(x.strip()) for x in block_input.split(",") if x.strip()]
    proc_sizes = [int(x.strip()) for x in proc_input.split(",") if x.strip()]

    if not block_sizes or not proc_sizes:
        st.warning("Please provide at least one memory block and one process size.")
        st.stop()
except ValueError:
    st.error("Invalid format: Please enter only integers separated by commas.")
    st.stop()

# Build the Block and Process Instances
blocks_data = [Block(bid=i + 1, capacity=size) for i, size in enumerate(block_sizes)]
procs_data = [Process(pid=i + 1, size=size) for i, size in enumerate(proc_sizes)]

# Run All Algorithms
results_map = {
    "First-Fit": first_fit(blocks_data, procs_data),
    "Best-Fit": best_fit(blocks_data, procs_data),
    "Worst-Fit": worst_fit(blocks_data, procs_data)
}

# View: Compare All
if view_mode == "Compare All":
    st.subheader("Performance Comparison Matrix")
    comparison_df = get_comparison_summary(list(results_map.values()))
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    st.divider()

    col1, col2, col3 = st.columns(3)
    
    algo_columns = [
        ("First-Fit", results_map["First-Fit"], col1),
        ("Best-Fit", results_map["Best-Fit"], col2),
        ("Worst-Fit", results_map["Worst-Fit"], col3)
    ]

    for name, res, col in algo_columns:
        with col:
            st.markdown(f"### {name}")
            st.plotly_chart(render_memory_strip(res), use_container_width=True)
            st.dataframe(get_process_status_table(res), use_container_width=True, hide_index=True)

# View: Individual Algorithm
else:
    active_res = results_map[view_mode]

    # Quick Metric Indicators
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Processes", len(procs_data))
    m2.metric("Allocated Processes", f"{active_res.allocated_count} / {len(procs_data)}")
    m3.metric("Internal Fragmentation", f"{active_res.total_internal_fragmentation} KB")
    m4.metric("External Fragmentation", f"{active_res.total_external_fragmentation} KB")
    m5.metric("Memory Utilization", f"{active_res.memory_utilization}%")

    st.subheader("Physical Partition Map")
    st.plotly_chart(render_memory_strip(active_res), use_container_width=True)

    st.subheader("Process Allocation Status")
    st.dataframe(get_process_status_table(active_res), use_container_width=True, hide_index=True)