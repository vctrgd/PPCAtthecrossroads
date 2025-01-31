from dataclasses import dataclass
import multiprocessing
currentId = multiprocessing.Value('i',0, lock=multiprocessing.Lock())

@dataclass
class Vehicle:
    """Represents a vehicle moving through the intersection."""
    vehicle_id: int
    isPriority: bool  # "normal" or "priority"
    source: str
    destination: str
    isWaiting: bool 