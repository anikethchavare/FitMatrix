# FitMatrix - components/metrics.py

# Imports
import pandas as pd
from typing import List
from core.models import AllocationResult

# Function 1: get_process_status_table
def get_process_status_table(result: AllocationResult) -> pd.DataFrame:
    records = []
    block_map = {b.bid: b for b in result.blocks}

    for p in result.processes:
        if p.allocated_block_id is not None:
            blk = block_map[p.allocated_block_id]
            status = "Allocated"
            block_info = f"Block {blk.bid} ({blk.capacity} KB)"
            frag = f"{blk.internal_fragmentation} KB"
        else:
            status = "Not Allocated"
            block_info = "None"
            frag = "N/A"

        records.append({
            "Process ID": f"P{p.pid}",
            "Required Size (KB)": p.size,
            "Status": status,
            "Target Block": block_info,
            "Internal Fragmentation": frag
        })

    return pd.DataFrame(records)

# Function 2: get_comparison_summary
def get_comparison_summary(results: List[AllocationResult]) -> pd.DataFrame:
    records = []
    
    for r in results:
        records.append({
            "Algorithm": r.algorithm_name,
            "Processes Allocated": f"{r.allocated_count} / {len(r.processes)}",
            "Processes Unallocated": r.unallocated_count,
            "Total Internal Frag (KB)": r.total_internal_fragmentation,
            "Total External Frag (KB)": r.total_external_fragmentation,
            "Memory Utilization (%)": f"{r.memory_utilization}%"
        })
        
    return pd.DataFrame(records)