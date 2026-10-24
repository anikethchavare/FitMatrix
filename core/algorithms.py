# FitMatrix - core/algorithms.py

# Imports
import copy
from typing import List, Tuple
from .models import Block, Process, AllocationResult, AllocationStepLog

# Palette for Allocated Processes
PROCESS_PALETTE = [
    "#3B82F6",  # Blue
    "#10B981",  # Emerald
    "#8B5CF6",  # Violet
    "#F59E0B",  # Amber
    "#EC4899",  # Pink
    "#06B6D4",  # Cyan
    "#F97316",  # Orange
    "#6366F1",  # Indigo
]

# Function 1: _assign_process_colors (Internal)
def _assign_process_colors(processes: List[Process]) -> None:
    """ Assign consistent, aesthetically distinct hex colors to processes. """
    
    for i, process in enumerate(processes):
        process.color = PROCESS_PALETTE[i % len(PROCESS_PALETTE)]

# Function 2: _initialize_blocks_with_addresses (Internal)
def _initialize_blocks_with_addresses(blocks: List[Block]) -> List[Block]:
    """ Calculate and assign base and limit physical memory addresses. """
    
    cloned_blocks = copy.deepcopy(blocks)
    current_address = 0
    
    for block in cloned_blocks:
        block.base_address = current_address
        current_address += block.capacity
        block.allocated_process_id = None
        block.allocated_size = 0
        block.process_color = None
        
    return cloned_blocks

# Function 3: _calculate_summary_metrics (Internal)
def _calculate_summary_metrics(
        algorithm_name: str,
        blocks: List[Block],
        processes: List[Process],
        trace_logs: List[AllocationStepLog]
) -> AllocationResult:
    """ Compute final metrics including utilization and internal/external fragmentation. """
    
    total_memory = sum(b.capacity for b in blocks)
    total_allocated_size = sum(b.allocated_size for b in blocks)
    total_internal_frag = sum(b.internal_fragmentation for b in blocks)

    allocated_count = sum(1 for p in processes if p.allocated_block_id is not None)
    unallocated_count = len(processes) - allocated_count
    
    total_free_space = sum(b.free_space for b in blocks)
    total_external_frag = total_free_space if unallocated_count > 0 else 0

    utilization = round((total_allocated_size / total_memory * 100), 2) if total_memory > 0 else 0.0

    return AllocationResult(
        algorithm_name=algorithm_name,
        blocks=blocks,
        processes=processes,
        total_memory=total_memory,
        total_internal_fragmentation=total_internal_frag,
        total_external_fragmentation=total_external_frag,
        allocated_count=allocated_count,
        unallocated_count=unallocated_count,
        memory_utilization=utilization,
        trace_logs=trace_logs
    )

# Function 4: first_fit
def first_fit(initial_blocks: List[Block], initial_processes: List[Process]) -> AllocationResult:
    """
    Allocates the first partition that is large enough.
    Stops searching immediately once a fitting partition is encountered.
    """
    
    blocks = _initialize_blocks_with_addresses(initial_blocks)
    processes = copy.deepcopy(initial_processes)
    _assign_process_colors(processes)

    trace_logs: List[AllocationStepLog] = []
    step_counter = 1

    for process in processes:
        allocated = False
        
        for block in blocks:
            if block.is_allocated:
                trace_logs.append(AllocationStepLog(
                    step_num=step_counter,
                    process_id=process.pid,
                    process_size=process.size,
                    inspected_block_id=block.bid,
                    block_capacity=block.capacity,
                    decision="SKIPPED_OCCUPIED",
                    message=f"Block {block.bid} (Cap: {block.capacity} KB) is occupied by P{block.allocated_process_id}. Skipping."
                ))
                
                step_counter += 1
                continue

            if block.capacity >= process.size:
                block.allocated_process_id = process.pid
                block.allocated_size = process.size
                block.process_color = process.color
                process.allocated_block_id = block.bid
                allocated = True

                trace_logs.append(AllocationStepLog(
                    step_num=step_counter,
                    process_id=process.pid,
                    process_size=process.size,
                    inspected_block_id=block.bid,
                    block_capacity=block.capacity,
                    decision="ALLOCATED",
                    message=f"Found first suitable block! Allocated P{process.pid} ({process.size} KB) into Block {block.bid} ({block.capacity} KB). Internal Frag: {block.internal_fragmentation} KB."
                ))
                
                step_counter += 1
                break
            else:
                trace_logs.append(AllocationStepLog(
                    step_num=step_counter,
                    process_id=process.pid,
                    process_size=process.size,
                    inspected_block_id=block.bid,
                    block_capacity=block.capacity,
                    decision="SKIPPED_TOO_SMALL",
                    message=f"Block {block.bid} (Cap: {block.capacity} KB) is smaller than P{process.pid} ({process.size} KB). Skipping."
                ))
                
                step_counter += 1

        if not allocated:
            trace_logs.append(AllocationStepLog(
                step_num=step_counter,
                process_id=process.pid,
                process_size=process.size,
                inspected_block_id=-1,
                block_capacity=0,
                decision="UNALLOCATED",
                message=f"Allocation Failed: No contiguous partition found large enough for P{process.pid} ({process.size} KB)."
            ))
            
            step_counter += 1

    return _calculate_summary_metrics("First-Fit", blocks, processes, trace_logs)

# Function 5: best_fit
def best_fit(initial_blocks: List[Block], initial_processes: List[Process]) -> AllocationResult:
    """
    Scans all partitions and allocates the smallest available partition 
    that is large enough (producing minimum internal fragmentation).
    """
    
    blocks = _initialize_blocks_with_addresses(initial_blocks)
    processes = copy.deepcopy(initial_processes)
    _assign_process_colors(processes)

    trace_logs: List[AllocationStepLog] = []
    step_counter = 1

    for process in processes:
        best_block_idx = -1
        min_residual = float('inf')

        for idx, block in enumerate(blocks):
            if block.is_allocated:
                trace_logs.append(AllocationStepLog(
                    step_num=step_counter,
                    process_id=process.pid,
                    process_size=process.size,
                    inspected_block_id=block.bid,
                    block_capacity=block.capacity,
                    decision="SKIPPED_OCCUPIED",
                    message=f"Block {block.bid} is already occupied by P{block.allocated_process_id}. Skipping."
                ))
                
                step_counter += 1
                continue

            if block.capacity >= process.size:
                residual = block.capacity - process.size
                
                if residual < min_residual:
                    min_residual = residual
                    best_block_idx = idx
                    trace_logs.append(AllocationStepLog(
                        step_num=step_counter,
                        process_id=process.pid,
                        process_size=process.size,
                        inspected_block_id=block.bid,
                        block_capacity=block.capacity,
                        decision="CANDIDATE_FOUND",
                        message=f"Block {block.bid} fits P{process.pid} with current lowest residual ({residual} KB). Setting as current best candidate."
                    ))
                else:
                    trace_logs.append(AllocationStepLog(
                        step_num=step_counter,
                        process_id=process.pid,
                        process_size=process.size,
                        inspected_block_id=block.bid,
                        block_capacity=block.capacity,
                        decision="SKIPPED_SUBOPTIMAL",
                        message=f"Block {block.bid} fits ({residual} KB residual), but is larger than current best ({min_residual} KB residual)."
                    ))
                    
                step_counter += 1
            else:
                trace_logs.append(AllocationStepLog(
                    step_num=step_counter,
                    process_id=process.pid,
                    process_size=process.size,
                    inspected_block_id=block.bid,
                    block_capacity=block.capacity,
                    decision="SKIPPED_TOO_SMALL",
                    message=f"Block {block.bid} ({block.capacity} KB) is smaller than P{process.pid} ({process.size} KB). Skipping."
                ))
                
                step_counter += 1

        if best_block_idx != -1:
            chosen = blocks[best_block_idx]
            chosen.allocated_process_id = process.pid
            chosen.allocated_size = process.size
            chosen.process_color = process.color
            process.allocated_block_id = chosen.bid

            trace_logs.append(AllocationStepLog(
                step_num=step_counter,
                process_id=process.pid,
                process_size=process.size,
                inspected_block_id=chosen.bid,
                block_capacity=chosen.capacity,
                decision="ALLOCATED",
                message=f"Best fit confirmed! P{process.pid} allocated to Block {chosen.bid}. Internal Frag: {chosen.internal_fragmentation} KB."
            ))
            
            step_counter += 1
        else:
            trace_logs.append(AllocationStepLog(
                step_num=step_counter,
                process_id=process.pid,
                process_size=process.size,
                inspected_block_id=-1,
                block_capacity=0,
                decision="UNALLOCATED",
                message=f"Allocation Failed: No partition can fit P{process.pid} ({process.size} KB)."
            ))
            
            step_counter += 1

    return _calculate_summary_metrics("Best-Fit", blocks, processes, trace_logs)

# Function 6: worst_fit
def worst_fit(initial_blocks: List[Block], initial_processes: List[Process]) -> AllocationResult:
    """
    Scans all partitions and allocates the largest available partition,
    theorizing that the remaining hole will be large enough to be useful.
    """
    
    blocks = _initialize_blocks_with_addresses(initial_blocks)
    processes = copy.deepcopy(initial_processes)
    _assign_process_colors(processes)

    trace_logs: List[AllocationStepLog] = []
    step_counter = 1

    for process in processes:
        worst_block_idx = -1
        max_residual = -1

        for idx, block in enumerate(blocks):
            if block.is_allocated:
                trace_logs.append(AllocationStepLog(
                    step_num=step_counter,
                    process_id=process.pid,
                    process_size=process.size,
                    inspected_block_id=block.bid,
                    block_capacity=block.capacity,
                    decision="SKIPPED_OCCUPIED",
                    message=f"Block {block.bid} is already occupied by P{block.allocated_process_id}. Skipping."
                ))
                
                step_counter += 1
                continue

            if block.capacity >= process.size:
                residual = block.capacity - process.size
                
                if residual > max_residual:
                    max_residual = residual
                    worst_block_idx = idx
                    trace_logs.append(AllocationStepLog(
                        step_num=step_counter,
                        process_id=process.pid,
                        process_size=process.size,
                        inspected_block_id=block.bid,
                        block_capacity=block.capacity,
                        decision="CANDIDATE_FOUND",
                        message=f"Block {block.bid} leaves largest residual hole so far ({residual} KB). Setting as current worst candidate."
                    ))
                else:
                    trace_logs.append(AllocationStepLog(
                        step_num=step_counter,
                        process_id=process.pid,
                        process_size=process.size,
                        inspected_block_id=block.bid,
                        block_capacity=block.capacity,
                        decision="SKIPPED_SUBOPTIMAL",
                        message=f"Block {block.bid} fits ({residual} KB residual), but leaves smaller hole than Block {blocks[worst_block_idx].bid} ({max_residual} KB)."
                    ))
                    
                step_counter += 1
            else:
                trace_logs.append(AllocationStepLog(
                    step_num=step_counter,
                    process_id=process.pid,
                    process_size=process.size,
                    inspected_block_id=block.bid,
                    block_capacity=block.capacity,
                    decision="SKIPPED_TOO_SMALL",
                    message=f"Block {block.bid} ({block.capacity} KB) is smaller than P{process.pid} ({process.size} KB). Skipping."
                ))
                
                step_counter += 1

        if worst_block_idx != -1:
            chosen = blocks[worst_block_idx]
            chosen.allocated_process_id = process.pid
            chosen.allocated_size = process.size
            chosen.process_color = process.color
            process.allocated_block_id = chosen.bid

            trace_logs.append(AllocationStepLog(
                step_num=step_counter,
                process_id=process.pid,
                process_size=process.size,
                inspected_block_id=chosen.bid,
                block_capacity=chosen.capacity,
                decision="ALLOCATED",
                message=f"Worst fit confirmed! P{process.pid} allocated to Block {chosen.bid}. Residual hole remaining: {chosen.internal_fragmentation} KB."
            ))
            
            step_counter += 1
        else:
            trace_logs.append(AllocationStepLog(
                step_num=step_counter,
                process_id=process.pid,
                process_size=process.size,
                inspected_block_id=-1,
                block_capacity=0,
                decision="UNALLOCATED",
                message=f"Allocation Failed: No partition can fit P{process.pid} ({process.size} KB)."
            ))
            
            step_counter += 1

    return _calculate_summary_metrics("Worst-Fit", blocks, processes, trace_logs)