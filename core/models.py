# FitMatrix - core/models.py

# Imports
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

# Class 1: Process (Data Class)
@dataclass
class Process:
    """ Represents a process requesting contiguous memory. """
    
    pid: int
    size: int
    allocated_block_id: Optional[int] = None
    color: Optional[str] = None

# Class 2: AllocationStepLog (Data Class)
@dataclass
class AllocationStepLog:
    """ Captures each step during the allocation scan for step-by-step playback. """
    
    step_num: int
    process_id: int
    process_size: int
    inspected_block_id: int
    block_capacity: int
    decision: str 
    message: str

# Class 3: Block (Data Class)
@dataclass
class Block:
    """ Represents a physical memory block or partition. """
    
    bid: int
    capacity: int
    base_address: int = 0
    allocated_process_id: Optional[int] = None
    allocated_size: int = 0
    process_color: Optional[str] = None
    
    # Method 1: limit_address (Getter)
    @property
    def limit_address(self) -> int:
        return self.base_address + self.capacity
    
    # Method 2: is_allocated (Getter)
    @property
    def is_allocated(self) -> bool:
        return self.allocated_process_id is not None

    # Method 3: internal_fragmentation (Getter)
    @property
    def internal_fragmentation(self) -> int:
        if self.is_allocated:
            return max(0, self.capacity - self.allocated_size)
        
        return 0
    
    # Method 4: free_space (Getter)
    @property
    def free_space(self) -> int:
        if self.is_allocated:
            return 0
        
        return self.capacity
    
    # Method 5: utilization_percentage (Getter)
    @property
    def utilization_percentage(self) -> float:
        if not self.is_allocated or self.capacity == 0:
            return 0.0
        
        return round((self.allocated_size / self.capacity) * 100, 2)

# Class 4: AllocationResult (Data Class)
@dataclass
class AllocationResult:
    """ Aggregates final outcomes, metrics, and trace logs for an algorithm run. """
    
    algorithm_name: str
    blocks: List[Block]
    processes: List[Process]
    total_memory: int
    total_internal_fragmentation: int
    total_external_fragmentation: int
    allocated_count: int
    unallocated_count: int
    memory_utilization: float
    trace_logs: List[AllocationStepLog] = field(default_factory=list)